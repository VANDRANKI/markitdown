# Authoring Custom Converters for MarkItDown

This guide walks through writing, testing, and registering a custom `DocumentConverter` plugin.

## The `DocumentConverter` Interface

Every converter implements two methods:

```python
from markitdown import DocumentConverter, DocumentConverterResult
from typing import BinaryIO


class MyConverter(DocumentConverter):
    """Convert .myformat files to Markdown."""

    def convert(
        self,
        source: str | BinaryIO,
        **kwargs,
    ) -> DocumentConverterResult | None:
        """Convert a source file or stream to Markdown.

        Args:
            source: File path (str) or binary stream to convert.
            **kwargs: Extra options forwarded by MarkItDown (e.g. file_extension).

        Returns:
            A `DocumentConverterResult` on success, or None if this converter
            cannot handle the given source (lets the next converter try).
        """
        file_extension = kwargs.get("file_extension", "")
        if file_extension.lower() not in (".myformat", ".myfmt"):
            return None  # signal: not handled
        content = self._extract_content(source)
        return DocumentConverterResult(
            title=self._extract_title(content),
            text_content=self._to_markdown(content),
        )

    def _extract_content(self, source: str | BinaryIO) -> str:
        if isinstance(source, str):
            with open(source, encoding="utf-8") as f:
                return f.read()
        return source.read().decode("utf-8")

    def _extract_title(self, content: str) -> str | None:
        """Extract the document title from raw content, or return None."""
        lines = content.splitlines()
        return lines[0].strip() if lines else None

    def _to_markdown(self, content: str) -> str:
        """Convert raw content to Markdown text."""
        return content  # replace with real transformation
```

## Returning `None` vs Raising

- Return `None` when the converter **can't handle** the file (wrong type, wrong extension).
- **Raise** `FileNotFoundError`, `ValueError`, or `RuntimeError` when the file is the right type but conversion fails — this surfaces the error to the caller rather than silently skipping.

## Registering Your Converter

```python
from markitdown import MarkItDown

md = MarkItDown()
md.register_converter(MyConverter())

# or via entry_points in pyproject.toml:
# [project.entry-points."markitdown.converters"]
# myformat = "mypackage.converters:MyConverter"
```

## File Validation Helpers

Use these helpers to validate inputs before conversion:

```python
import os
from pathlib import Path


def require_file_exists(path: str) -> Path:
    """Validate that a file path exists and is a regular file.

    Args:
        path: Filesystem path to validate.

    Returns:
        Resolved `Path` object.

    Raises:
        FileNotFoundError: If the path does not exist.
        IsADirectoryError: If the path points to a directory.
    """
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if resolved.is_dir():
        raise IsADirectoryError(f"Expected a file, got a directory: {path}")
    return resolved


def get_file_extension(path: str | Path) -> str:
    """Return the lowercase file extension including the dot.

    Args:
        path: File path to inspect.

    Returns:
        Lowercase extension string, e.g. `".pdf"`, or `""` if none.
    """
    return Path(path).suffix.lower()


def check_file_size(
    path: str | Path,
    max_bytes: int = 100 * 1024 * 1024,  # 100 MB default
) -> None:
    """Assert a file does not exceed the maximum allowed size.

    Args:
        path: File path to check.
        max_bytes: Maximum allowed file size in bytes.

    Raises:
        ValueError: If the file exceeds `max_bytes`.
    """
    size = os.path.getsize(path)
    if size > max_bytes:
        raise ValueError(
            f"File too large: {size:,} bytes (max {max_bytes:,} bytes)"
        )
```

## Testing Your Converter

```python
import pytest
from markitdown import MarkItDown


def test_myformat_conversion(tmp_path):
    sample = tmp_path / "test.myformat"
    sample.write_text("Title Line\nBody content", encoding="utf-8")

    md = MarkItDown()
    md.register_converter(MyConverter())
    result = md.convert(str(sample))

    assert result.text_content is not None
    assert "Title Line" in result.text_content


def test_wrong_extension_returns_none():
    converter = MyConverter()
    result = converter.convert("document.txt", file_extension=".txt")
    assert result is None
```

## Best Practices

1. **Always check the extension first** — return `None` early if the file type doesn't match.
2. **Handle both str and BinaryIO** — callers may pass either.
3. **Use `pathlib.Path`** — more readable and cross-platform than `os.path`.
4. **Close streams you open** — use context managers (`with open(...) as f`).
5. **Add entry_points** — makes your converter installable as a plugin without code changes.
