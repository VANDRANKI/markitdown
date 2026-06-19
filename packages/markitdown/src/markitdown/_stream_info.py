"""StreamInfo dataclass for carrying file-stream metadata between converters.

This module defines :class:`StreamInfo`, a frozen dataclass that travels
alongside a ``BinaryIO`` stream through the MarkItDown converter pipeline.
Converters inspect ``StreamInfo`` fields to decide whether they can handle
a given file and to emit richer conversion results (e.g. preserving the
original filename in the Markdown output).
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(kw_only=True, frozen=True)
class StreamInfo:
    """Immutable metadata snapshot for a file stream.

    ``StreamInfo`` is a *frozen* dataclass: instances cannot be mutated
    after creation.  Use :meth:`copy_and_update` to derive a modified copy.

    All fields default to ``None``; callers should only populate the fields
    they actually know.  Converters must never assume a field is set.

    Attributes:
        mimetype: MIME type string inferred from the HTTP ``Content-Type``
            header, file magic bytes, or the file extension.  Example:
            ``'application/pdf'``.
        extension: Lowercase file extension *with* the leading dot, e.g.
            ``'.pdf'``, ``'.docx'``.  Derived from the filename or URL path.
        charset: Character-set / encoding label when the stream carries text,
            e.g. ``'utf-8'``.  ``None`` for binary streams.
        filename: Human-readable filename without directory components.
            Sourced from the local filesystem path, the URL's last path
            segment, or an HTTP ``Content-Disposition`` header.
        local_path: Absolute path on disk when the stream was opened from the
            local filesystem.  ``None`` when the source is a URL or an
            in-memory buffer.
        url: The URL the stream was fetched from, if applicable.
            ``None`` for local files and in-memory buffers.
    """

    mimetype: Optional[str] = None
    extension: Optional[str] = None
    charset: Optional[str] = None
    filename: Optional[str] = None  # From local path, url, or Content-Disposition header
    local_path: Optional[str] = None  # If read from disk
    url: Optional[str] = None  # If read from url

    def copy_and_update(self, *args: "StreamInfo", **kwargs: Optional[str]) -> "StreamInfo":
        """Return a new :class:`StreamInfo` with selected fields overridden.

        Builds a fresh ``StreamInfo`` from the current instance's fields,
        then applies updates from each positional ``StreamInfo`` argument
        (non-``None`` fields only), and finally applies any explicit keyword
        arguments.  Later arguments win over earlier ones.

        Args:
            *args: Zero or more :class:`StreamInfo` instances whose non-``None``
                fields will be merged into the result, in order.
            **kwargs: Explicit field overrides that take precedence over
                everything else.  Keys must be valid ``StreamInfo`` field
                names; values may be ``None`` to clear a field.

        Returns:
            A new, frozen :class:`StreamInfo` reflecting all applied updates.

        Raises:
            AssertionError: If any positional argument is not a
                :class:`StreamInfo` instance.
            TypeError: If an unknown keyword argument is supplied.

        Example::

            base = StreamInfo(mimetype="application/pdf", filename="report.pdf")
            updated = base.copy_and_update(extension=".pdf", local_path="/tmp/report.pdf")
            # updated.mimetype == "application/pdf"
            # updated.extension == ".pdf"
            # updated.local_path == "/tmp/report.pdf"
        """
        new_info = asdict(self)

        for si in args:
            assert isinstance(si, StreamInfo), (
                f"Positional arguments must be StreamInfo instances, got {type(si).__name__}"
            )
            new_info.update({k: v for k, v in asdict(si).items() if v is not None})

        if len(kwargs) > 0:
            new_info.update(kwargs)

        return StreamInfo(**new_info)
