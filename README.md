# MarkItDown

[![PyPI](https://img.shields.io/pypi/v/markitdown.svg)](https://pypi.org/project/markitdown/)
![PyPI - Downloads](https://img.shields.io/pypi/dd/markitdown)
[![Built by AutoGen Team](https://img.shields.io/badge/Built%20by-AutoGen%20Team-blue)](https://github.com/microsoft/autogen)

> [!TIP]
> MarkItDown now offers an MCP (Model Context Protocol) server for integration with LLM applications like Claude Desktop. See [markitdown-mcp](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp) for more information.

> [!IMPORTANT]
> Breaking changes between 0.0.1 to 0.1.0:
> * Dependencies are now organized into optional feature-groups (further details below). Use `pip install 'markitdown[all]'` to have backward-compatible behavior.
> * `convert_stream()` now requires a **binary** file-like object (e.g., a file opened in binary mode, or an `io.BytesIO` object). This is a breaking change from the previous version, where it previously also accepted text file-like objects like `io.StringIO`.
> * The `DocumentConverter` class interface has changed to read from file-like streams rather than file paths. *No temporary files are created anymore*. If you are the maintainer of a plugin or a custom `DocumentConverter`, you likely need to update your code. Otherwise, if you are only using the `MarkItDown` class or CLI (as in the examples below), you should not need to change anything.

MarkItDown is a lightweight Python utility for converting various files to Markdown for use with LLMs and related text analysis pipelines. It is most comparable to [textract](https://github.com/deanmalmgren/textract), but with a focus on preserving important document structure as Markdown (including headings, lists, tables, links, etc.). While the output is often human-readable, it is primarily meant to be consumed by text analysis tools and may not be the best option for high-fidelity document conversion for human readers.

## Supported Formats

MarkItDown currently supports conversion from:

| Format | Notes |
|--------|-------|
| PDF | Text extraction; use `[az-doc-intel]` or `markitdown-ocr` plugin for scanned PDFs |
| PowerPoint (`.pptx`) | Slides, speaker notes, embedded images |
| Word (`.docx`) | Paragraphs, tables, headings |
| Excel (`.xlsx`, `.xls`) | Sheets rendered as Markdown tables |
| Images | EXIF metadata + optional LLM-based OCR/description |
| Audio | EXIF metadata + optional speech transcription |
| HTML | Converts web pages, preserving headings, links, and lists |
| CSV / JSON / XML | Text-based structured formats |
| ZIP archives | Iterates over and converts each entry |
| YouTube URLs | Fetches available video transcripts |
| EPub | E-book text and structure |

## Why Markdown?

Markdown is extremely close to plain text, with minimal markup, but still provides a way to represent important document structure. Mainstream LLMs such as GPT-4o natively "speak" Markdown and often incorporate it into their responses unprompted — suggesting they have been trained on large amounts of Markdown-formatted text and understand it well. As a side benefit, Markdown conventions are also highly token-efficient.

## Prerequisites

MarkItDown requires **Python 3.10 or higher**. It is recommended to use a virtual environment to avoid dependency conflicts.

```bash
# Standard venv
python -m venv .venv
source .venv/bin/activate

# Using uv
uv venv --python=3.12 .venv
source .venv/bin/activate
# NOTE: use 'uv pip install' inside a uv-managed environment

# Using conda
conda create -n markitdown python=3.12
conda activate markitdown
```

## Installation

```bash
# Install with all optional dependencies (recommended)
pip install 'markitdown[all]'

# Install only specific format support
pip install 'markitdown[pdf,docx,pptx]'

# Install from source
git clone git@github.com:microsoft/markitdown.git
cd markitdown
pip install -e 'packages/markitdown[all]'
```

### Optional Dependencies

Install only what you need:

| Extra | Adds support for |
|-------|------------------|
| `[all]` | All optional dependencies |
| `[pptx]` | PowerPoint files |
| `[docx]` | Word files |
| `[xlsx]` | Excel files (`.xlsx`) |
| `[xls]` | Legacy Excel files (`.xls`) |
| `[pdf]` | PDF files |
| `[outlook]` | Outlook `.msg` messages |
| `[az-doc-intel]` | Azure Document Intelligence |
| `[audio-transcription]` | WAV and MP3 transcription |
| `[youtube-transcription]` | YouTube video transcripts |

## Usage

### Command-Line

```bash
# Convert a file and print to stdout
markitdown path-to-file.pdf

# Convert and save to a file
markitdown path-to-file.pdf -o document.md

# Pipe content into markitdown
cat path-to-file.pdf | markitdown

# Use Azure Document Intelligence
markitdown path-to-file.pdf -o document.md -d -e "<document_intelligence_endpoint>"
```

### Python API

#### Basic conversion

```python
from markitdown import MarkItDown

md = MarkItDown(enable_plugins=False)  # Set enable_plugins=True to load installed plugins
result = md.convert("report.xlsx")
print(result.markdown)  # or str(result)
```

#### Convert from a file path

```python
from markitdown import MarkItDown

md = MarkItDown()

# PDF
result = md.convert("paper.pdf")
print(result.markdown)

# Word document
result = md.convert("report.docx")
print(result.markdown)

# PowerPoint presentation
result = md.convert("slides.pptx")
print(result.markdown)

# Web page
result = md.convert("https://en.wikipedia.org/wiki/Markdown")
print(result.markdown)
```

#### Convert from a stream

```python
from markitdown import MarkItDown
import io

md = MarkItDown()

# Binary stream (e.g., downloaded content)
with open("document.pdf", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")
    print(result.markdown)

# BytesIO buffer
bytes_data = b"..."  # some binary content
buf = io.BytesIO(bytes_data)
result = md.convert_stream(buf, file_extension=".pdf")
print(result.markdown)
```

#### Convert a local file by URI

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("file:///absolute/path/to/document.pdf")
print(result.markdown)
```

#### LLM-powered image descriptions

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="Describe the image in detail.",  # optional custom prompt
)
result = md.convert("photo.jpg")
print(result.markdown)
```

#### Azure Document Intelligence

```python
from markitdown import MarkItDown

md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
result = md.convert("scanned.pdf")
print(result.markdown)
```

### Plugins

MarkItDown supports 3rd-party plugins. Plugins are **disabled by default**.

```bash
# List installed plugins
markitdown --list-plugins

# Run with plugins enabled
markitdown --use-plugins path-to-file.pdf
```

To find available plugins, search GitHub for the tag [`#markitdown-plugin`](https://github.com/topics/markitdown-plugin). To develop a plugin, see `packages/markitdown-sample-plugin`.

#### markitdown-ocr Plugin

The `markitdown-ocr` plugin adds OCR support to PDF, DOCX, PPTX, and XLSX converters, extracting text from embedded images using an LLM vision model — the same `llm_client` / `llm_model` pattern that MarkItDown already uses for image descriptions. No new ML libraries or binary dependencies are required.

```bash
pip install markitdown-ocr
pip install openai  # or any OpenAI-compatible client
```

```python
from markitdown import MarkItDown
from openai import OpenAI

md = MarkItDown(
    enable_plugins=True,
    llm_client=OpenAI(),
    llm_model="gpt-4o",
)
result = md.convert("document_with_images.pdf")
print(result.markdown)
```

If no `llm_client` is provided, the plugin still loads but OCR is silently skipped and the standard built-in converter is used instead.

See [`packages/markitdown-ocr/README.md`](packages/markitdown-ocr/README.md) for detailed documentation.

### Docker

```bash
docker build -t markitdown:latest .
docker run --rm -i markitdown:latest < ~/your-file.pdf > output.md
```

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### How to Contribute

You can help by looking at issues or helping review PRs. Any issue or PR is welcome, but we have also marked some as 'open for contribution' and 'open for reviewing' to help facilitate community contributions.

<div align="center">

|            | All                                                          | Especially Needs Help from Community                                                                                                      |
| ---------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Issues** | [All Issues](https://github.com/microsoft/markitdown/issues) | [Issues open for contribution](https://github.com/microsoft/markitdown/issues?q=is%3Aissue+is%3Aopen+label%3A%22open+for+contribution%22) |
| **PRs**    | [All PRs](https://github.com/microsoft/markitdown/pulls)     | [PRs open for reviewing](https://github.com/microsoft/markitdown/pulls?q=is%3Apr+is%3Aopen+label%3A%22open+for+reviewing%22)              |

</div>

### Running Tests and Checks

```bash
# Navigate to the MarkItDown package
cd packages/markitdown

# Install hatch and run tests
pip install hatch  # https://hatch.pypa.io/dev/install/
hatch shell
hatch test

# (Alternative) Use the Devcontainer (all dependencies pre-installed)
hatch test

# Run pre-commit checks before submitting a PR
pre-commit run --all-files
```

### Contributing 3rd-party Plugins

You can also contribute by creating and sharing 3rd-party plugins. See `packages/markitdown-sample-plugin` for more details.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.
