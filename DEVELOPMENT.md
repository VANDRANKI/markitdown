# Development Guide

This document explains how to set up a local development environment for MarkItDown, understand the project structure, and contribute new file format converters.

## Project Structure

MarkItDown is organized as a monorepo under the `packages/` directory:

```
markitdown/
├── packages/
│   └── markitdown/          # Main Python package
│       ├── src/
│       │   └── markitdown/
│       │       ├── __init__.py          # Public API surface
│       │       ├── _markitdown.py       # Core MarkItDown class
│       │       ├── _base_converter.py   # Abstract base for converters
│       │       ├── _stream_info.py      # Stream metadata helpers
│       │       └── converters/          # One file per format
│       │           ├── _pdf.py
│       │           ├── _docx.py
│       │           ├── _pptx.py
│       │           ├── _xlsx.py
│       │           ├── _html.py
│       │           └── ...
│       ├── tests/
│       └── pyproject.toml
├── scripts/                 # Developer utility scripts
├── DEVELOPMENT.md           # This file
└── README.md
```

## Setting Up a Development Environment

### Prerequisites

- Python 3.9 or later
- `pip` or a compatible package manager

### Install in Editable Mode

To install the package along with its development dependencies, run:

```bash
pip install -e "packages/markitdown[dev]"
```

This installs MarkItDown in editable (source-linked) mode, so any changes you make to the source files are immediately reflected without reinstalling.

### Optional: Docker Dev Container

If you prefer an isolated environment, a dev container configuration is available. Open the repository in VS Code and select **Reopen in Container** when prompted. The container pre-installs all dependencies and tools.

## Running Tests

Tests live in `packages/markitdown/tests/`. Run the full suite with:

```bash
cd packages/markitdown
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_markitdown.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=markitdown --cov-report=html
# Open htmlcov/index.html in your browser
```

## Running the CLI

After installing in editable mode, you can invoke MarkItDown from the command line:

```bash
# Convert a file and print to stdout
python -m markitdown path/to/file.pdf

# Convert and write to a file
python -m markitdown path/to/file.docx -o output.md

# Convert from stdin (pipe)
cat file.html | python -m markitdown --stdin -x text/html
```

## Adding a New File Format Converter

Each supported file format has its own converter module under `packages/markitdown/src/markitdown/converters/`. Follow these steps to add support for a new format:

### 1. Create the converter module

Create a new file, e.g., `packages/markitdown/src/markitdown/converters/_myformat.py`:

```python
# SPDX-FileCopyrightText: 2024 Microsoft Corporation
# SPDX-License-Identifier: MIT

from typing import BinaryIO, Any
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

ACCEPTED_MIME_TYPES = ["application/x-myformat"]
ACCEPTED_FILE_EXTENSIONS = [".myfmt"]


class MyFormatConverter(DocumentConverter):
    """Converts .myfmt files to Markdown."""

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()
        return mimetype in ACCEPTED_MIME_TYPES or extension in ACCEPTED_FILE_EXTENSIONS

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        # Parse the file and build a Markdown string
        content = file_stream.read().decode("utf-8")
        markdown = f"# Converted from MyFormat\n\n{content}\n"
        return DocumentConverterResult(markdown=markdown)
```

### 2. Register the converter

Open `packages/markitdown/src/markitdown/_markitdown.py` and add your converter to the default converter list in `MarkItDown.__init__`:

```python
from .converters._myformat import MyFormatConverter

# Inside __init__, alongside the other converters:
self.register_converter(MyFormatConverter())
```

### 3. Add dependencies (if needed)

If the converter requires a third-party library, add it as an optional dependency in `packages/markitdown/pyproject.toml`:

```toml
[project.optional-dependencies]
myformat = ["myformat-library>=1.0"]
```

### 4. Write tests

Add tests in `packages/markitdown/tests/` covering at least:

- A file that converts successfully
- Edge cases (empty file, malformed input)

### 5. Add a sample test file

Place a small sample file (e.g., `packages/markitdown/tests/test_files/test.myfmt`) to support integration tests and the smoke test script.

## Linting and Formatting

The project uses `ruff` for linting and formatting:

```bash
# Check for issues
ruff check packages/

# Auto-fix issues
ruff check --fix packages/

# Format code
ruff format packages/
```

## Releasing

Releases are managed via the `pyproject.toml` version field and GitHub Actions. To prepare a release:

1. Bump the version in `packages/markitdown/pyproject.toml`
2. Update `CHANGELOG.md` if present
3. Open a PR and get it reviewed
4. After merging, tag the commit: `git tag vX.Y.Z && git push --tags`
