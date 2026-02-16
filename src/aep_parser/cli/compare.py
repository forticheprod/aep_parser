"""
AEP/AEPX File Comparison Tool.

Compares two After Effects project files (.aep or .aepx) and reports differences
at the byte level, including:
- The hierarchical chunk path where the difference occurs
- Byte position and hex values
- If only one bit differs, the bit position (7 to 0 from left to right)

Usage:
    aep-compare file1.aepx file2.aepx
    aep-compare file1.aep file2.aep
    aep-compare file1.aep file2.aep --json
    aep-compare file1.aep file2.aep --filter ldta    aep-compare file1.aep file2.aep --format aepx"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from ..kaitai import Aep


@dataclass
class ByteDifference:
    """Represents a single byte difference between two files."""

    path: str
    offset: int
    byte1: int
    byte2: int
    bit_position: int | None = (
        None  # 7 to 0 from left to right, None if multiple bits differ
    )

    def __post_init__(self) -> None:
        """Calculate bit position if only one bit differs."""
        xor = self.byte1 ^ self.byte2
        if xor != 0 and (xor & (xor - 1)) == 0:  # Check if only one bit is set
            # Find the bit position (7 to 0 from left to right)
            self.bit_position = 7 - (xor.bit_length() - 1)

    def format_diff(self) -> str:
        """Format the difference for display."""
        bit_info = f", bit {self.bit_position}" if self.bit_position is not None else ""
        return (
            f"  Offset {self.offset:4d} (0x{self.offset:04X}): "
            f"0x{self.byte1:02X} ({self.byte1:08b}) vs "
            f"0x{self.byte2:02X} ({self.byte2:08b}){bit_info}"
        )


@dataclass
class ChunkDifference:
    """Represents all differences within a specific chunk/element."""

    path: str
    byte_diffs: list[ByteDifference]
    size1: int
    size2: int

    def has_size_difference(self) -> bool:
        """Check if the chunks have different sizes."""
        return self.size1 != self.size2


def parse_aepx(file_path: Path) -> dict[str, bytes]:
    """
    Parse an AEPX file and extract all bdata elements with their paths.

    Returns a dict mapping element paths to their binary data.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Remove namespace for easier navigation
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    result: dict[str, bytes] = {}
    _extract_bdata_recursive(root, "", result)
    return result


def _extract_bdata_recursive(
    element: ET.Element,
    parent_path: str,
    result: dict[str, bytes],
    counters: dict[str, int] | None = None,
) -> None:
    """Recursively extract bdata from all elements."""
    if counters is None:
        counters = {}

    # Build current path with index for duplicates
    tag = element.tag
    counter_key = parent_path + "/" + tag if parent_path else tag

    if counter_key not in counters:
        counters[counter_key] = 0
    else:
        counters[counter_key] += 1

    if counters[counter_key] > 0:
        current_path = (
            f"{parent_path}/{tag}[{counters[counter_key]}]"
            if parent_path
            else f"{tag}[{counters[counter_key]}]"
        )
    else:
        current_path = f"{parent_path}/{tag}" if parent_path else tag

    # Skip XML metadata elements
    if tag in ("ProjectXMPMetadata", "xmpmeta"):
        return

    # Extract bdata if present
    bdata = element.get("bdata")
    if bdata:
        try:
            binary_data = bytes.fromhex(bdata)
            result[current_path] = binary_data
        except ValueError:
            pass  # Skip invalid hex data

    # Recurse into children
    child_counters: dict[str, int] = {}
    for child in element:
        _extract_bdata_recursive(child, current_path, result, child_counters)


def compare_binary_data(
    data1: bytes, data2: bytes, path: str
) -> Iterator[ByteDifference]:
    """Compare two byte sequences and yield differences."""
    min_len = min(len(data1), len(data2))

    # Compare common bytes
    for i in range(min_len):
        if data1[i] != data2[i]:
            yield ByteDifference(path=path, offset=i, byte1=data1[i], byte2=data2[i])

    # Report extra bytes in longer sequence
    if len(data1) > min_len:
        for i in range(min_len, len(data1)):
            yield ByteDifference(
                path=path,
                offset=i,
                byte1=data1[i],
                byte2=-1,  # -1 indicates missing
            )
    elif len(data2) > min_len:
        for i in range(min_len, len(data2)):
            yield ByteDifference(
                path=path,
                offset=i,
                byte1=-1,
                byte2=data2[i],  # -1 indicates missing
            )


