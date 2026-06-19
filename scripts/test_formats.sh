#!/usr/bin/env bash
# test_formats.sh — Integration smoke test for MarkItDown format converters.
#
# Usage:
#   ./scripts/test_formats.sh [--sample-dir DIR]
#
# This script attempts to convert one sample file of each supported format and
# checks that the output is non-empty Markdown.  It is intentionally simple —
# for full unit/property tests see packages/markitdown/tests/.
#
# Requires:
#   - Python 3.9+
#   - markitdown installed (e.g. pip install -e "packages/markitdown[all]")
#   - Sample files in SAMPLE_DIR (see below, or pass --sample-dir)

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default location for sample files.  Override with --sample-dir.
SAMPLE_DIR="${REPO_ROOT}/packages/markitdown/tests/test_files"

# ── Argument parsing ──────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sample-dir)
      SAMPLE_DIR="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--sample-dir DIR]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────

PASS=0
FAIL=0
SKIP=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

check_format() {
  local label="$1"    # Human-readable name, e.g. "PDF"
  local filename="$2" # Filename to look for in SAMPLE_DIR

  local filepath="${SAMPLE_DIR}/${filename}"

  if [[ ! -f "${filepath}" ]]; then
    echo -e "  ${YELLOW}SKIP${NC}  ${label} — sample file not found: ${filepath}"
    (( SKIP++ )) || true
    return
  fi

  local output
  if output=$(python -m markitdown "${filepath}" 2>&1); then
    # Check that we got some actual Markdown content (at least 10 chars)
    if [[ ${#output} -lt 10 ]]; then
      echo -e "  ${RED}FAIL${NC}  ${label} — output was too short (${#output} chars)"
      (( FAIL++ )) || true
    else
      echo -e "  ${GREEN}PASS${NC}  ${label} — ${#output} chars of Markdown produced"
      (( PASS++ )) || true
    fi
  else
    echo -e "  ${RED}FAIL${NC}  ${label} — markitdown exited with error:"
    echo "         ${output}"
    (( FAIL++ )) || true
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────

echo ""
echo "MarkItDown Format Smoke Tests"
echo "Sample dir: ${SAMPLE_DIR}"
echo "──────────────────────────────────────────────"

# Check that markitdown is available
if ! python -m markitdown --help &>/dev/null; then
  echo "ERROR: 'python -m markitdown' is not available." >&2
  echo "Install with: pip install -e \"packages/markitdown[all]\"" >&2
  exit 1
fi

# Add or remove entries here as new converters are added.
# Format: check_format "<Label>" "<filename in SAMPLE_DIR>"
check_format "PDF"              "test.pdf"
check_format "DOCX (Word)"     "test.docx"
check_format "PPTX (PowerPoint)" "test.pptx"
check_format "XLSX (Excel)"    "test.xlsx"
check_format "HTML"            "test.html"
check_format "Markdown"        "test.md"
check_format "Plain text"      "test.txt"
check_format "CSV"             "test.csv"
check_format "ZIP"             "test.zip"
check_format "EPUB"            "test.epub"
check_format "WAV (audio)"     "test.wav"
check_format "MP3 (audio)"     "test.mp3"
check_format "JPG (image)"     "test.jpg"
check_format "PNG (image)"     "test.png"

echo "──────────────────────────────────────────────"
echo -e "Results: ${GREEN}${PASS} passed${NC}  ${RED}${FAIL} failed${NC}  ${YELLOW}${SKIP} skipped${NC}"
echo ""

if [[ ${FAIL} -gt 0 ]]; then
  exit 1
fi
