"""Internal utility functions for MarkItDown converters.

Not part of the public API — subject to change without notice.
"""

from __future__ import annotations

import re
from typing import Optional


def sanitize_markdown_heading(text: str) -> str:
    """Strip characters that break Markdown headings.

    Args:
        text: Raw heading text extracted from a source document.

    Returns:
        Cleaned text safe to use after a ``#`` prefix.
    """
    text = text.strip()
    text = re.sub(r"[#\[\]<>]", "", text)
    return text.strip() or "Untitled"


def truncate_text(text: str, max_chars: int = 500, ellipsis: str = "…") -> str:
    """Truncate text to a maximum character count.

    Args:
        text: The text to truncate.
        max_chars: Maximum number of characters to return.
        ellipsis: String appended when truncation occurs.

    Returns:
        Truncated (or original) text.
    """
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(None, 1)[0]
    return cut + ellipsis


def normalise_whitespace(text: str) -> str:
    """Collapse runs of whitespace to a single space and strip edges.

    Args:
        text: Input text that may contain tabs, newlines, or multiple spaces.

    Returns:
        Text with all whitespace sequences replaced by a single space.
    """
    return re.sub(r"\s+", " ", text).strip()
