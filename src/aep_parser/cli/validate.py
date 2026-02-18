"""
AEP Parser Validation Tool.

Compares parsed AEP values against expected JSON values (from ExtendScript export)
to validate parsing correctness.

Usage:
    aep-validate project.aep expected.json
    aep-validate project.aep expected.json --verbose
    aep-validate project.aep expected.json --category layers
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from aep_parser import parse

# Fields to skip to avoid circular references.
# Back-references: containing_comp, parent_folder, parent (OutputModule),
#   _parent (Layer).
# Cross-references that re-enter the object graph: _source (AVLayer → Item),
#   comp (RenderQueueItem → CompItem),
#   post_render_target_comp (OutputModule → CompItem).
# The non-circular ID fields (source_id, parent_id) are still serialized.
SKIP_FIELDS = {
    "containing_comp",
    "parent_folder",
    "_parent",
    "_source",
    "parent",
    "comp",
    "post_render_target_comp",
}

# @property attributes that return complex/duplicate data and should not be
# included in to_dict() serialization.
SKIP_PROPERTIES = {
    "composition_layers",
    "footage_layers",
    "footage_missing",
    "missing_footage_path",
    "selected_layers",
    # Circular: AVLayer.source → Item → layers → AVLayer…
    "source",
    # Circular: AVItem.used_in → list[CompItem] → layers → source → AVItem…
    "used_in",
    # Duplicate/circular: Project re-serialises items already in `items` field
    "compositions",
    "folders",
    "footages",
}


def to_dict(obj: Any) -> Any:
    """Convert dataclass/enum to dict recursively, skipping circular reference fields."""
    if is_dataclass(obj) and not isinstance(obj, type):
        result = {}
        for field in fields(obj):
            if field.name in SKIP_FIELDS:
                continue
            value = getattr(obj, field.name)
            result[field.name] = to_dict(value)
        # Include @property attributes (non-private, non-skipped)
        for name in dir(type(obj)):
            if name.startswith("_") or name in SKIP_FIELDS or name in SKIP_PROPERTIES:
                continue
            if name in result:
                continue
            attr = getattr(type(obj), name, None)
            if isinstance(attr, property):
                try:
                    value = getattr(obj, name)
                    result[name] = to_dict(value)
                except Exception:
                    pass
        return result
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj


def get_enum_value(val: Any) -> Any:
    """Get enum value as int if it's an IntEnum, else return as-is."""
    if isinstance(val, Enum):
        return val.value
    return val


def compare_values(expected: Any, parsed: Any, tolerance: float = 0.001) -> bool:
    """
    Compare two values with tolerance for floats.

    Args:
        expected: Expected value from ExtendScript JSON.
        parsed: Parsed value from aep_parser.
        tolerance: Float comparison tolerance.

    Returns:
        True if values match.
    """
    if expected is None and parsed is None:
        return True
    if expected is None or parsed is None:
        return False
    if isinstance(expected, bool) and isinstance(parsed, bool):
        return expected == parsed
    if isinstance(expected, (int, float)) and isinstance(parsed, (int, float)):
        return math.isclose(expected, parsed, rel_tol=tolerance, abs_tol=tolerance)
    if isinstance(expected, str) and isinstance(parsed, str):
        return expected == parsed
    if isinstance(expected, list) and isinstance(parsed, list):
        if len(expected) != len(parsed):
            return False
        return all(compare_values(e, p, tolerance) for e, p in zip(expected, parsed))
    return expected == parsed


class ValidationResult:
    """Stores validation results."""

    def __init__(self) -> None:
        self.differences: list[str] = []
        self.warnings: list[str] = []
        self.categories: dict[str, int] = {}

    def add_diff(
        self, path: str, expected: Any, parsed: Any, category: str = "other"
    ) -> None:
        """Add a difference."""
        self.differences.append(f"{path}: expected {expected!r}, got {parsed!r}")
        self.categories[category] = self.categories.get(category, 0) + 1

    def add_warning(self, message: str) -> None:
        """Add a warning."""
        self.warnings.append(message)

    def __len__(self) -> int:
        return len(self.differences)


