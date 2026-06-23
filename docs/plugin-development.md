# MarkItDown Plugin Development

This guide explains how to create custom converters that extend MarkItDown's file-type support.

## Converter Interface

All converters must implement the `DocumentConverter` protocol:

```python
from markitdown import DocumentConverter, DocumentConverterResult
from typing import BinaryIO, Optional

class MyCustomConverter(DocumentConverter):
    """Convert .myformat files to Markdown."""

    def convert(
        self,
        local_path: str,
        **kwargs: object,
    ) -> Optional[DocumentConverterResult]:
        """Convert a file to Markdown.

        Args:
            local_path: Absolute path to the file on disk.
            **kwargs: Additional options (e.g., `url`, `file_extension`).

        Returns:
            A `DocumentConverterResult` with the Markdown content,
            or `None` if this converter cannot handle the file.
        """
        # Check if this converter applies to the file
        ext = kwargs.get("file_extension", "")
        if ext.lower() != ".myformat":
            return None

        # Read and convert the file
        with open(local_path, "rb") as f:
            content = self._parse(f)

        return DocumentConverterResult(
            title=self._extract_title(content),
            text_content=self._to_markdown(content),
        )

    def _parse(self, f: BinaryIO) -> dict:
        """Parse the binary file content."""
        ...

    def _extract_title(self, content: dict) -> Optional[str]:
        """Extract document title from parsed content."""
        return content.get("title")

    def _to_markdown(self, content: dict) -> str:
        """Render parsed content as Markdown."""
        ...
```

## Registering a Converter

```python
from markitdown import MarkItDown

md = MarkItDown()
md.register_converter(MyCustomConverter())

# Now it handles .myformat files automatically
result = md.convert("document.myformat")
print(result.text_content)
```

## Error Handling

Converters should handle errors gracefully:

```python
import logging

logger = logging.getLogger(__name__)

class RobustConverter(DocumentConverter):
    def convert(self, local_path: str, **kwargs: object):
        try:
            return self._do_convert(local_path, **kwargs)
        except FileNotFoundError:
            logger.warning("File not found: %s", local_path)
            return None
        except (ValueError, KeyError) as e:
            logger.error("Failed to parse %s: %s", local_path, e)
            return None
```

## Running Tests

```bash
# Install with development extras
pip install -e packages/markitdown[dev]

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_converters.py -v -k "test_pdf"
```

## Type Checking

```bash
mypy packages/markitdown/src/
```