def compare_aepx_files(
    file1: Path, file2: Path
) -> tuple[list[ChunkDifference], list[str], list[str]]:
    """
    Compare two AEPX files and return differences.

    Returns:
        - List of ChunkDifference for chunks that exist in both files
        - List of paths that only exist in file1
        - List of paths that only exist in file2
    """
    data1 = parse_aepx(file1)
    data2 = parse_aepx(file2)

    paths1 = set(data1.keys())
    paths2 = set(data2.keys())

    only_in_file1 = sorted(paths1 - paths2)
    only_in_file2 = sorted(paths2 - paths1)
    common_paths = sorted(paths1 & paths2)

    differences: list[ChunkDifference] = []

    for path in common_paths:
        bytes1 = data1[path]
        bytes2 = data2[path]

        byte_diffs = list(compare_binary_data(bytes1, bytes2, path))

        if byte_diffs or len(bytes1) != len(bytes2):
            differences.append(
                ChunkDifference(
                    path=path,
                    byte_diffs=byte_diffs,
                    size1=len(bytes1),
                    size2=len(bytes2),
                )
            )

    return differences, only_in_file1, only_in_file2


def parse_aep_chunks(file_path: Path) -> dict[str, bytes]:
    """
    Parse an AEP file using Kaitai and extract all chunks with their paths.

    Returns a dict mapping chunk paths to their raw binary data.
    """
    aep = Aep.from_file(str(file_path))
    result: dict[str, bytes] = {}
    _extract_chunks_recursive(aep.data.chunks, "", result)
    return result


def _get_chunk_identifier(chunk: Any) -> str:
    """Get a descriptive identifier for a chunk."""
    chunk_type = str(chunk.chunk_type)

    # For LIST chunks, include the list_type
    if chunk_type == "LIST" and hasattr(chunk, "list_type"):
        return f"LIST:{chunk.list_type}"

    return chunk_type


def _extract_chunks_recursive(
    chunks: list[Any],
    parent_path: str,
    result: dict[str, bytes],
    counters: dict[str, int] | None = None,
) -> None:
    """Recursively extract chunk data with paths."""
    if counters is None:
        counters = {}

    for chunk in chunks:
        identifier = _get_chunk_identifier(chunk)
        counter_key = parent_path + "/" + identifier if parent_path else identifier

        if counter_key not in counters:
            counters[counter_key] = 0
        else:
            counters[counter_key] += 1

        if counters[counter_key] > 0:
            current_path = (
                f"{parent_path}/{identifier}[{counters[counter_key]}]"
                if parent_path
                else f"{identifier}[{counters[counter_key]}]"
            )
        else:
            current_path = f"{parent_path}/{identifier}" if parent_path else identifier

        # Get raw bytes from the chunk's data section
        try:
            raw_data = chunk._raw_data
            if raw_data:
                result[current_path] = raw_data
        except (AttributeError, TypeError):
            pass

        # Recurse into LIST chunks
        if chunk.chunk_type == "LIST" and hasattr(chunk, "chunks") and chunk.chunks:
            child_counters: dict[str, int] = {}
            _extract_chunks_recursive(
                chunk.chunks, current_path, result, child_counters
            )


