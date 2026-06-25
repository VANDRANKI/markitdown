# Supported Formats Reference

This page lists all input formats MarkItDown can convert to Markdown,
along with their dependencies and known limitations.

## Format Support Table

| Format | Extension | Extra Dependency | Notes |
|---|---|---|---|
| PDF | `.pdf` | None (built-in) | Text-layer PDFs; scanned PDFs require OCR |
| Word Document | `.docx` | None (built-in) | Full text, tables, headings |
| Excel Spreadsheet | `.xlsx` | None (built-in) | Each sheet becomes a Markdown table |
| PowerPoint | `.pptx` | None (built-in) | Slide text and speaker notes |
| HTML | `.html`, `.htm` | None (built-in) | Strips scripts/styles, preserves structure |
| CSV | `.csv` | None (built-in) | Converted to Markdown table |
| JSON | `.json` | None (built-in) | Pretty-printed as fenced code block |
| XML | `.xml` | None (built-in) | Pretty-printed as fenced code block |
| Plain Text | `.txt` | None (built-in) | Passed through as-is |
| Markdown | `.md` | None (built-in) | Passed through as-is |
| Images | `.jpg`, `.png`, `.gif`, `.bmp`, `.tiff` | Optional: vision-capable LLM | Describes image content via LLM |
| Audio | `.mp3`, `.wav`, `.m4a` | Optional: Whisper / speech-to-text | Transcribes audio to text |
| ZIP Archive | `.zip` | None (built-in) | Recursively converts contained files |
| YouTube URL | URL | `yt-dlp` | Extracts transcript if available |
| Wikipedia URL | URL | None | Extracts article text |

## Using Optional Dependencies

### Image Description (Vision LLM)

```python
import markitdown
from openai import OpenAI

client = OpenAI()
md = markitdown.MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("photo.jpg")
print(result.text_content)
```

### Audio Transcription

```python
# Requires openai package with Whisper access
md = markitdown.MarkItDown(llm_client=client, llm_model="whisper-1")
result = md.convert("lecture.mp3")
```

## Known Limitations

- **Scanned PDFs**: Text cannot be extracted without OCR. Use an OCR pre-processor
  (e.g., Tesseract) and convert the resulting text file instead.
- **Password-protected files**: Word, Excel, and PDF files with passwords are not supported.
- **Complex layouts**: Multi-column PDFs and heavily formatted Word documents
  may lose some structural information during conversion.
- **Large Excel files**: Very large spreadsheets (10,000+ rows) may be truncated
  to keep Markdown output manageable.
- **Embedded images in Office files**: Images inside `.docx`/`.pptx` files
  are skipped unless a vision LLM is configured.
