# Adding a New MarkItDown Converter

Step-by-step guide for adding support for a new file format.

## 1. Create the Converter Class

Create `packages/markitdown/src/markitdown/converters/<format>_converter.py`:

```python
from typing import Any, Optional
from markitdown._base_converter import DocumentConverter, DocumentConverterResult


class CsvConverter(DocumentConverter):
    """Convert CSV files to Markdown tables."""

    def accepts(
        self,
        local_path: str,
        url: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Return True only for .csv files."""
        return local_path.lower().endswith(".csv")

    def convert(
        self,
        local_path: str,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """Convert a CSV file to a Markdown table.

        Args:
            local_path: Path to the local CSV file.
            **kwargs: Unused keyword arguments.

        Returns:
            A DocumentConverterResult with the table in Markdown format.

        Raises:
            FileConversionException: If the CSV cannot be parsed.
        """
        import csv
        from markitdown._exceptions import FileConversionException

        try:
            with open(local_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except (OSError, csv.Error) as e:
            raise FileConversionException(
                f"Failed to parse CSV '{local_path}': {e}"
            ) from e

        if not rows:
            return DocumentConverterResult(title=None, text_content="(empty CSV)")

        header = rows[0]
        separator = ["---"] * len(header)
        data_rows = rows[1:]

        lines = []
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(separator) + " |")
        for row in data_rows:
            lines.append("| " + " | ".join(row) + " |")

        return DocumentConverterResult(title=None, text_content="\n".join(lines))
```

## 2. Register the Converter

In `packages/markitdown/src/markitdown/_markitdown.py`, import and register:

```python
from markitdown.converters.csv_converter import CsvConverter

class MarkItDown:
    def __init__(self, ...):
        ...
        self.register_converter(CsvConverter())
```

## 3. Add Tests

Create `packages/markitdown/tests/test_csv_converter.py`:

```python
import pytest
from markitdown import MarkItDown

FIXTURE_CSV = "tests/fixtures/sample.csv"

def test_csv_converts_to_markdown_table():
    md = MarkItDown()
    result = md.convert(FIXTURE_CSV)
    assert "| Name |" in result.text_content
    assert "| ---" in result.text_content

def test_csv_empty_file(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    md = MarkItDown()
    result = md.convert(str(empty))
    assert "empty" in result.text_content.lower()
```

## 4. Add the Test Fixture

Create `packages/markitdown/tests/fixtures/sample.csv`:

```csv
Name,Age,City
Alice,30,New York
Bob,25,San Francisco
```

## 5. Update Documentation

- Add the new format to the supported formats table in `README.md`
- Add the optional dependency to `packages/markitdown/pyproject.toml`
  under the `[project.optional-dependencies]` section if needed
