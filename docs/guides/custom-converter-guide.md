# Writing Custom Converters

MarkItDown supports extending the conversion pipeline with custom converters
for file types not covered by the built-in handlers. This guide explains the
interface, registration, and testing patterns.

## The `DocumentConverter` Interface

Every converter must implement `DocumentConverter`:

```python
from markitdown import DocumentConverter, DocumentConverterResult


class MyConverter(DocumentConverter):
    """Convert .myext files to Markdown."""

    def convert(
        self,
        local_path: str,
        **kwargs,
    ) -> DocumentConverterResult | None:
        """Attempt to convert the file at `local_path`.

        Args:
            local_path: Absolute path to the local copy of the file to convert.
            **kwargs: Additional context such as `file_extension`, `url`, or
                `parent_converters`.

        Returns:
            A `DocumentConverterResult` if this converter can handle the file,
            or `None` to signal that the next converter should be tried.
        """
        extension = kwargs.get("file_extension", "").lower()
        if extension != ".myext":
            return None

        with open(local_path, "r", encoding="utf-8") as fh:
            raw = fh.read()

        markdown = self._transform(raw)
        return DocumentConverterResult(
            title=None,
            text_content=markdown,
        )

    def _transform(self, raw: str) -> str:
        """Apply domain-specific transformation logic."""
        # Example: wrap every line in a Markdown code block
        lines = raw.strip().splitlines()
        return "```\n" + "\n".join(lines) + "\n```"
```

---

## Registering Your Converter

```python
from markitdown import MarkItDown

md = MarkItDown()
md.register_converter(MyConverter())

# The custom converter is now tried for every conversion request
result = md.convert("data/report.myext")
print(result.text_content)
```

Converters are tried in **registration order**, most-recently-registered first.
Built-in converters run last as fallbacks.

---

## Parsing Structured Formats

For structured formats (JSON, YAML, TOML) that should render as Markdown
tables or code blocks:

```python
import json
from markitdown import DocumentConverter, DocumentConverterResult


class JsonToTableConverter(DocumentConverter):
    """Render JSON arrays-of-objects as Markdown tables."""

    def convert(self, local_path: str, **kwargs) -> DocumentConverterResult | None:
        if kwargs.get("file_extension", "").lower() != ".json":
            return None

        with open(local_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        if not isinstance(data, list) or not data:
            return None  # let the default JSON handler take over

        if not isinstance(data[0], dict):
            return None

        headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]

        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join("---" for _ in headers) + " |\n"
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"

        return DocumentConverterResult(title=None, text_content=table)
```

---

## Using LLM-Assisted Conversion

For complex formats (scanned PDFs, diagrams, slides), delegate to an LLM:

```python
from markitdown import MarkItDown

# Pass an OpenAI client to enable LLM-assisted conversions
from openai import OpenAI
openai_client = OpenAI()

md = MarkItDown(llm_client=openai_client, llm_model="gpt-4o")
result = md.convert("presentation.pptx")
print(result.text_content)
```

LLM-assisted conversion is used automatically for image slides and other
content types that require visual understanding.

---

## Testing Your Converter

```python
import tempfile
import os
from markitdown import MarkItDown


def test_myext_converter():
    converter = MyConverter()
    md_app = MarkItDown()
    md_app.register_converter(converter)

    # Write a temporary test file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".myext", delete=False, encoding="utf-8"
    ) as fh:
        fh.write("line one\nline two\n")
        tmp_path = fh.name

    try:
        result = md_app.convert(tmp_path)
        assert result is not None
        assert "line one" in result.text_content
        assert "line two" in result.text_content
    finally:
        os.unlink(tmp_path)
```

---

## Built-In Converter Reference

| Converter | Handled Extensions |
|-----------|--------------------|
| `PlainTextConverter` | `.txt`, `.md`, `.rst` |
| `HtmlConverter` | `.html`, `.htm` |
| `DocxConverter` | `.docx` |
| `PdfConverter` | `.pdf` |
| `PptxConverter` | `.pptx` |
| `XlsxConverter` | `.xlsx` |
| `ImageConverter` (LLM) | `.jpg`, `.png`, `.gif`, `.webp` |
| `ZipConverter` | `.zip` |
| `YouTubeConverter` | YouTube URLs |

Register a custom converter with the same extension to **override** the
built-in handler for that type.
