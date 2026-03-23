#!/usr/bin/env python
"""Generate the output color space UID-to-name mapping from ICC profiles.

Scans directories containing ICC/ICM files and computes the ICC Profile ID
(per ISO 15076-1 §7.2.18) for each profile.  The UID is
`MD5(icc_data)` with bytes 44-47, 64-67 and 84-99 zeroed before hashing.

This is the algorithm Adobe After Effects uses internally to identify
output color space profiles stored in the `output_profile_id` field of
output-module `ldat` chunks.

Note: Two profiles (`* wsRGB` and `* wscRGB`) are WCS (Windows Color
System) CDMP profiles for which Adobe Color Engine generates ICC wrappers
at runtime.  They have no ICC files on disk and will not be found by this
script.  `e-sRGB` is also a WCS CDMP profile but Adobe ships an ICC
version in ACE.dll.

Usage (Windows)::

    python scripts/generate_color_space_mapping.py

Usage with custom directories::

    python scripts/generate_color_space_mapping.py ^
        "C:\\Program Files (x86)\\Common Files\\Adobe\\Color\\MPProfiles" ^
        "C:\\Program Files (x86)\\Common Files\\Adobe\\Color\\Profiles\\Recommended"

Usage (macOS)::

    python scripts/generate_color_space_mapping.py \\
        "/Library/Application Support/Adobe/Color/MPProfiles" \\
        "/Library/Application Support/Adobe/Color/Profiles/Recommended"

Output is a Python dict literal that can be pasted into
`src/aep_parser/parsers/mappings.py`.
"""

from __future__ import annotations

import hashlib
import platform
import sys
from pathlib import Path


def icc_profile_id(data: bytes) -> str:
    """Compute the ICC Profile ID (MD5) per ISO 15076-1 §7.2.18.

    The hash is computed over the entire ICC profile with bytes 44-47
    (profile flags), 64-67 (rendering intent) and 84-99 (profile ID)
    zeroed out.

    Args:
        data: Raw ICC profile bytes.

    Returns:
        The 32-character lowercase hex digest.
    """
    buf = bytearray(data)
    buf[44:48] = b"\x00" * 4
    buf[64:68] = b"\x00" * 4
    buf[84:100] = b"\x00" * 16
    return hashlib.md5(bytes(buf)).hexdigest()


def icc_profile_description(data: bytes) -> str | None:
    """Extract the `desc` tag text from an ICC profile.

    Supports both ICCv2 `textDescriptionType` and ICCv4
    `multiLocalizedUnicodeType` tag formats.

    Args:
        data: Raw ICC profile bytes.

    Returns:
        The profile description string, or `None` if not found.
    """
    if len(data) < 132:
        return None
    tag_count = int.from_bytes(data[128:132], "big")
    offset = 132
    for _ in range(tag_count):
        if offset + 12 > len(data):
            return None
        sig = data[offset : offset + 4]
        tag_offset = int.from_bytes(data[offset + 4 : offset + 8], "big")
        if sig == b"desc":
            if tag_offset + 12 > len(data):
                return None
            type_sig = data[tag_offset : tag_offset + 4]
            if type_sig == b"desc":
                # ICCv2 textDescriptionType
                str_len = int.from_bytes(
                    data[tag_offset + 8 : tag_offset + 12], "big"
                )
                end = min(tag_offset + 12 + str_len, len(data))
                raw = data[tag_offset + 12 : end]
                return raw.rstrip(b"\x00").decode("ascii", errors="replace")
            if type_sig == b"mluc":
                # ICCv4 multiLocalizedUnicodeType
                if tag_offset + 16 > len(data):
                    return None
                rec_count = int.from_bytes(
                    data[tag_offset + 8 : tag_offset + 12], "big"
                )
                if rec_count == 0:
                    return None
                rec_off = tag_offset + 16
                s_len = int.from_bytes(
                    data[rec_off + 4 : rec_off + 8], "big"
                )
                s_offset = int.from_bytes(
                    data[rec_off + 8 : rec_off + 12], "big"
                )
                abs_off = tag_offset + s_offset
                end = min(abs_off + s_len, len(data))
                return (
                    data[abs_off:end]
                    .decode("utf-16-be", errors="replace")
                    .rstrip("\x00")
                )
        offset += 12
    return None


def _default_directories() -> list[Path]:
    """Return platform-specific default Adobe ICC profile directories."""
    if platform.system() == "Windows":
        base = Path(
            r"C:\Program Files (x86)\Common Files\Adobe\Color"
        )
        return [
            base / "MPProfiles",
            base / "Profiles",
            base / "Profiles" / "Recommended",
        ]
    # macOS
    base = Path("/Library/Application Support/Adobe/Color")
    return [
        base / "MPProfiles",
        base / "Profiles",
        base / "Profiles" / "Recommended",
    ]


def scan_icc_directories(
    directories: list[Path],
) -> dict[str, str]:
    """Scan directories for ICC/ICM files and build a UID-to-name mapping.

    Args:
        directories: Directories to scan (non-recursive).

    Returns:
        Dict mapping 32-char hex profile IDs to description strings,
        sorted alphabetically by description.
    """
    result: dict[str, str] = {}
    for directory in directories:
        if not directory.is_dir():
            print(f"  Skipping (not found): {directory}", file=sys.stderr)
            continue
        print(f"  Scanning: {directory}", file=sys.stderr)
        for f in sorted(directory.iterdir()):
            if f.suffix.lower() not in (".icc", ".icm"):
                continue
            try:
                data = f.read_bytes()
            except OSError as e:
                print(f"    Error reading {f.name}: {e}", file=sys.stderr)
                continue
            if len(data) < 132:
                continue
            pid = icc_profile_id(data)
            desc = icc_profile_description(data)
            if desc:
                if pid in result and result[pid] != desc:
                    print(
                        f"    Duplicate UID {pid}: "
                        f"{result[pid]!r} vs {desc!r} ({f.name})",
                        file=sys.stderr,
                    )
                result[pid] = desc
    # Sort by description for readability
    return dict(sorted(result.items(), key=lambda kv: kv[1]))


def format_mapping(mapping: dict[str, str]) -> str:
    """Format the mapping as a Python dict literal.

    Args:
        mapping: UID-to-name dict.

    Returns:
        Python source code for the dict.
    """
    lines = ["_ADOBE_OUTPUT_COLOR_SPACE_PROFILES: dict[str, str] = {"]
    for uid, name in mapping.items():
        lines.append(f'    "{uid}": "{name}",')
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    """Entry point."""
    if len(sys.argv) > 1:
        directories = [Path(d) for d in sys.argv[1:]]
    else:
        directories = _default_directories()

    print(
        f"Scanning {len(directories)} directories for ICC profiles...",
        file=sys.stderr,
    )
    mapping = scan_icc_directories(directories)
    print(
        f"\nFound {len(mapping)} profiles.\n",
        file=sys.stderr,
    )
    print(format_mapping(mapping))
    return 0


if __name__ == "__main__":
    sys.exit(main())
