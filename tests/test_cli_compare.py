"""Tests for CLI compare module.

These tests verify the aep-compare command line tool functionality.
"""

from __future__ import annotations

from pathlib import Path

from aep_parser.cli.compare import (
    ByteDifference,
    ChunkDifference,
    compare_aep_files,
    compare_binary_data,
    filter_differences,
    to_json_output,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


class TestByteDifference:
    """Tests for ByteDifference dataclass."""

    def test_single_bit_difference_detected(self) -> None:
        """Test that single bit differences are detected and position calculated."""
        # Bit 0 differs (0x00 vs 0x01)
        diff = ByteDifference(path="test", offset=0, byte1=0x00, byte2=0x01)
        assert diff.bit_position == 7  # Bit 0 from right = bit 7 from left

    def test_multiple_bit_difference_no_position(self) -> None:
        """Test that multiple bit differences don't have a bit position."""
        # Multiple bits differ (0x00 vs 0xFF)
        diff = ByteDifference(path="test", offset=0, byte1=0x00, byte2=0xFF)
        assert diff.bit_position is None

    def test_format_diff_with_bit_position(self) -> None:
        """Test format_diff output includes bit position when applicable."""
        diff = ByteDifference(path="test", offset=10, byte1=0x80, byte2=0x00)
        formatted = diff.format_diff()
        assert "bit 0" in formatted  # MSB is bit 0
        assert "0x80" in formatted
        assert "0x00" in formatted


class TestCompareBinaryData:
    """Tests for compare_binary_data function."""

    def test_identical_bytes_no_differences(self) -> None:
        """Test that identical byte sequences produce no differences."""
        data = b"\x00\x01\x02\x03"
        diffs = list(compare_binary_data(data, data, "test"))
        assert len(diffs) == 0

    def test_single_byte_difference(self) -> None:
        """Test detection of a single byte difference."""
        data1 = b"\x00\x01\x02\x03"
        data2 = b"\x00\xFF\x02\x03"
        diffs = list(compare_binary_data(data1, data2, "test"))
        assert len(diffs) == 1
        assert diffs[0].offset == 1
        assert diffs[0].byte1 == 0x01
        assert diffs[0].byte2 == 0xFF

    def test_different_lengths_reported(self) -> None:
        """Test that extra bytes in longer sequence are reported."""
        data1 = b"\x00\x01\x02"
        data2 = b"\x00\x01\x02\x03\x04"
        diffs = list(compare_binary_data(data1, data2, "test"))
        assert len(diffs) == 2  # Two extra bytes in data2
        assert diffs[0].offset == 3
        assert diffs[0].byte1 == -1  # Missing in data1
        assert diffs[0].byte2 == 0x03


class TestCompareAepFiles:
    """Tests for compare_aep_files function."""

    def test_identical_files_no_differences(self) -> None:
        """Test that comparing a file with itself produces no differences."""
        aep_path = SAMPLES_DIR / "versions" / "ae2025" / "complete.aep"

        differences, only_in_file1, only_in_file2 = compare_aep_files(
            aep_path, aep_path
        )
        assert len(differences) == 0
        assert len(only_in_file1) == 0
        assert len(only_in_file2) == 0

    def test_different_files_detected(self) -> None:
        """Test that different files produce differences."""
        file1 = SAMPLES_DIR / "models" / "layer" / "enabled_false.aep"
        file2 = SAMPLES_DIR / "models" / "layer" / "locked_true.aep"

        differences, only_in_file1, only_in_file2 = compare_aep_files(file1, file2)
        # Files are different, so we expect some differences
        total_diffs = len(differences) + len(only_in_file1) + len(only_in_file2)
        assert total_diffs > 0


class TestFilterDifferences:
    """Tests for filter_differences function."""

    def test_filter_matches_pattern(self) -> None:
        """Test that filter correctly matches patterns."""
        diff1 = ChunkDifference(path="LIST:Layr/ldta", byte_diffs=[], size1=10, size2=10)
        diff2 = ChunkDifference(path="LIST:Comp/cdta", byte_diffs=[], size1=10, size2=10)
        differences = [diff1, diff2]

        filtered, _, _ = filter_differences(differences, [], [], "ldta")
        assert len(filtered) == 1
        assert filtered[0].path == "LIST:Layr/ldta"

    def test_filter_case_insensitive(self) -> None:
        """Test that filter is case-insensitive."""
        diff = ChunkDifference(path="LIST:Layr/LDTA", byte_diffs=[], size1=10, size2=10)
        filtered, _, _ = filter_differences([diff], [], [], "ldta")
        assert len(filtered) == 1


class TestToJsonOutput:
    """Tests for to_json_output function."""

    def test_json_output_structure(self) -> None:
        """Test that JSON output has expected structure."""
        diff = ChunkDifference(
            path="test/path",
            byte_diffs=[ByteDifference(path="test", offset=0, byte1=0x00, byte2=0x01)],
            size1=10,
            size2=10,
        )
        output = to_json_output(
            Path("file1.aep"),
            Path("file2.aep"),
            [diff],
            ["only1"],
            ["only2"],
        )
        assert "file1" in output
        assert "file2" in output
        assert "chunks_with_differences" in output
        assert "only_in_file1" in output
        assert "only_in_file2" in output
        assert "summary" in output
        assert output["summary"]["chunks_with_differences"] == 1
        assert output["summary"]["total_byte_differences"] == 1