def compare_aep_files(
    file1: Path, file2: Path
) -> tuple[list[ChunkDifference], list[str], list[str]]:
    """
    Compare two AEP files and return differences.

    Returns:
        - List of ChunkDifference for chunks that exist in both files
        - List of paths that only exist in file1
        - List of paths that only exist in file2
    """
    data1 = parse_aep_chunks(file1)
    data2 = parse_aep_chunks(file2)

    paths1 = set(data1.keys())
    paths2 = set(data2.keys())

    only_in_file1 = sorted(paths1 - paths2)
    only_in_file2 = sorted(paths2 - paths1)
    common_paths = sorted(paths1 & paths2)

    differences: list[ChunkDifference] = []

    for path in common_paths:
        bytes1 = data1[path]
        bytes2 = data2[path]

        byte_diffs = list(compare_binary_data(bytes1, bytes2, path))

        if byte_diffs or len(bytes1) != len(bytes2):
            differences.append(
                ChunkDifference(
                    path=path,
                    byte_diffs=byte_diffs,
                    size1=len(bytes1),
                    size2=len(bytes2),
                )
            )

    return differences, only_in_file1, only_in_file2


def print_results(
    file1: Path,
    file2: Path,
    differences: list[ChunkDifference],
    only_in_file1: list[str],
    only_in_file2: list[str],
) -> None:
    """Print comparison results to stdout."""
    print(f"\n{'=' * 80}")
    print("Comparing:")
    print(f"  File 1: {file1}")
    print(f"  File 2: {file2}")
    print(f"{'=' * 80}\n")

    if not differences and not only_in_file1 and not only_in_file2:
        print("No differences found!")
        return

    # Print chunks only in file1
    if only_in_file1:
        print(f"\n{'─' * 40}")
        print(f"Chunks only in File 1 ({len(only_in_file1)}):")
        print(f"{'─' * 40}")
        for path in only_in_file1:
            print(f"  {path}")

    # Print chunks only in file2
    if only_in_file2:
        print(f"\n{'─' * 40}")
        print(f"Chunks only in File 2 ({len(only_in_file2)}):")
        print(f"{'─' * 40}")
        for path in only_in_file2:
            print(f"  {path}")

    # Print byte differences
    if differences:
        print(f"\n{'─' * 40}")
        print(f"Byte differences ({len(differences)} chunks):")
        print(f"{'─' * 40}")

        for diff in differences:
            print(f"\n[{diff.path}]")
            if diff.has_size_difference():
                print(f"  Size: {diff.size1} bytes vs {diff.size2} bytes")

            for byte_diff in diff.byte_diffs:
                if byte_diff.byte1 == -1:
                    print(
                        f"  Offset {byte_diff.offset:4d} (0x{byte_diff.offset:04X}): "
                        f"<missing> vs 0x{byte_diff.byte2:02X}"
                    )
                elif byte_diff.byte2 == -1:
                    print(
                        f"  Offset {byte_diff.offset:4d} (0x{byte_diff.offset:04X}): "
                        f"0x{byte_diff.byte1:02X} vs <missing>"
                    )
                else:
                    print(byte_diff.format_diff())

    # Summary
    total_byte_diffs = sum(len(d.byte_diffs) for d in differences)
    print(f"\n{'=' * 80}")
    print("Summary:")
    print(f"  Chunks with differences: {len(differences)}")
    print(f"  Total byte differences: {total_byte_diffs}")
    print(f"  Chunks only in File 1: {len(only_in_file1)}")
    print(f"  Chunks only in File 2: {len(only_in_file2)}")
    print(f"{'=' * 80}\n")


def to_json_output(
    file1: Path,
    file2: Path,
    differences: list[ChunkDifference],
    only_in_file1: list[str],
    only_in_file2: list[str],
) -> dict[str, Any]:
    """Convert comparison results to a JSON-serializable dict."""
    return {
        "file1": str(file1),
        "file2": str(file2),
        "chunks_with_differences": [
            {
                "path": diff.path,
                "size1": diff.size1,
                "size2": diff.size2,
                "byte_differences": [
                    {
                        "offset": bd.offset,
                        "offset_hex": f"0x{bd.offset:04X}",
                        "byte1": bd.byte1 if bd.byte1 >= 0 else None,
                        "byte1_hex": f"0x{bd.byte1:02X}" if bd.byte1 >= 0 else None,
                        "byte1_binary": f"{bd.byte1:08b}" if bd.byte1 >= 0 else None,
                        "byte2": bd.byte2 if bd.byte2 >= 0 else None,
                        "byte2_hex": f"0x{bd.byte2:02X}" if bd.byte2 >= 0 else None,
                        "byte2_binary": f"{bd.byte2:08b}" if bd.byte2 >= 0 else None,
                        "bit_position": bd.bit_position,
                    }
                    for bd in diff.byte_diffs
                ],
            }
            for diff in differences
        ],
        "only_in_file1": only_in_file1,
        "only_in_file2": only_in_file2,
        "summary": {
            "chunks_with_differences": len(differences),
            "total_byte_differences": sum(len(d.byte_diffs) for d in differences),
            "only_in_file1": len(only_in_file1),
            "only_in_file2": len(only_in_file2),
        },
    }


