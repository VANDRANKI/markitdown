"""Utility functions for parsing and converting URI formats used by MarkItDown."""

import base64
import os
from typing import Dict, Optional, Tuple
from urllib.parse import unquote_to_bytes, urlparse
from urllib.request import url2pathname


def file_uri_to_path(file_uri: str) -> Tuple[Optional[str], str]:
    """Convert a ``file://`` URI to a local filesystem path.

    Parameters
    ----------
    file_uri:
        A URI with the ``file`` scheme, e.g. ``file:///home/user/doc.pdf`` or
        ``file://hostname/share/doc.pdf``.

    Returns
    -------
    Tuple[Optional[str], str]
        A 2-tuple of ``(netloc, absolute_path)`` where *netloc* is the host
        portion of the URI (``None`` for local files) and *absolute_path* is
        the resolved local filesystem path.

    Raises
    ------
    ValueError
        If *file_uri* does not use the ``file`` scheme.
    """
    parsed = urlparse(file_uri)
    if parsed.scheme != "file":
        raise ValueError(f"Not a file URL: {file_uri}")

    netloc: Optional[str] = parsed.netloc if parsed.netloc else None
    path: str = os.path.abspath(url2pathname(parsed.path))
    return netloc, path


def parse_data_uri(
    uri: str,
) -> Tuple[Optional[str], Dict[str, str], bytes]:
    """Parse an RFC 2397 data URI into its component parts.

    A data URI has the form::

        data:[<mediatype>][;base64],<data>

    where *<mediatype>* is a MIME type string (default ``text/plain``) and
    *<data>* is either Base64-encoded or percent-encoded content.

    Parameters
    ----------
    uri:
        The data URI string to parse.

    Returns
    -------
    Tuple[Optional[str], Dict[str, str], bytes]
        A 3-tuple of:

        * ``mime_type`` – The declared MIME type, or ``None`` if absent.
        * ``attributes`` – A dict of additional metadata parameters (e.g.
          ``{"charset": "utf-8"}``).  Boolean parameters (no ``=`` sign) are
          stored with an empty-string value.
        * ``content`` – The decoded binary payload as :class:`bytes`.

    Raises
    ------
    ValueError
        If *uri* is not a data URI, or if the URI is malformed (missing the
        ``,`` separator between the header and payload).
    """
    if not uri.startswith("data:"):
        raise ValueError("Not a data URI")

    header, _, data = uri.partition(",")
    if not _:
        raise ValueError("Malformed data URI, missing ',' separator")

    meta = header[5:]  # Strip leading 'data:'
    parts = meta.split(";")

    is_base64: bool = False
    if parts[-1] == "base64":
        parts.pop()
        is_base64 = True

    mime_type: Optional[str] = None
    if parts and parts[0]:
        mime_type = parts.pop(0)

    attributes: Dict[str, str] = {}
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            attributes[key] = value
        elif part:
            attributes[part] = ""

    content: bytes = base64.b64decode(data) if is_base64 else unquote_to_bytes(data)

    return mime_type, attributes, content
