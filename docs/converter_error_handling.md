# MarkItDown Converter Error Handling

This guide documents how converters should handle errors, what exceptions
to raise, and how to distinguish between format detection failures and
conversion failures.

## Exception Hierarchy

```
Exception
└── MarkItDownException           # base for all MarkItDown errors
    ├── FileConversionException    # conversion of a known format failed
    ├── UnsupportedFormatException # no converter handles this file type
    └── MissingDependencyException # required library not installed
```

## When to Raise vs Return

Converters must raise on failures — never return an empty string or `None`:

```python
from markitdown._exceptions import FileConversionException

class PdfConverter(DocumentConverter):
    def convert(
        self,
        local_path: str,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        try:
            text = self._extract_pdf_text(local_path)
        except PdfReadError as e:
            # Raise, don't return empty string — the caller can't distinguish
            # between an empty PDF and a conversion failure.
            raise FileConversionException(
                f"Failed to read PDF '{local_path}': {e}"
            ) from e

        if not text.strip():
            # Empty is OK if the PDF is legitimately blank (e.g., scanned image)
            # Return a note rather than raising.
            return DocumentConverterResult(
                title=None,
                text_content="[PDF contains no extractable text — may be image-only]",
            )

        return DocumentConverterResult(title=None, text_content=text)
```

## Format Detection Errors

The `accepts()` method must never raise — it's called speculatively on all
converters. Return `False` instead of raising:

```python
def accepts(
    self,
    local_path: str,
    url: Optional[str] = None,
    **kwargs: Any,
) -> bool:
    # WRONG: raises on non-PDF files
    with open(local_path, 'rb') as f:
        PdfReader(f)  # raises PdfReadError for non-PDF
    return True

    # CORRECT: catch and return False
    try:
        with open(local_path, 'rb') as f:
            PdfReader(f)
        return True
    except Exception:
        return False
```

## Dependency Checking

If a converter requires an optional dependency, check at import time and
skip registration if the library is missing:

```python
try:
    from pypdf import PdfReader
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False


class PdfConverter(DocumentConverter):
    def accepts(self, local_path: str, **kwargs: Any) -> bool:
        if not _PYPDF_AVAILABLE:
            return False  # silently skip — user didn't install pypdf
        ...

    def convert(self, local_path: str, **kwargs: Any) -> DocumentConverterResult:
        if not _PYPDF_AVAILABLE:
            from markitdown._exceptions import MissingDependencyException
            raise MissingDependencyException(
                "pypdf is required for PDF conversion. "
                "Install it with: pip install markitdown[pdf]"
            )
        ...
```

## Page Limit Behavior

PDF and DOCX converters may hit page limits. Do not silently truncate:

```python
MAX_PAGES = 1000  # configurable via kwargs

def _extract_pdf_text(self, path: str, max_pages: int = MAX_PAGES) -> str:
    reader = PdfReader(path)
    total_pages = len(reader.pages)

    if total_pages > max_pages:
        # Warn the caller rather than silently dropping pages
        import warnings
        warnings.warn(
            f"PDF has {total_pages} pages; only the first {max_pages} will be "
            "converted. Pass max_pages=N to convert more.",
            UserWarning,
            stacklevel=3,
        )

    pages = reader.pages[:max_pages]
    return "\n\n".join(
        page.extract_text() or "" for page in pages
    )
```

## Testing Error Paths

Every converter must have tests for the failure path:

```python
import pytest
from markitdown import MarkItDown
from markitdown._exceptions import FileConversionException

def test_pdf_converter_raises_on_corrupt_file(tmp_path):
    corrupt_pdf = tmp_path / "corrupt.pdf"
    corrupt_pdf.write_bytes(b"this is not a PDF")

    md = MarkItDown()
    with pytest.raises(FileConversionException, match="Failed to read PDF"):
        md.convert(str(corrupt_pdf))

def test_pdf_converter_handles_blank_pdf(blank_pdf_path):
    md = MarkItDown()
    result = md.convert(blank_pdf_path)
    assert "image-only" in result.text_content  # note, not empty string
```
