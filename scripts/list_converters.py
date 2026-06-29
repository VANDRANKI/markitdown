#!/usr/bin/env python3
"""List all DocumentConverters registered with MarkItDown.

Instantiates MarkItDown with all options off, then prints each
converter class name and the file extensions it accepts (when
discoverable via the accepts() or _extensions attribute).

Usage:
    python scripts/list_converters.py
    python scripts/list_converters.py --all       # enable plugins too
    python scripts/list_converters.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_markitdown(enable_plugins: bool = False):
    """Import and return a MarkItDown instance."""
    try:
        from markitdown import MarkItDown
    except ImportError:
        print(
            "ERROR: markitdown is not installed.\n"
            "Install with: pip install markitdown",
            file=sys.stderr,
        )
        sys.exit(1)
    return MarkItDown(enable_plugins=enable_plugins)


def get_converter_info(converter) -> dict:
    """Extract name and extension hints from a converter instance."""
    name = type(converter).__name__
    # Try common patterns for extension introspection
    extensions: list[str] = []
    for attr in ("_supported_extensions", "SUPPORTED_EXTENSIONS", "extensions"):
        val = getattr(converter, attr, None)
        if isinstance(val, (list, tuple, set, frozenset)):
            extensions = sorted(str(e).lower() for e in val)
            break
    return {"name": name, "extensions": extensions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all", dest="enable_plugins", action="store_true",
        help="Enable plugins when instantiating MarkItDown",
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args(argv)

    md = load_markitdown(enable_plugins=args.enable_plugins)

    # MarkItDown stores converters in _converters (list) as of 0.1.x
    converters = getattr(md, "_converters", []) or []
    if not converters:
        print("No converters found (MarkItDown API may have changed).")
        return 1

    records = [get_converter_info(c) for c in converters]

    if args.as_json:
        print(json.dumps(records, indent=2))
        return 0

    print(f"Registered converters ({len(records)} total):\n")
    for record in records:
        ext_str = ", ".join(record["extensions"]) if record["extensions"] else "(extensions not exposed)"
        print(f"  {record['name']:45s} {ext_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
