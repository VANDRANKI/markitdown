"""Abstract base classes for MarkItDown document converters.

This module defines the two foundational abstractions that all built-in
and third-party converters must implement:

* :class:`DocumentConverterResult` — a lightweight wrapper around the
  converted Markdown text and optional document metadata.
* :class:`DocumentConverter` — the abstract converter interface with two
  methods that subclasses must override: :meth:`~DocumentConverter.accepts`
  and :meth:`~DocumentConverter.convert`.

Plugin authors should subclass :class:`DocumentConverter` and register
their converter with :class:`~markitdown.MarkItDown` via
:meth:`~markitdown.MarkItDown.register_converter`.
"""

from typing import Any, BinaryIO, Optional
from ._stream_info import StreamInfo


class DocumentConverterResult:
    """Wraps the output of a single document conversion.

    Attributes:
        markdown: The full Markdown representation of the converted document.
        title: Optional human-readable title extracted from the document
            (e.g. the ``<title>`` tag of an HTML file or the metadata title
            of a PDF).  ``None`` when the converter could not determine a
            title.
    """

    def __init__(
        self,
        markdown: str,
        *,
        title: Optional[str] = None,
    ) -> None:
        """Initialise a conversion result.

        Args:
            markdown: The converted Markdown text.  Must not be ``None``;
                pass an empty string ``''`` if the document produced no
                meaningful output.
            title: Optional document title.  Defaults to ``None``.
        """
        self.markdown = markdown
        self.title = title

    @property
    def text_content(self) -> str:
        """Soft-deprecated alias for :attr:`markdown`.

        New code should access :attr:`markdown` directly or rely on
        ``str(result)``.  This property will be removed in a future
        major release.
        """
        return self.markdown

    @text_content.setter
    def text_content(self, markdown: str) -> None:
        """Soft-deprecated setter alias for :attr:`markdown`.

        Prefer assigning to :attr:`markdown` directly.  Will be removed
        in a future major release.
        """
        self.markdown = markdown

    def __str__(self) -> str:
        """Return the converted Markdown text.

        Returns:
            The full Markdown string stored in :attr:`markdown`.
        """
        return self.markdown


class DocumentConverter:
    """Abstract base class for all MarkItDown document converters.

    Subclasses must implement both :meth:`accepts` and :meth:`convert`.
    The :meth:`accepts` method is called first and acts as a cheap gate;
    only if it returns ``True`` will :meth:`convert` be invoked.

    See the plugin guide for a complete walk-through:
    https://github.com/microsoft/markitdown/blob/main/PLUGINS.md
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """Return ``True`` if this converter can handle the given stream.

        The check should be as cheap as possible — typically an
        ``O(1)`` comparison of ``stream_info.mimetype`` or
        ``stream_info.extension``.  For URL-based converters (e.g.
        Wikipedia, YouTube) ``stream_info.url`` may also be inspected.

        Seeking within ``file_stream`` is strongly discouraged.  If
        peeking at file bytes is unavoidable, the method *must* restore
        the stream position before returning::

            cur_pos = file_stream.tell()
            header = file_stream.read(4)
            file_stream.seek(cur_pos)  # always reset

        Args:
            file_stream: Open binary stream to inspect.  Supports
                ``read()``, ``seek()``, and ``tell()``.
            stream_info: Metadata about the stream (MIME type, extension,
                filename, URL, etc.).  See :class:`~markitdown.StreamInfo`.
            **kwargs: Additional options forwarded from the calling
                :class:`~markitdown.MarkItDown` instance.

        Returns:
            ``True`` if :meth:`convert` should be called for this stream;
            ``False`` to skip this converter and try the next one.

        Raises:
            NotImplementedError: If the subclass has not overridden this method.
        """
        raise NotImplementedError(
            f"The subclass, {type(self).__name__}, must implement the accepts() method "
            "to determine if they can handle the document."
        )

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """Convert the document stream to Markdown.

        This method is called only when :meth:`accepts` returned ``True``
        for the same ``file_stream`` and ``stream_info``.

        The stream position on entry is the same as after the preceding
        :meth:`accepts` call (i.e. at the beginning of the file, unless
        :meth:`accepts` advanced and did not reset it — which it should
        never do).

        Args:
            file_stream: Open binary stream to convert.  Supports
                ``read()``, ``seek()``, and ``tell()``.
            stream_info: Metadata about the stream.  The same object
                that was passed to :meth:`accepts`.
            **kwargs: Converter-specific options.  Unknown keys should
                be silently ignored to allow forward compatibility.

        Returns:
            A :class:`DocumentConverterResult` containing at least the
            ``markdown`` field.  The ``title`` field should be populated
            whenever a reliable title can be extracted from the document.

        Raises:
            FileConversionException: If the format is recognised but
                conversion fails for any other reason.
            MissingDependencyException: If an optional dependency
                required by this converter is not installed.
            NotImplementedError: If the subclass has not overridden
                this method.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement the convert() method."
        )
