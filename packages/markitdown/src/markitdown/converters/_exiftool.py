import json
import locale
import subprocess
from typing import Any, BinaryIO, Union


def _parse_version(version: str) -> tuple:
    """Parse a dotted version string (e.g. "12.24") into a tuple of ints for comparison."""
    return tuple(map(int, (version.split("."))))


def exiftool_metadata(
    file_stream: BinaryIO,
    *,
    exiftool_path: Union[str, None],
) -> Any:  # Need a better type for json data
    """Extract metadata from ``file_stream`` by shelling out to the ``exiftool`` binary.

    Args:
        file_stream: A binary stream positioned anywhere; its position is restored
            before this function returns.
        exiftool_path: Path to the ``exiftool`` executable. If falsy, no metadata
            extraction is attempted and an empty dict is returned.

    Returns:
        A dict of metadata fields as parsed from exiftool's JSON output, or an
        empty dict if ``exiftool_path`` was not provided.

    Raises:
        RuntimeError: If the exiftool version cannot be determined, or if the
            installed version is older than 12.24 (vulnerable to CVE-2021-22204).
    """
    # Nothing to do
    if not exiftool_path:
        return {}

    # Verify exiftool version
    try:
        version_output = subprocess.run(
            [exiftool_path, "-ver"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        version = _parse_version(version_output)
        min_version = (12, 24)
        if version < min_version:
            raise RuntimeError(
                f"ExifTool version {version_output} is vulnerable to CVE-2021-22204. "
                "Please upgrade to version 12.24 or later."
            )
    except (subprocess.CalledProcessError, ValueError) as e:
        raise RuntimeError("Failed to verify ExifTool version.") from e

    # Run exiftool
    cur_pos = file_stream.tell()
    try:
        output = subprocess.run(
            [exiftool_path, "-json", "-"],
            input=file_stream.read(),
            capture_output=True,
            text=False,
        ).stdout

        return json.loads(
            output.decode(locale.getpreferredencoding(False)),
        )[0]
    finally:
        file_stream.seek(cur_pos)