def compare_project_level(
    expected: dict[str, Any], parsed: dict[str, Any], result: ValidationResult
) -> None:
    """Compare project-level properties."""
    mappings = {
        "bitsPerChannel": "bits_per_channel",
        "transparencyGridThumbnails": "transparency_grid_thumbnails",
        "displayStartFrame": "display_start_frame",
        "framesCountType": "frames_count_type",
        "feetFramesFilmType": "feet_frames_film_type",
        "framesUseFeetFrames": "frames_use_feet_frames",
        "timeDisplayType": "time_display_type",
        "footageTimecodeDisplayStartType": "footage_timecode_display_start_type",
        "expressionEngine": "expression_engine",
    }

    for exp_key, parsed_key in mappings.items():
        if exp_key in expected:
            exp_val = expected[exp_key]
            if isinstance(exp_val, dict) and exp_val.get("_undefined"):
                continue
            parsed_val = get_enum_value(parsed.get(parsed_key))
            if not compare_values(exp_val, parsed_val):
                result.add_diff(f"Project.{exp_key}", exp_val, parsed_val, "project")


def compare_marker(
    expected_marker: dict[str, Any],
    parsed_marker: dict[str, Any],
    path: str,
    frame_rate: float,
    result: ValidationResult,
) -> None:
    """Compare marker properties."""
    # Calculate time from frame_time if available
    parsed_time = None
    if parsed_marker.get("frame_time") is not None:
        parsed_time = parsed_marker["frame_time"] / frame_rate

    # Compare time
    if "time" in expected_marker:
        exp_val = expected_marker["time"]
        if not isinstance(exp_val, dict) or not exp_val.get("_undefined"):
            if not compare_values(exp_val, parsed_time):
                result.add_diff(f"{path}.time", exp_val, parsed_time, "markers")

    marker_mappings = {
        "comment": "comment",
        "chapter": "chapter",
        "url": "url",
        "duration": "duration",
    }

    for exp_key, parsed_key in marker_mappings.items():
        if exp_key in expected_marker:
            exp_val = expected_marker[exp_key]
            if isinstance(exp_val, dict) and exp_val.get("_undefined"):
                continue
            parsed_val = parsed_marker.get(parsed_key)
            if not compare_values(exp_val, parsed_val):
                result.add_diff(f"{path}.{exp_key}", exp_val, parsed_val, "markers")


def compare_layer(
    expected_layer: dict[str, Any],
    parsed_layer: dict[str, Any],
    path: str,
    comp_duration: float,
    result: ValidationResult,
) -> None:
    """Compare layer properties."""
    layer_mappings = {
        "name": "name",
        "id": "id",
        "comment": "comment",
        "enabled": "enabled",
        "inPoint": "in_point",
        "outPoint": "out_point",
        "startTime": "start_time",
        "stretch": "stretch",
        "label": "label",
        "locked": "locked",
        "nullLayer": "null_layer",
        "shy": "shy",
        "solo": "solo",
        "isNameSet": "is_name_set",
        # AVLayer specific
        "adjustmentLayer": "adjustment_layer",
        "audioEnabled": "audio_enabled",
        "blendingMode": "blending_mode",
        "collapseTransformation": "collapse_transformation",
        "effectsActive": "effects_active",
        "environmentLayer": "environment_layer",
        "frameBlending": "frame_blending",
        "frameBlendingType": "frame_blending_type",
        "guideLayer": "guide_layer",
        "height": "height",
        "width": "width",
        "motionBlur": "motion_blur",
        "preserveTransparency": "preserve_transparency",
        "quality": "quality",
        "samplingQuality": "sampling_quality",
        "threeDLayer": "three_d_layer",
        "timeRemapEnabled": "time_remap_enabled",
        "trackMatteType": "track_matte_type",
        "sourceId": "_source_id",
    }

    for exp_key, parsed_key in layer_mappings.items():
        if exp_key in expected_layer:
            exp_val = expected_layer[exp_key]
            if isinstance(exp_val, dict) and exp_val.get("_undefined"):
                continue
            parsed_val = get_enum_value(parsed_layer.get(parsed_key))
            if not compare_values(exp_val, parsed_val):
                result.add_diff(f"{path}.{exp_key}", exp_val, parsed_val, "layers")


