import csv
import io
from typing import BinaryIO, Any
from charset_normalizer import from_bytes
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

ACCEPTED_MIME_TYPE_PREFIXES = [
    "text/csv",
    "application/csv",
]
ACCEPTED_FILE_EXTENSIONS = [".csv"]


class CsvConverter(DocumentConverter):
    """
    Converts CSV files to Markdown tables.

    The first row of the CSV is treated as a header row and rendered as the
    Markdown table header with a separator line beneath it.  Subsequent rows
    are rendered as data rows.

    Column count is normalised to the header width: short rows are padded with
    empty cells and over-wide rows are silently truncated.

    Accepted inputs
    ---------------
    * MIME types: ``text/csv``, ``application/csv`` (and prefixed variants)
    * Extensions: ``.csv``

    Example output
    --------------
    Given input::

        Name,Age,City
        Alice,30,New York
        Bob,25,London

    The converter produces::

        | Name  | Age | City     |
        | ----- | --- | -------- |
        | Alice | 30  | New York |
        | Bob   | 25  | London   |
    """

    def __init__(self) -> None:
        super().__init__()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """
        Return ``True`` when *stream_info* indicates a CSV file.

        The check is purely metadata-based (extension and MIME type); the
        stream is not read.

        Parameters
        ----------
        file_stream:
            The binary file stream (not inspected by this method).
        stream_info:
            Metadata about the stream.  ``extension`` and ``mimetype`` are
            the fields consulted.
        **kwargs:
            Ignored; present for interface compatibility.

        Returns
        -------
        bool
            ``True`` if the extension matches ``.csv`` or the MIME type
            starts with ``text/csv`` or ``application/csv``.
        """
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()
        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True
        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True
        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """
        Convert a CSV stream to a Markdown table.

        The stream is read in full.  If ``stream_info.charset`` is set the
        bytes are decoded with that charset; otherwise
        `charset-normalizer <https://charset-normalizer.readthedocs.io/>`_
        is used to detect the encoding automatically.

        An empty CSV (zero rows) returns an empty Markdown string rather than
        raising an exception.

        Parameters
        ----------
        file_stream:
            The binary file stream containing CSV data.
        stream_info:
            Metadata about the stream.  ``charset`` is used for decoding
            when available.
        **kwargs:
            Ignored; present for interface compatibility.

        Returns
        -------
        DocumentConverterResult
            The conversion result whose ``markdown`` field contains the
            rendered Markdown table, or an empty string for empty input.
        """
        # Read the file content
        if stream_info.charset:
            content = file_stream.read().decode(stream_info.charset)
        else:
            content = str(from_bytes(file_stream.read()).best())

        # Parse CSV content
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        if not rows:
            return DocumentConverterResult(markdown="")

        # Create markdown table
        markdown_table = []

        # Add header row
        markdown_table.append("| " + " | ".join(rows[0]) + " |")

        # Add separator row
        markdown_table.append("| " + " | ".join(["---"] * len(rows[0])) + " |")

        # Add data rows
        for row in rows[1:]:
            # Pad short rows to match the header column count
            while len(row) < len(rows[0]):
                row.append("")
            # Truncate rows that are wider than the header
            row = row[: len(rows[0])]
            markdown_table.append("| " + " | ".join(row) + " |")

        result = "\n".join(markdown_table)

        return DocumentConverterResult(markdown=result)
