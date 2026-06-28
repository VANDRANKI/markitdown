# Batch Conversion and Pipeline Patterns

This guide explains how to convert multiple documents efficiently using
MarkItDown and how to compose conversion pipelines.

## 1. Basic batch conversion

```python
from pathlib import Path
from markitdown import MarkItDown

md = MarkItDown()

def convert_directory(input_dir: Path, output_dir: Path) -> None:
    """Convert every supported file in input_dir to Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for file_path in input_dir.iterdir():
        if file_path.suffix in {".pdf", ".docx", ".pptx", ".xlsx", ".html"}:
            result = md.convert(str(file_path))
            if result is not None:
                out_path = output_dir / (file_path.stem + ".md")
                out_path.write_text(result.text_content, encoding="utf-8")
                print(f"Converted: {file_path.name} -> {out_path.name}")
```

## 2. Parallel batch conversion with ThreadPoolExecutor

For large collections, parallelise I/O-bound conversion.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_convert(files: list[Path], output_dir: Path, workers: int = 4) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    md = MarkItDown()  # create once; MarkItDown is thread-safe

    def convert_one(path: Path) -> tuple[Path, bool]:
        try:
            result = md.convert(str(path))
            if result is None:
                return path, False
            out = output_dir / (path.stem + ".md")
            out.write_text(result.text_content, encoding="utf-8")
            return path, True
        except Exception as exc:
            print(f"Error converting {path.name}: {exc}")
            return path, False

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(convert_one, f): f for f in files}
        for future in as_completed(futures):
            path, ok = future.result()
            status = "ok" if ok else "FAILED"
            print(f"[{status}] {path.name}")
```

## 3. Pipeline: convert then post-process

Compose converters with post-processing steps.

```python
from typing import Callable

PostProcessor = Callable[[str], str]

def add_front_matter(source_path: Path) -> PostProcessor:
    """Prepend YAML front matter with file metadata."""
    import datetime
    date = datetime.date.today().isoformat()
    header = f"---\nsource: {source_path.name}\ndate: {date}\n---\n\n"
    return lambda text: header + text

def strip_empty_lines(text: str) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines)

def convert_with_pipeline(
    file_path: Path,
    post_processors: list[PostProcessor],
) -> str:
    result = md.convert(str(file_path))
    if result is None:
        raise ValueError(f"MarkItDown could not convert {file_path}")
    text = result.text_content
    for step in post_processors:
        text = step(text)
    return text

# Usage
markdown = convert_with_pipeline(
    Path("report.pdf"),
    [add_front_matter(Path("report.pdf")), strip_empty_lines],
)
```

## 4. Error handling strategy

```python
from dataclasses import dataclass

@dataclass
class ConversionResult:
    path: Path
    markdown: str | None
    error: str | None

    @property
    def succeeded(self) -> bool:
        return self.markdown is not None

def safe_convert(path: Path) -> ConversionResult:
    try:
        result = md.convert(str(path))
        if result is None:
            return ConversionResult(path, None, "converter returned None")
        return ConversionResult(path, result.text_content, None)
    except Exception as exc:
        return ConversionResult(path, None, str(exc))
```

## Performance tips

- Reuse a single `MarkItDown()` instance across all conversions — it is thread-safe.
- Use `ThreadPoolExecutor` for I/O-heavy workloads (PDF extraction, network URLs).
- For CPU-intensive formats, benchmark `ProcessPoolExecutor` vs threading.
- Write output incrementally using `Path.write_text` inside each worker rather than
  accumulating everything in memory first.
