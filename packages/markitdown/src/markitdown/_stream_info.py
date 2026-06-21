from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(kw_only=True, frozen=True)
class StreamInfo:
    """Immutable metadata describing a binary file stream.

    All fields are optional and will be ``None`` when the corresponding
    information is not available.  The set of populated fields depends on
    how the stream was opened:

    * Local file  – ``local_path``, ``filename``, and ``extension`` are
      typically set; ``url`` is ``None``.
    * HTTP response – ``url``, ``mimetype``, ``charset``, and ``filename``
      (from ``Content-Disposition``) may be set; ``local_path`` is ``None``.
    * Raw stream  – only the fields explicitly provided by the caller are set.

    Because the dataclass is frozen, use :meth:`copy_and_update` to create
    a modified copy rather than mutating an existing instance.
    """

    mimetype: Optional[str] = None
    """MIME type string, e.g. ``"application/pdf"`` or ``"text/html; charset=utf-8"``."""

    extension: Optional[str] = None
    """File extension including the leading dot, e.g. ``".pdf"`` or ``".docx"``."""

    charset: Optional[str] = None
    """Character-set / encoding name, e.g. ``"utf-8"`` or ``"latin-1"``."""

    filename: Optional[str] = None
    """Base filename derived from a local path, URL, or ``Content-Disposition`` header."""

    local_path: Optional[str] = None
    """Absolute path to the file on disk, set only when the stream was opened from a local file."""

    url: Optional[str] = None
    """Source URL, set only when the stream was fetched over the network."""

    def copy_and_update(
        self,
        *args: "StreamInfo",
        **kwargs: Optional[str],
    ) -> "StreamInfo":
        """Return a new :class:`StreamInfo` with selected fields overridden.

        Fields are applied left-to-right: the current instance is the base,
        each positional *StreamInfo* argument overlays non-``None`` values on
        top, and finally any *kwargs* are applied (including explicit ``None``
        to clear a field).

        Parameters
        ----------
        *args:
            Zero or more :class:`StreamInfo` instances whose non-``None``
            fields overwrite the corresponding fields of this instance.
        **kwargs:
            Explicit field overrides applied after all positional arguments.
            Pass ``field=None`` to clear a field that was previously set.

        Returns
        -------
        StreamInfo
            A new frozen :class:`StreamInfo` instance with the merged values.

        Examples
        --------
        >>> base = StreamInfo(mimetype="application/octet-stream", extension=".bin")
        >>> base.copy_and_update(extension=".pdf", mimetype="application/pdf")
        StreamInfo(mimetype='application/pdf', extension='.pdf', ...)
        """
        new_info = asdict(self)

        for si in args:
            assert isinstance(si, StreamInfo)
            new_info.update({k: v for k, v in asdict(si).items() if v is not None})

        if len(kwargs) > 0:
            new_info.update(kwargs)

        return StreamInfo(**new_info)
