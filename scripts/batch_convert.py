#!/usr/bin/env python3
"""Batch convert a directory of documents to Markdown using MarkItDown.

Usage::

    python scripts/batch_convert.py --input-dir ./docs --output-dir ./markdown
    python scripts/batch_convert.py --input-dir ./docs --output-dir ./markdown --exts .pdf .docx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def convert_directory(
    input_dir: Path,
    output_dir: Path,
    extensions: list[str],
) -> tuple[int, int]:
    """Convert all matching files in a directory to Markdown.

    Args:
        input_dir: Source directory containing documents.
        output_dir: Destination directory for Markdown output.
        extensions: List of file extensions to process (e.g. ``[".pdf", ".docx"]``).

    Returns:
        Tuple of ``(success_count, failure_count)``.
    """
    try:
        from markitdown import MarkItDown, MarkItDownException
    except ImportError:
        print("ERROR: markitdown is not installed. Run: pip install markitdown", file=sys.stderr)
        sys.exit(1)

    md = MarkItDown()
    output_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    failure = 0

    for src_file in sorted(input_dir.rglob("*")):
        if not src_file.is_file():
            continue
        if src_file.suffix.lower() not in extensions:
            continue

        rel_path = src_file.relative_to(input_dir)
        dest_file = output_dir / rel_path.with_suffix(".md")
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = md.convert(str(src_file))
            dest_file.write_text(result.text_content, encoding="utf-8")
            print(f"  [OK]   {rel_path}")
            success += 1
        except MarkItDownException as exc:
            print(f"  [FAIL] {rel_path}: {exc}")
            failure += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [ERR]  {rel_path}: unexpected error: {exc}")
            failure += 1

    return success, failure


def main() -> None:
    """Entry point for the batch converter script."""
    parser = argparse.ArgumentParser(
        description="Batch convert documents to Markdown using MarkItDown."
    )
    parser.add_argument(
        "--input-dir", required=True, type=Path, help="Source directory."
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Destination directory."
    )
    parser.add_argument(
        "--exts",
        nargs="+",
        default=[".pdf", ".docx", ".pptx", ".xlsx", ".html"],
        help="File extensions to convert (default: .pdf .docx .pptx .xlsx .html).",
    )
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"ERROR: Input directory '{args.input_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    exts = [e if e.startswith(".") else f".{e}" for e in args.exts]
    print(f"Converting files in '{args.input_dir}' with extensions: {exts}")
    success, failure = convert_directory(args.input_dir, args.output_dir, exts)
    print(f"\nDone: {success} succeeded, {failure} failed.")
    sys.exit(0 if failure == 0 else 1)


if __name__ == "__main__":
    main()
