#!/usr/bin/env python3 -m pytest
"""Tests for the CSV converter's Markdown table generation."""

import io

from markitdown import MarkItDown, StreamInfo

markitdown = MarkItDown()


def _convert_csv(text: str):
    stream_info = StreamInfo(extension=".csv", mimetype="text/csv", charset="utf-8")
    return markitdown.convert_stream(
        io.BytesIO(text.encode("utf-8")), stream_info=stream_info
    )


def test_pipe_character_in_cell_is_escaped():
    """
    Regression test: a literal "|" in CSV data must not be interpreted as
    a Markdown table column separator, or it silently corrupts the table
    structure (extra/misaligned columns).
    """
    csv_text = "Name,Note\nAlice,a | b\n"
    result = _convert_csv(csv_text)

    lines = [line for line in result.markdown.splitlines() if line.strip()]
    # Header, separator, and exactly one data row -- no extra rows
    # introduced by the unescaped pipe.
    assert len(lines) == 3
    # The pipe must be escaped so it isn't read as a column separator.
    assert "a \\| b" in result.markdown
    assert lines[2] == "| Alice | a \\| b |"


def test_embedded_newline_in_quoted_cell_does_not_break_table():
    """
    Regression test: a quoted CSV field containing an embedded newline
    must not turn into a bogus extra Markdown table row.
    """
    csv_text = 'Name,Note\nAlice,"line1\nline2"\n'
    result = _convert_csv(csv_text)

    lines = [line for line in result.markdown.splitlines() if line.strip()]
    assert len(lines) == 3
    assert "line1 line2" in result.markdown
