"""StreamInfo dataclass for carrying metadata about a file stream through the converter pipeline."""

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(kw_only=True, frozen=True)
class StreamInfo:
    """Immutable metadata bundle describing a binary file stream.

    All fields are optional and default to ``None``.  Which fields are
    populated depends on how the stream was obtained:

    * Local file opened by path → ``local_path``, ``filename``, ``extension``
      are typically set; ``url`` is ``None``.
    * HTTP response → ``url``, ``mimetype``, and possibly ``filename`` (from
      the ``Content-Disposition`` header) are set; ``local_path`` is ``None``.
    * Data URI → ``mimetype`` is set; ``url`` and ``local_path`` are ``None``.

    Attributes
    ----------
    mimetype:
        MIME type string (e.g. ``"application/pdf"``), if known.
    extension:
        File extension *including* the leading dot (e.g. ``".pdf"``), if known.
    charset:
        Character-set/encoding label (e.g. ``"utf-8"``), if known.  Relevant
        for text-based formats such as HTML, CSV, and JSON.
    filename:
        Base filename (without directory) derived from a local path, URL, or
        ``Content-Disposition`` header, if available.
    local_path:
        Absolute path on the local filesystem when the stream was opened from
        disk; ``None`` for remote or in-memory streams.
    url:
        Source URL when the stream was fetched over HTTP/HTTPS or was
        originally a remote reference; ``None`` for local-only streams.
    """

    mimetype: Optional[str] = None
    extension: Optional[str] = None
    charset: Optional[str] = None
    filename: Optional[str] = None  # From local path, URL, or Content-Disposition header
    local_path: Optional[str] = None  # Set when the stream was read from disk
    url: Optional[str] = None  # Set when the stream was fetched from a URL

    def copy_and_update(self, *args: "StreamInfo", **kwargs: Optional[str]) -> "StreamInfo":
        """Return a new :class:`StreamInfo` with selected fields overridden.

        Positional arguments must be :class:`StreamInfo` instances.  Their
        non-``None`` fields are merged in order, so later arguments take
        precedence over earlier ones.  Keyword arguments are applied last and
        take precedence over everything.

        Parameters
        ----------
        *args:
            Zero or more :class:`StreamInfo` instances whose non-``None``
            fields will be merged into the copy.
        **kwargs:
            Explicit field overrides applied after all positional arguments.

        Returns
        -------
        StreamInfo
            A new frozen :class:`StreamInfo` instance.

        Examples
        --------
        >>> base = StreamInfo(mimetype="application/octet-stream")
        >>> refined = base.copy_and_update(extension=".pdf", mimetype="application/pdf")
        >>> refined.mimetype
        'application/pdf'
        >>> refined.extension
        '.pdf'
        """
        new_info = asdict(self)

        for si in args:
            assert isinstance(si, StreamInfo)
            new_info.update({k: v for k, v in asdict(si).items() if v is not None})

        if kwargs:
            new_info.update(kwargs)

        return StreamInfo(**new_info)
