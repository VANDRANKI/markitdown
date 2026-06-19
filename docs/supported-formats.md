# Supported Input Formats

MarkItDown converts documents to Markdown. The table below lists all
supported input formats and any converter-specific notes.

## Document formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text extracted via `pdfminer`; image-only PDFs require OCR |
| Word | `.docx` | Tables converted to Markdown tables |
| PowerPoint | `.pptx` | Each slide becomes a Markdown section |
| Excel | `.xlsx` | Each sheet becomes a Markdown table |

## Web and markup formats

| Format | Extension | Notes |
|--------|-----------|-------|
| HTML | `.html`, `.htm` | Script and style tags stripped |
| XML | `.xml` | Tags stripped; text content preserved |
| RSS/Atom | `.rss`, `.atom` | Feed items become Markdown list entries |

## Data formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Converted to a Markdown table |
| JSON | `.json` | Pretty-printed in a fenced code block |

## Archive formats

| Format | Extension | Notes |
|--------|-----------|-------|
| ZIP | `.zip` | Contents are extracted and each file is converted |

## Image formats (with LLM vision)

| Format | Extension | Notes |
|--------|-----------|-------|
| JPEG | `.jpg`, `.jpeg` | LLM describes the image; requires `llm_client` |
| PNG | `.png` | LLM describes the image; requires `llm_client` |

## Adding a custom converter

See `CONTRIBUTING.md` for instructions on registering a new `DocumentConverter`
subclass for an unsupported format.
