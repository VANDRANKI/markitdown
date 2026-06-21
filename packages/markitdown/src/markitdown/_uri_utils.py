import base64
import os
from typing import Tuple, Dict
from urllib.request import url2pathname
from urllib.parse import urlparse, unquote_to_bytes


def file_uri_to_path(file_uri: str) -> Tuple[str | None, str]:
    """
    Convert a ``file://`` URI to a local filesystem path.

    Parameters
    ----------
    file_uri:
        A URI that starts with ``file://``. Both ``file:///path`` (no host)
        and ``file://host/path`` (UNC-style) forms are accepted.

    Returns
    -------
    tuple[str | None, str]
        A 2-tuple of ``(netloc, absolute_path)`` where *netloc* is the
        hostname component (``None`` when absent, e.g. plain
        ``file:///…`` URIs) and *absolute_path* is the OS-native absolute
        path resolved via :func:`os.path.abspath`.

    Raises
    ------
    ValueError
        If *file_uri* does not use the ``file`` scheme.
    """
    parsed = urlparse(file_uri)
    if parsed.scheme != "file":
        raise ValueError(f"Not a file URL: {file_uri}")

    netloc = parsed.netloc if parsed.netloc else None
    path = os.path.abspath(url2pathname(parsed.path))
    return netloc, path


def parse_data_uri(uri: str) -> Tuple[str | None, Dict[str, str], bytes]:
    """
    Parse an RFC 2397 ``data:`` URI into its constituent parts.

    The grammar handled is::

        data:[<mediatype>][;base64],<data>

    where ``<mediatype>`` is an optional MIME type optionally followed by
    semicolon-separated ``key=value`` attribute pairs (e.g. ``charset=utf-8``).
    When ``base64`` appears as the last token before the comma the payload is
    decoded from Base64; otherwise it is percent-decoded.

    Parameters
    ----------
    uri:
        The raw data URI string to parse.

    Returns
    -------
    tuple[str | None, dict[str, str], bytes]
        A 3-tuple of:

        * **mime_type** – The MIME type string (e.g. ``"image/png"``), or
          ``None`` when the URI omits it.
        * **attributes** – A dictionary of additional metadata attributes
          found in the header (e.g. ``{"charset": "utf-8"}``).  Boolean
          flags with no value are stored with an empty-string value.
        * **content** – The decoded binary payload as :class:`bytes`.

    Raises
    ------
    ValueError
        If *uri* does not start with ``data:``, or the required ``,``
        separator is missing (malformed URI).
    """
    if not uri.startswith("data:"):
        raise ValueError("Not a data URI")

    header, _, data = uri.partition(",")
    if not _:
        raise ValueError("Malformed data URI, missing ',' separator")

    meta = header[5:]  # Strip 'data:'
    parts = meta.split(";")

    is_base64 = False
    # Ends with base64?
    if parts[-1] == "base64":
        parts.pop()
        is_base64 = True

    mime_type = None  # Normally this would default to text/plain but we won't assume
    if len(parts) and len(parts[0]) > 0:
        # First part is the mime type
        mime_type = parts.pop(0)

    attributes: Dict[str, str] = {}
    for part in parts:
        # Handle key=value pairs in the middle
        if "=" in part:
            key, value = part.split("=", 1)
            attributes[key] = value
        elif len(part) > 0:
            attributes[part] = ""

    content = base64.b64decode(data) if is_base64 else unquote_to_bytes(data)

    return mime_type, attributes, content