def compare_comp_item(
    expected_item: dict[str, Any],
    parsed_comp: dict[str, Any],
    path: str,
    result: ValidationResult,
) -> None:
    """Compare composition item properties."""
    comp_mappings = {
        "name": "name",
        "id": "id",
        "comment": "comment",
        "duration": "duration",
        "frameRate": "frame_rate",
        "width": "width",
        "height": "height",
        "displayStartTime": "display_start_time",
        "dropFrame": "drop_frame",
        "bgColor": "bg_color",
        "pixelAspect": "pixel_aspect",
        "shutterPhase": "shutter_phase",
        "shutterAngle": "shutter_angle",
        "motionBlur": "motion_blur",
        "workAreaStart": "work_area_start",
        "workAreaDuration": "work_area_duration",
        "preserveNestedResolution": "preserve_nested_resolution",
        "preserveNestedFrameRate": "preserve_nested_frame_rate",
        "frameBlending": "frame_blending",
        "hideShyLayers": "hide_shy_layers",
        "resolutionFactor": "resolution_factor",
    }

    for exp_key, parsed_key in comp_mappings.items():
        if exp_key in expected_item:
            exp_val = expected_item[exp_key]
            if isinstance(exp_val, dict) and exp_val.get("_undefined"):
                continue
            parsed_val = get_enum_value(parsed_comp.get(parsed_key))
            if not compare_values(exp_val, parsed_val):
                result.add_diff(f"{path}.{exp_key}", exp_val, parsed_val, "composition")

    # Compare layer counts
    exp_layers = expected_item.get("layers", [])
    parsed_layers = parsed_comp.get("layers", [])
    if len(exp_layers) != len(parsed_layers):
        result.add_diff(
            f"{path}.numLayers", len(exp_layers), len(parsed_layers), "composition"
        )

    # Compare each layer
    comp_duration = expected_item.get("duration", 60.0)
    for i, (exp_layer, parsed_layer) in enumerate(zip(exp_layers, parsed_layers)):
        compare_layer(
            exp_layer, parsed_layer, f"{path}.layers[{i}]", comp_duration, result
        )

    # Compare markers
    exp_markers = expected_item.get("markers", [])
    parsed_markers = parsed_comp.get("markers", [])
    if len(exp_markers) != len(parsed_markers):
        result.add_diff(
            f"{path}.numMarkers", len(exp_markers), len(parsed_markers), "markers"
        )

    frame_rate = expected_item.get("frameRate", 24.0)
    for i, (exp_marker, parsed_marker) in enumerate(zip(exp_markers, parsed_markers)):
        compare_marker(
            exp_marker, parsed_marker, f"{path}.markers[{i}]", frame_rate, result
        )


def compare_folder_hierarchy(
    expected_items: list[dict[str, Any]],
    parsed_items: dict[int, dict[str, Any]],
    result: ValidationResult,
) -> None:
    """Compare folder hierarchy."""
    expected_folders = {}
    for item in expected_items:
        if item.get("itemType") == "FolderItem":
            expected_folders[item["id"]] = item

    parsed_folders = {}
    for item_id, item in parsed_items.items():
        if item.get("type_name") == "Folder":
            parsed_folders[item_id] = item

    for folder_id, exp_folder in expected_folders.items():
        if folder_id not in parsed_folders:
            result.add_diff(
                f"Folder[{exp_folder['name']}]", "exists", "missing", "folders"
            )
        else:
            parsed_folder = parsed_folders[folder_id]
            if exp_folder["name"] != parsed_folder.get("name"):
                result.add_diff(
                    f"Folder[id={folder_id}].name",
                    exp_folder["name"],
                    parsed_folder.get("name"),
                    "folders",
                )


def compare_settings(
    expected_settings: dict[str, Any],
    parsed_settings: dict[str, Any] | None,
    path: str,
    result: ValidationResult,
) -> None:
    """Compare render settings.

    Render settings are now stored as raw integer values with ExtendScript keys.
    """
    if parsed_settings is None:
        result.add_diff(f"{path}", "exists", "missing", "renderqueue")
        return

    # Map expected JSON keys to parsed ExtendScript keys
    # Parsed values are raw integers matching ExtendScript
    key_mappings = {
        "quality": "Quality",
        "effects": "Effects",
        "proxyUse": "Proxy Use",
        "motionBlur": "Motion Blur",
        "frameBlending": "Frame Blending",
        "fieldRender": "Field Render",
        "guideLayers": "Guide Layers",
        "soloSwitches": "Solo Switches",
        "colorDepth": "Color Depth",
    }

    for exp_key, parsed_key in key_mappings.items():
        if exp_key in expected_settings:
            exp_val = expected_settings[exp_key]
            parsed_val = parsed_settings.get(parsed_key)
            if exp_val != parsed_val:
                result.add_diff(
                    f"{path}.{exp_key}",
                    exp_val,
                    parsed_val,
                    "renderqueue",
                )


