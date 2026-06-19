"""Unit tests for markitdown._utils."""

import pytest
from markitdown._utils import (
    sanitize_markdown_heading,
    truncate_text,
    normalise_whitespace,
)


class TestSanitizeMarkdownHeading:
    def test_strips_leading_hashes(self):
        assert sanitize_markdown_heading("# My Heading") == "My Heading"

    def test_strips_angle_brackets(self):
        assert sanitize_markdown_heading("<script>alert(1)</script>") == "scriptalert(1)/script"

    def test_empty_returns_untitled(self):
        assert sanitize_markdown_heading("   ") == "Untitled"

    def test_plain_text_unchanged(self):
        assert sanitize_markdown_heading("  Hello World  ") == "Hello World"


class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("hello", 10) == "hello"

    def test_truncates_at_word_boundary(self):
        result = truncate_text("one two three four five", max_chars=12)
        assert result.endswith("…")
        assert "four" not in result

    def test_exact_length_unchanged(self):
        text = "a" * 10
        assert truncate_text(text, 10) == text


class TestNormaliseWhitespace:
    def test_collapses_spaces(self):
        assert normalise_whitespace("hello   world") == "hello world"

    def test_collapses_tabs_and_newlines(self):
        assert normalise_whitespace("hello\t\nworld") == "hello world"

    def test_strips_edges(self):
        assert normalise_whitespace("  hello  ") == "hello"
