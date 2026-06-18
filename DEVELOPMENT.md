# MarkItDown Development Guide

## Setup

```bash
git clone https://github.com/VANDRANKI/markitdown.git
cd markitdown
pip install -e "packages/markitdown[dev]"
```

## Running Tests

```bash
# All tests
pytest packages/markitdown/tests/ -v

# Single file
pytest packages/markitdown/tests/test_converters.py -v

# With coverage
pytest packages/markitdown/tests/ --cov=markitdown --cov-report=html
```

## Writing a Custom Converter

Converters live in `packages/markitdown/src/markitdown/converters/` and
must implement the `DocumentConverter` interface:

```python
from markitdown import DocumentConverter, DocumentConverterResult

class MyFormatConverter(DocumentConverter):
    """Convert MyFormat files to Markdown."""

    def convert(
        self,
        local_path: str,
        **kwargs,
    ) -> DocumentConverterResult | None:
        """Return None if this converter does not handle the file.

        Args:
            local_path: Path to the downloaded / local file.
            **kwargs: Extra options (e.g., url, file_extension).

        Returns:
            A DocumentConverterResult with the Markdown content,
            or None to fall through to the next converter.
        """
        file_ext = kwargs.get("file_extension", "")
        if file_ext.lower() != ".myformat":
            return None

        # ... conversion logic ...
        return DocumentConverterResult(
            title="Document Title",
            text_content="# Document Title\n\nContent here...",
        )
```

Register it:

```python
from markitdown import MarkItDown
from my_package import MyFormatConverter

md = MarkItDown()
md.register_converter(MyFormatConverter())
result = md.convert("document.myformat")
print(result.text_content)
```

## Adding a Built-in Converter

1. Create `packages/markitdown/src/markitdown/converters/my_format.py`
2. Implement `DocumentConverter`
3. Register it in `_markitdown.py` inside `MarkItDown.__init__`
4. Add tests in `packages/markitdown/tests/test_converters.py`
5. Add a sample test file under `packages/markitdown/tests/test_files/`

## Code Style

```bash
ruff format .    # formatting
ruff check .     # linting
mypy src/        # type checking
```

## Docker (quick functional test)

```bash
docker build -t markitdown .
docker run --rm markitdown --help
```

## Commit Convention

```
feat: add PPTX slide notes to converter output
fix: handle password-protected DOCX files gracefully
docs: add example for YouTube transcript conversion
test: add coverage for edge cases in HTML table parsing
```