def compare_output_module_settings(
    expected_settings: dict[str, Any],
    parsed_settings: dict[str, Any] | None,
    path: str,
    result: ValidationResult,
) -> None:
    """Compare output module settings.

    Output module settings are stored as a dict with ExtendScript keys.
    """
    if expected_settings is None:
        return
    if parsed_settings is None:
        result.add_diff(f"{path}", "exists", "missing", "renderqueue")
        return

    # Compare video output
    if "videoOutput" in expected_settings:
        exp_has_video = expected_settings["videoOutput"] == "On"
        parsed_has_video = parsed_settings.get("Video Output", False)
        if exp_has_video != parsed_has_video:
            result.add_diff(
                f"{path}.videoOutput",
                expected_settings["videoOutput"],
                "On" if parsed_has_video else "Off",
                "renderqueue",
            )

    # Compare audio output
    if "audioOutput" in expected_settings:
        exp_has_audio = expected_settings["audioOutput"] == "On"
        parsed_has_audio = parsed_settings.get("Output Audio", False)
        if exp_has_audio != parsed_has_audio:
            result.add_diff(
                f"{path}.audioOutput",
                expected_settings["audioOutput"],
                "On" if parsed_has_audio else "Off",
                "renderqueue",
            )


def compare_render_queue(
    expected_rq: dict[str, Any],
    parsed_rq: dict[str, Any],
    result: ValidationResult,
    verbose: bool = False,
) -> None:
    """Compare render queue items."""
    expected_items = expected_rq.get("items", [])
    parsed_items = parsed_rq.get("items", [])

    if len(expected_items) != len(parsed_items):
        result.add_diff(
            "RenderQueue.numItems",
            len(expected_items),
            len(parsed_items),
            "renderqueue",
        )
        if verbose:
            print(
                f"  Item count mismatch: expected {len(expected_items)}, got {len(parsed_items)}"
            )

    # Compare each render queue item
    for i, exp_item in enumerate(expected_items):
        if i >= len(parsed_items):
            result.add_diff(f"RenderQueueItem[{i}]", "exists", "missing", "renderqueue")
            continue

        parsed_item = parsed_items[i]
        path = f"RenderQueueItem[{i}]"

        # Compare render settings
        if "settings" in exp_item:
            compare_settings(
                exp_item["settings"],
                parsed_item.get("settings"),
                f"{path}.settings",
                result,
            )

        # Compare output modules
        exp_oms = exp_item.get("outputModules", [])
        parsed_oms = parsed_item.get("output_modules", [])

        if len(exp_oms) != len(parsed_oms):
            result.add_diff(
                f"{path}.numOutputModules",
                len(exp_oms),
                len(parsed_oms),
                "renderqueue",
            )

        for j, exp_om in enumerate(exp_oms):
            if j >= len(parsed_oms):
                result.add_diff(
                    f"{path}.outputModule[{j}]", "exists", "missing", "renderqueue"
                )
                continue

            parsed_om = parsed_oms[j]
            om_path = f"{path}.outputModule[{j}]"

            # Compare output module settings
            if "settings" in exp_om:
                compare_output_module_settings(
                    exp_om["settings"],
                    parsed_om["settings"],
                    f"{om_path}.settings",
                    result,
                )


