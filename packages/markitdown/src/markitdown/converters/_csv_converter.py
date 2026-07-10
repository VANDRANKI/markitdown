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
    """

    def __init__(self):
        super().__init__()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
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
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        """Convert a CSV stream into a Markdown table.

        The file is decoded using ``stream_info.charset`` if provided, otherwise the
        charset is auto-detected via ``charset_normalizer``. Rows are parsed with the
        standard ``csv`` module (default dialect: comma-delimited, double-quoted).
        The first row is treated as the header. Data rows with fewer columns than the
        header are padded with empty strings; rows with more columns are truncated to
        match the header width. Cell values are not escaped, so values containing a
        literal ``|`` character will break the resulting Markdown table's column
        alignment.

        Args:
            file_stream: Binary stream containing the CSV data.
            stream_info: Metadata about the stream, used here for `charset` detection.

        Returns:
            A `DocumentConverterResult` with the CSV rendered as a Markdown table
            (or an empty markdown string if the CSV has no rows).
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
            # Make sure row has the same number of columns as header
            while len(row) < len(rows[0]):
                row.append("")
            # Truncate if row has more columns than header
            row = row[: len(rows[0])]
            markdown_table.append("| " + " | ".join(row) + " |")

        result = "\n".join(markdown_table)

        return DocumentConverterResult(markdown=result)
