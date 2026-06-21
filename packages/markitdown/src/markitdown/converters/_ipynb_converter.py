from typing import BinaryIO, Any, Optional
import json

from .._base_converter import DocumentConverter, DocumentConverterResult
from .._exceptions import FileConversionException
from .._stream_info import StreamInfo

CANDIDATE_MIME_TYPE_PREFIXES = [
    "application/json",
]

ACCEPTED_FILE_EXTENSIONS = [".ipynb"]


class IpynbConverter(DocumentConverter):
    """
    Converts Jupyter Notebook (``.ipynb``) files to Markdown.

    Each notebook cell is rendered according to its type:

    * **markdown** cells are included verbatim.
    * **code** cells are wrapped in a fenced ``python`` code block.
    * **raw** cells are wrapped in a plain (un-annotated) fenced code block.

    The document title is extracted from the first ``# ``-prefixed heading
    found in any markdown cell, unless the notebook's own metadata supplies
    a ``title`` field (which takes precedence).

    Accepted inputs
    ---------------
    * Extensions: ``.ipynb``
    * MIME type ``application/json`` is also accepted *after* a content
      sniff confirms the presence of the ``nbformat`` key.
    """

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """
        Return ``True`` when the stream appears to be a Jupyter Notebook.

        Determination is made in two stages:

        1. If the file extension is ``.ipynb``, accept immediately without
           reading the stream.
        2. If the MIME type matches ``application/json``, peek at the raw
           bytes to check for the ``nbformat`` and ``nbformat_minor`` keys
           that are mandatory in every valid notebook.  The stream position
           is reset before returning so that ``convert()`` can re-read from
           the beginning.

        Parameters
        ----------
        file_stream:
            The binary file stream to inspect.
        stream_info:
            Metadata about the stream.  ``extension``, ``mimetype``, and
            ``charset`` are consulted.
        **kwargs:
            Ignored; present for interface compatibility.

        Returns
        -------
        bool
            ``True`` if the stream is (or appears to be) a Jupyter Notebook.
        """
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in CANDIDATE_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                # Read further to see if it's a notebook
                cur_pos = file_stream.tell()
                try:
                    encoding = stream_info.charset or "utf-8"
                    notebook_content = file_stream.read().decode(encoding)
                    return (
                        "nbformat" in notebook_content
                        and "nbformat_minor" in notebook_content
                    )
                finally:
                    file_stream.seek(cur_pos)

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """
        Convert a Jupyter Notebook stream to Markdown.

        The stream is read in full, parsed as JSON, and each cell is
        rendered to Markdown via :meth:`_convert`.

        Parameters
        ----------
        file_stream:
            The binary file stream containing ``.ipynb`` JSON data.
        stream_info:
            Metadata about the stream.  ``charset`` is used for decoding
            when present; defaults to ``"utf-8"``.
        **kwargs:
            Ignored; present for interface compatibility.

        Returns
        -------
        DocumentConverterResult
            The conversion result.  ``title`` is populated when a heading
            or notebook metadata title is found.

        Raises
        ------
        FileConversionException
            If the notebook JSON cannot be parsed or an unexpected error
            occurs during cell processing.
        """
        # Parse and convert the notebook
        encoding = stream_info.charset or "utf-8"
        notebook_content = file_stream.read().decode(encoding=encoding)
        return self._convert(json.loads(notebook_content))

    def _convert(self, notebook_content: dict) -> DocumentConverterResult:
        """
        Convert parsed notebook JSON to a :class:`DocumentConverterResult`.

        This helper exists so the conversion logic can be unit-tested
        independently of stream I/O.

        Parameters
        ----------
        notebook_content:
            The notebook parsed from JSON -- a dict with at least a
            ``"cells"`` key containing a list of cell objects.

        Returns
        -------
        DocumentConverterResult
            Markdown text assembled from all cells, plus an optional title.

        Raises
        ------
        FileConversionException
            Wraps any unexpected exception raised while processing cells.
        """
        try:
            md_output = []
            title: Optional[str] = None

            for cell in notebook_content.get("cells", []):
                cell_type = cell.get("cell_type", "")
                source_lines = cell.get("source", [])

                if cell_type == "markdown":
                    md_output.append("".join(source_lines))

                    # Extract the first # heading as title if not already found
                    if title is None:
                        for line in source_lines:
                            if line.startswith("# "):
                                title = line.lstrip("# ").strip()
                                break

                elif cell_type == "code":
                    # Code cells are wrapped in Markdown code blocks
                    md_output.append(f"```python\n{''.join(source_lines)}\n```")
                elif cell_type == "raw":
                    md_output.append(f"```\n{''.join(source_lines)}\n```")

            md_text = "\n\n".join(md_output)

            # Notebook-level metadata title takes precedence over cell headings
            title = notebook_content.get("metadata", {}).get("title", title)

            return DocumentConverterResult(
                markdown=md_text,
                title=title,
            )

        except Exception as e:
            raise FileConversionException(
                f"Error converting .ipynb file: {e}"
            ) from e