def validate_aep(
    aep_path: Path,
    json_path: Path,
    verbose: bool = False,
    category_filter: str | None = None,
) -> ValidationResult:
    """
    Validate parsed AEP against expected JSON.

    Args:
        aep_path: Path to .aep file.
        json_path: Path to expected JSON (from ExtendScript export).
        verbose: Whether to print detailed progress.
        category_filter: Only show differences from this category.

    Returns:
        ValidationResult containing all differences.
    """
    result = ValidationResult()

    # Parse AEP
    if verbose:
        print(f"Parsing: {aep_path.name}")
    app = parse(aep_path)
    project = app.project
    parsed = to_dict(project)

    # Load expected JSON
    with json_path.open(encoding="utf-8") as f:
        expected = json.load(f)

    # Compare project-level properties
    if verbose:
        print("\n=== Comparing Project Properties ===")
    compare_project_level(expected, parsed, result)

    # Get expected items
    expected_items = expected.get("items", [])
    comps = [i for i in expected_items if i.get("itemType") == "CompItem"]

    # Compare compositions
    if verbose:
        print("\n=== Comparing Compositions ===")
    parsed_comps = parsed.get("_compositions", [])
    parsed_by_id = {comp["id"]: comp for comp in parsed_comps}

    for exp_item in comps:
        item_id = exp_item["id"]
        item_name = exp_item["name"]

        if item_id not in parsed_by_id:
            result.add_diff(f"Comp[{item_name}]", "exists", "missing", "composition")
            if verbose:
                print(f"  {item_name} (id={item_id}): MISSING!")
            continue

        parsed_comp = parsed_by_id[item_id]
        before_count = len(result)
        compare_comp_item(exp_item, parsed_comp, f"Comp[{item_name}]", result)

        if verbose:
            diff_count = len(result) - before_count
            if diff_count > 0:
                print(f"  {item_name} (id={item_id}): {diff_count} differences")
            else:
                print(f"  {item_name} (id={item_id}): OK")

    # Compare folder hierarchy
    if verbose:
        print("\n=== Comparing Folder Hierarchy ===")
    compare_folder_hierarchy(expected_items, parsed.get("items", {}), result)

    # Compare render queue
    if verbose:
        print("\n=== Comparing Render Queue ===")
    expected_rq = expected.get("renderQueue", {})
    compare_render_queue(expected_rq, parsed.get("render_queue", {}), result, verbose)

    return result


def print_results(
    result: ValidationResult, verbose: bool = False, category_filter: str | None = None
) -> None:
    """Print validation results."""
    print("\n" + "=" * 60)

    if not result.differences:
        print("SUCCESS: All parsed values match expected values!")
        return

    filtered_diffs = result.differences
    if category_filter:
        # Filter by category prefix
        filtered_diffs = [
            d for d in result.differences if category_filter.lower() in d.lower()
        ]

    print(f"TOTAL DIFFERENCES FOUND: {len(result.differences)}")

    if category_filter:
        print(f"(Showing {len(filtered_diffs)} matching filter '{category_filter}')")

    print("\nDifferences by category:")
    for cat, count in sorted(result.categories.items()):
        print(f"  {cat}: {count}")

    if verbose and filtered_diffs:
        print("\nAll differences:")
        for d in filtered_diffs[:50]:  # Limit output
            print(f"  {d}")
        if len(filtered_diffs) > 50:
            print(f"  ... and {len(filtered_diffs) - 50} more")


def main(args: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate parsed AEP values against expected JSON from ExtendScript export.",
    )
    parser.add_argument("aep_file", type=Path, help="Path to .aep file")
    parser.add_argument("json_file", type=Path, help="Path to expected JSON file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print detailed progress"
    )
    parser.add_argument(
        "-c",
        "--category",
        choices=[
            "project",
            "composition",
            "layers",
            "markers",
            "folders",
            "renderqueue",
        ],
        help="Filter differences by category",
    )

    parsed_args = parser.parse_args(args)

    if not parsed_args.aep_file.exists():
        print(f"Error: AEP file not found: {parsed_args.aep_file}")
        return 1

    if not parsed_args.json_file.exists():
        print(f"Error: JSON file not found: {parsed_args.json_file}")
        return 1

    print(f"Validating: {parsed_args.aep_file.name}")
    print(f"Expected:   {parsed_args.json_file.name}")

    result = validate_aep(
        parsed_args.aep_file,
        parsed_args.json_file,
        verbose=parsed_args.verbose,
        category_filter=parsed_args.category,
    )

    print_results(
        result, verbose=parsed_args.verbose, category_filter=parsed_args.category
    )

    return 0 if not result.differences else 1


if __name__ == "__main__":
    sys.exit(main())
