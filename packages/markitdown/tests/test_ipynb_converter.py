#!/usr/bin/env python3 -m pytest
"""Tests for the Jupyter Notebook (.ipynb) converter's title extraction."""

from markitdown.converters._ipynb_converter import IpynbConverter


def _notebook_with_markdown_cell(source_lines):
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "source": source_lines,
            }
        ],
    }


def test_title_extraction_strips_only_heading_marker():
    """A plain heading should have just the '# ' marker removed."""
    notebook = _notebook_with_markdown_cell(["# Test Notebook"])
    result = IpynbConverter()._convert(notebook)
    assert result.title == "Test Notebook"


def test_title_extraction_does_not_mangle_leading_hash_in_title():
    """
    Regression test: title text that itself starts with '#' or extra
    spaces must not be corrupted by a naive lstrip("# ") call, which
    strips *any* leading '#'/' ' characters rather than just the
    two-character heading marker.
    """
    notebook = _notebook_with_markdown_cell(["# #1 Trending"])
    result = IpynbConverter()._convert(notebook)
    assert result.title == "#1 Trending"


def test_title_extraction_does_not_mangle_leading_spaces_in_title():
    notebook = _notebook_with_markdown_cell(["#    Spacey Title"])
    result = IpynbConverter()._convert(notebook)
    assert result.title == "Spacey Title"
