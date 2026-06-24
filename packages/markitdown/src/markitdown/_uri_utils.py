"""Utilities for parsing and converting URI formats used by MarkItDown."""

import base64
import os
from typing import Tuple, Dict
from urllib.request import url2pathname
from urllib.parse import urlparse, unquote_to_bytes


def file_uri_to_path(file_uri: str) -> Tuple[str | None, str]:
    """Convert a file URI to a local file path.

    Parses a ``file://`` URI and returns the network location (for UNC paths
    on Windows) and the absolute local filesystem path.

    Args:
        file_uri: A URI string starting with the ``file`` scheme.

    Returns:
        A tuple of ``(netloc, path)`` where ``netloc`` is the network location
        component (e.g. a hostname for UNC paths, or ``None`` for local paths)
        and ``path`` is the absolute local file path.

    Raises:
        ValueError: If ``file_uri`` does not use the ``file`` scheme.
    """
    parsed = urlparse(file_uri)
    if parsed.scheme != "file":
        raise ValueError(f"Not a file URL: {file_uri}")

    netloc = parsed.netloc if parsed.netloc else None
    path = os.path.abspath(url2pathname(parsed.path))
    return netloc, path


def parse_data_uri(uri: str) -> Tuple[str | None, Dict[str, str], bytes]:
    """Parse a data URI into its component parts.

    Data URIs follow the format defined in RFC 2397:
    ``data:[<mediatype>][;base64],<data>``

    where ``<mediatype>`` is an optional MIME type (e.g. ``image/png``) and
    ``<data>`` is either URL-percent-encoded text or base64-encoded binary.

    Args:
        uri: A URI string starting with ``data:``.

    Returns:
        A 3-tuple of:

        - ``mime_type`` (str | None): The MIME type declared in the header,
          or ``None`` if absent. Note that RFC 2397 defaults to
          ``text/plain;charset=US-ASCII`` when absent, but this function
          returns ``None`` rather than assuming a default.
        - ``attributes`` (Dict[str, str]): Additional ``key=value`` parameters
          from the header (e.g. ``{"charset": "utf-8"}``). Parameters that
          appear without a value are stored as ``{param: ""}``.
        - ``content`` (bytes): The decoded data payload. Base64-encoded
          payloads are decoded with `base64.b64decode`; percent-encoded
          payloads are decoded with `urllib.parse.unquote_to_bytes`.

    Raises:
        ValueError: If ``uri`` does not start with ``data:`` or is missing
            the required ``,`` separator between header and data.
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
