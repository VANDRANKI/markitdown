# MarkItDown Converter Guide

A practical reference for using and extending MarkItDown converters.

---

## Supported input types

| Format | Notes |
|--------|-------|
| `.pdf` | Requires `pymupdf` or `pdfminer.six` |
| `.docx` | Microsoft Word 2007+ |
| `.xlsx`, `.xls` | Spreadsheets; each sheet becomes a markdown table |
| `.pptx` | PowerPoint; each slide becomes a markdown section |
| `.html`, `.htm` | HTML with trafilatura for clean body extraction |
| `.md`, `.txt` | Pass-through |
| `.csv` | Converted to a markdown table |
| `.png`, `.jpg`, `.webp` | Requires an Azure/OpenAI vision model for OCR |
| Audio `.mp3`, `.wav` | Requires Azure Speech or Whisper API |

---

## Basic usage

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("report.pdf")
print(result.text_content)
```

### Converting from a URL

```python
result = md.convert("https://example.com/page")
```

### Converting from a file-like object

```python
with open("document.docx", "rb") as fh:
    result = md.convert_stream(fh, file_extension=".docx")
```

---

## Error handling

MarkItDown raises `MarkItDownException` when a file cannot be converted:

```python
from markitdown import MarkItDown, MarkItDownException

md = MarkItDown()
try:
    result = md.convert("corrupted_file.pdf")
except MarkItDownException as exc:
    print(f"Conversion failed: {exc}")
    # Log and continue, or re-raise depending on your use case.
```

---

## Writing a custom converter

Create a class that inherits from `DocumentConverter` and implement the
`convert` method:

```python
from markitdown import DocumentConverter, DocumentConverterResult

class MyXmlConverter(DocumentConverter):
    """Convert custom XML reports to Markdown."""

    SUPPORTED_EXTENSIONS = [".myxml"]

    def convert(
        self,
        local_path: str,
        **kwargs,
    ) -> DocumentConverterResult | None:
        """Convert an XML file to Markdown.

        Args:
            local_path: Filesystem path to the input file.
            **kwargs: Additional keyword arguments (e.g. ``file_extension``).

        Returns:
            A :class:`DocumentConverterResult` on success, or *None* if this
            converter cannot handle the given file.
        """
        import xml.etree.ElementTree as ET

        ext = kwargs.get("file_extension", "")
        if ext.lower() not in self.SUPPORTED_EXTENSIONS:
            return None

        tree = ET.parse(local_path)
        root = tree.getroot()
        lines = [f"# {root.tag}"]
        for child in root:
            lines.append(f"## {child.tag}")
            lines.append(child.text or "")
        return DocumentConverterResult(title=root.tag, text_content="\n".join(lines))

# Register the converter
md = MarkItDown()
md.register_converter(MyXmlConverter())
```
