"""Tests for CLI validate module.

These tests verify the aep-validate command line tool functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pytest

from aep_parser.cli.validate import (
    ValidationResult,
    compare_layer,
    compare_marker,
    compare_project_level,
    compare_values,
    get_enum_value,
    main,
    to_dict,
    validate_aep,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


class TestToDict:
    """Tests for to_dict function."""

    def test_converts_dataclass_to_dict(self) -> None:
        """Test that dataclasses are converted to dicts."""

        @dataclass
        class TestClass:
            name: str
            value: int

        obj = TestClass(name="test", value=42)
        result = to_dict(obj)
        assert result == {"name": "test", "value": 42}

    def test_converts_enum_to_name(self) -> None:
        """Test that enums are converted to their name string."""

        class TestEnum(Enum):
            VALUE_A = 1
            VALUE_B = 2

        result = to_dict(TestEnum.VALUE_A)
        assert result == "VALUE_A"

    def test_converts_nested_dataclass(self) -> None:
        """Test that nested dataclasses are converted recursively."""

        @dataclass
        class Inner:
            value: int

        @dataclass
        class Outer:
            inner: Inner
            name: str

        obj = Outer(inner=Inner(value=10), name="outer")
        result = to_dict(obj)
        assert result == {"inner": {"value": 10}, "name": "outer"}

    def test_converts_list_of_dataclasses(self) -> None:
        """Test that lists of dataclasses are converted."""

        @dataclass
        class Item:
            id: int

        items = [Item(id=1), Item(id=2), Item(id=3)]
        result = to_dict(items)
        assert result == [{"id": 1}, {"id": 2}, {"id": 3}]

    def test_preserves_simple_values(self) -> None:
        """Test that simple values pass through unchanged."""
        assert to_dict(42) == 42
        assert to_dict("hello") == "hello"
        assert to_dict(3.14) == 3.14
        assert to_dict(True) is True
        assert to_dict(None) is None


class TestGetEnumValue:
    """Tests for get_enum_value function."""

    def test_returns_enum_name(self) -> None:
        """Test that enum values return their name."""

        class TestEnum(Enum):
            MY_VALUE = 1

        assert get_enum_value(TestEnum.MY_VALUE) == "MY_VALUE"

    def test_returns_non_enum_unchanged(self) -> None:
        """Test that non-enum values pass through unchanged."""
        assert get_enum_value(42) == 42
        assert get_enum_value("string") == "string"
        assert get_enum_value(None) is None


class TestCompareValues:
    """Tests for compare_values function."""

    def test_equal_integers(self) -> None:
        """Test comparison of equal integers."""
        assert compare_values(10, 10) is True

    def test_unequal_integers(self) -> None:
        """Test comparison of unequal integers."""
        assert compare_values(10, 20) is False

    def test_equal_floats_within_tolerance(self) -> None:
        """Test that floats within tolerance are considered equal."""
        assert compare_values(1.0, 1.0005) is True
        assert compare_values(1.0, 1.0005, tolerance=0.001) is True

    def test_unequal_floats_outside_tolerance(self) -> None:
        """Test that floats outside tolerance are considered unequal."""
        assert compare_values(1.0, 1.01, tolerance=0.001) is False

    def test_equal_strings(self) -> None:
        """Test comparison of equal strings."""
        assert compare_values("hello", "hello") is True

    def test_unequal_strings(self) -> None:
        """Test comparison of unequal strings."""
        assert compare_values("hello", "world") is False

    def test_equal_booleans(self) -> None:
        """Test comparison of booleans."""
        assert compare_values(True, True) is True
        assert compare_values(False, False) is True
        assert compare_values(True, False) is False

    def test_both_none(self) -> None:
        """Test that two None values are equal."""
        assert compare_values(None, None) is True

    def test_one_none(self) -> None:
        """Test that None and a value are unequal."""
        assert compare_values(None, 10) is False
        assert compare_values(10, None) is False

    def test_equal_lists(self) -> None:
        """Test comparison of equal lists."""
        assert compare_values([1, 2, 3], [1, 2, 3]) is True

    def test_unequal_lists_values(self) -> None:
        """Test comparison of lists with different values."""
        assert compare_values([1, 2, 3], [1, 2, 4]) is False

    def test_unequal_lists_length(self) -> None:
        """Test comparison of lists with different lengths."""
        assert compare_values([1, 2], [1, 2, 3]) is False

    def test_nested_lists_with_floats(self) -> None:
        """Test comparison of nested lists with floats."""
        assert compare_values([1.0, [2.0, 3.0]], [1.0, [2.0005, 3.0]]) is True


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_initial_state(self) -> None:
        """Test that ValidationResult initializes with empty collections."""
        result = ValidationResult()
        assert len(result) == 0
        assert result.differences == []
        assert result.warnings == []
        assert result.categories == {}

    def test_add_diff(self) -> None:
        """Test adding a difference."""
        result = ValidationResult()
        result.add_diff("path.to.value", "expected", "actual", "test_category")

        assert len(result) == 1
        assert "path.to.value" in result.differences[0]
        assert "'expected'" in result.differences[0]
        assert "'actual'" in result.differences[0]
        assert result.categories["test_category"] == 1

    def test_add_multiple_diffs_same_category(self) -> None:
        """Test adding multiple differences in same category."""
        result = ValidationResult()
        result.add_diff("path1", "e1", "a1", "cat1")
        result.add_diff("path2", "e2", "a2", "cat1")

        assert len(result) == 2
        assert result.categories["cat1"] == 2

    def test_add_diffs_different_categories(self) -> None:
        """Test adding differences in different categories."""
        result = ValidationResult()
        result.add_diff("path1", "e1", "a1", "cat1")
        result.add_diff("path2", "e2", "a2", "cat2")

        assert len(result) == 2
        assert result.categories["cat1"] == 1
        assert result.categories["cat2"] == 1

    def test_add_warning(self) -> None:
        """Test adding a warning."""
        result = ValidationResult()
        result.add_warning("This is a warning")

        assert len(result.warnings) == 1
        assert result.warnings[0] == "This is a warning"


class TestCompareProjectLevel:
    """Tests for compare_project_level function."""

    def test_matching_values(self) -> None:
        """Test that matching values produce no differences."""
        expected = {"bitsPerChannel": 8, "expressionEngine": "javascript-1.0"}
        parsed = {"bits_per_channel": 8, "expression_engine": "javascript-1.0"}
        result = ValidationResult()

        compare_project_level(expected, parsed, result)

        assert len(result) == 0

    def test_differing_values(self) -> None:
        """Test that differing values are recorded."""
        expected = {"bitsPerChannel": 16}
        parsed = {"bits_per_channel": 8}
        result = ValidationResult()

        compare_project_level(expected, parsed, result)

        assert len(result) == 1
        assert result.categories.get("project") == 1

    def test_undefined_values_skipped(self) -> None:
        """Test that undefined values are skipped."""
        expected = {"bitsPerChannel": {"_undefined": True}}
        parsed = {"bits_per_channel": 8}
        result = ValidationResult()

        compare_project_level(expected, parsed, result)

        assert len(result) == 0


class TestCompareMarker:
    """Tests for compare_marker function."""

    def test_matching_marker(self) -> None:
        """Test that matching markers produce no differences."""
        expected_marker = {
            "time": 1.0,
            "comment": "Test marker",
            "duration": 0.0,
        }
        parsed_marker = {
            "frame_time": 24,  # 1.0 second at 24fps
            "comment": "Test marker",
            "duration": 0.0,
        }
        result = ValidationResult()

        compare_marker(expected_marker, parsed_marker, "markers[0]", 24.0, result)

        assert len(result) == 0

    def test_differing_comment(self) -> None:
        """Test that differing comments are recorded."""
        expected_marker = {"comment": "Expected"}
        parsed_marker = {"comment": "Actual"}
        result = ValidationResult()

        compare_marker(expected_marker, parsed_marker, "markers[0]", 24.0, result)

        assert len(result) == 1
        assert result.categories.get("markers") == 1

    def test_time_mismatch(self) -> None:
        """Test that time mismatches are recorded."""
        expected_marker = {"time": 2.0}
        parsed_marker = {"frame_time": 24}  # 1.0 second at 24fps
        result = ValidationResult()

        compare_marker(expected_marker, parsed_marker, "markers[0]", 24.0, result)

        assert len(result) == 1


class TestCompareLayer:
    """Tests for compare_layer function."""

    def test_matching_layer(self) -> None:
        """Test that matching layers produce no differences."""
        expected = {
            "name": "Layer 1",
            "id": 1,
            "enabled": True,
            "inPoint": 0.0,
            "outPoint": 10.0,
        }
        parsed = {
            "name": "Layer 1",
            "id": 1,
            "enabled": True,
            "in_point": 0.0,
            "out_point": 10.0,
        }
        result = ValidationResult()

        compare_layer(expected, parsed, "layers[0]", 60.0, result)

        assert len(result) == 0

    def test_differing_enabled(self) -> None:
        """Test that differing enabled state is recorded."""
        expected = {"enabled": True}
        parsed = {"enabled": False}
        result = ValidationResult()

        compare_layer(expected, parsed, "layers[0]", 60.0, result)

        assert len(result) == 1
        assert result.categories.get("layers") == 1

    def test_differing_name(self) -> None:
        """Test that differing names are recorded."""
        expected = {"name": "Expected Name"}
        parsed = {"name": "Actual Name"}
        result = ValidationResult()

        compare_layer(expected, parsed, "layers[0]", 60.0, result)

        assert len(result) == 1


class TestValidateAep:
    """Tests for validate_aep function with real files."""

    def test_validate_existing_sample(self) -> None:
        """Test validation with an existing sample file and its JSON."""
        # Look for any sample that has both .aep and .json
        aep_path = SAMPLES_DIR / "versions" / "ae2025" / "complete.aep"
        json_path = aep_path.with_suffix(".json")

        if not aep_path.exists():
            pytest.skip("ae2025 sample not available")
        if not json_path.exists():
            pytest.skip("ae2025 JSON export not available")

        result = validate_aep(aep_path, json_path, verbose=False)

        # Just check that it runs without error
        assert isinstance(result, ValidationResult)


class TestMain:
    """Tests for main CLI entry point."""

    def test_missing_aep_file(self, tmp_path: Path) -> None:
        """Test error when AEP file doesn't exist."""
        json_file = tmp_path / "test.json"
        json_file.write_text("{}")

        exit_code = main([str(tmp_path / "nonexistent.aep"), str(json_file)])

        assert exit_code == 1

    def test_missing_json_file(self, tmp_path: Path) -> None:
        """Test error when JSON file doesn't exist."""
        aep_file = tmp_path / "test.aep"
        aep_file.write_bytes(b"RIFX")  # Minimal fake AEP

        exit_code = main([str(aep_file), str(tmp_path / "nonexistent.json")])

        assert exit_code == 1

    def test_with_verbose_flag(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that verbose flag produces additional output."""
        aep_path = SAMPLES_DIR / "versions" / "ae2025" / "complete.aep"
        json_path = aep_path.with_suffix(".json")

        if not aep_path.exists() or not json_path.exists():
            pytest.skip("ae2025 sample with JSON not available")

        main([str(aep_path), str(json_path), "--verbose"])

        captured = capsys.readouterr()
        assert "Comparing" in captured.out or "Parsing" in captured.out

    def test_with_category_filter(self, tmp_path: Path) -> None:
        """Test that category filter argument is accepted."""
        aep_path = SAMPLES_DIR / "versions" / "ae2025" / "complete.aep"
        json_path = aep_path.with_suffix(".json")

        if not aep_path.exists() or not json_path.exists():
            pytest.skip("ae2025 sample with JSON not available")

        # Should not raise an error with valid category
        exit_code = main([str(aep_path), str(json_path), "-c", "layers"])

        # Exit code depends on whether there are differences
        assert exit_code in (0, 1)