def filter_differences(
    differences: list[ChunkDifference],
    only_in_file1: list[str],
    only_in_file2: list[str],
    filter_pattern: str,
) -> tuple[list[ChunkDifference], list[str], list[str]]:
    """Filter results to only include paths matching the pattern."""
    pattern_lower = filter_pattern.lower()
    filtered_diffs = [d for d in differences if pattern_lower in d.path.lower()]
    filtered_only1 = [p for p in only_in_file1 if pattern_lower in p.lower()]
    filtered_only2 = [p for p in only_in_file2 if pattern_lower in p.lower()]
    return filtered_diffs, filtered_only1, filtered_only2


def main() -> int:
    """CLI entry point for aep-compare command."""
    parser = argparse.ArgumentParser(
        prog="aep-compare",
        description="Compare two After Effects project files (.aep or .aepx)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s project1.aepx project2.aepx
    %(prog)s project1.aep project2.aep
    %(prog)s project1.aep project2.aep --json
    %(prog)s project1.aep project2.aep --filter ldta
    %(prog)s project1.aep project2.aep --filter "LIST:Layr"

Output shows for each different byte:
    - The chunk path (hierarchy of elements/chunks)
    - Byte offset (decimal and hex)
    - Byte values (hex and binary)
    - Bit position (7-0) if only one bit differs
        """,
    )
    parser.add_argument("file1", type=Path, help="First AEP/AEPX file")
    parser.add_argument("file2", type=Path, help="Second AEP/AEPX file")
    parser.add_argument(
        "--format",
        choices=["auto", "aep", "aepx"],
        default="auto",
        help="File format (default: auto-detect from extension)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Filter results to only show chunks matching this pattern (case-insensitive)",
    )

    args = parser.parse_args()

    # Validate files exist
    if not args.file1.exists():
        print(f"Error: File not found: {args.file1}", file=sys.stderr)
        return 1
    if not args.file2.exists():
        print(f"Error: File not found: {args.file2}", file=sys.stderr)
        return 1

    # Determine format
    file_format = args.format
    if file_format == "auto":
        ext1 = args.file1.suffix.lower()
        ext2 = args.file2.suffix.lower()
        if ext1 != ext2:
            print(
                f"Error: Files have different extensions ({ext1} vs {ext2}). "
                "Use --format to specify the format.",
                file=sys.stderr,
            )
            return 1
        file_format = "aepx" if ext1 == ".aepx" else "aep"

    # Compare files
    try:
        if file_format == "aepx":
            differences, only_in_file1, only_in_file2 = compare_aepx_files(
                args.file1, args.file2
            )
        else:
            differences, only_in_file1, only_in_file2 = compare_aep_files(
                args.file1, args.file2
            )
    except Exception as e:
        print(f"Error comparing files: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1

    # Apply filter if specified
    if args.filter:
        differences, only_in_file1, only_in_file2 = filter_differences(
            differences, only_in_file1, only_in_file2, args.filter
        )

    # Output results
    if args.json:
        output = to_json_output(
            args.file1, args.file2, differences, only_in_file1, only_in_file2
        )
        print(json.dumps(output, indent=2))
    else:
        print_results(args.file1, args.file2, differences, only_in_file1, only_in_file2)

    return 0 if not differences and not only_in_file1 and not only_in_file2 else 1


if __name__ == "__main__":
    sys.exit(main())
