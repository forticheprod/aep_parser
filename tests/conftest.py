"""Shared test fixtures and helpers for aep_parser tests."""

from __future__ import annotations

import json
import os
from pathlib import Path

from aep_parser import App, Project
from aep_parser import parse as _parse_aep

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """Parse an AEP file and return the Project object.

    Convenience wrapper around :func:`aep_parser.parse` for tests that only
    need the ``Project``.
    """
    return _parse_aep(aep_file_path).project


def parse_app(aep_file_path: str | os.PathLike[str]) -> App:
    """Parse an AEP file and return the App object."""
    return _parse_aep(aep_file_path)


def load_expected(samples_dir: Path, sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = samples_dir / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def get_sample_files(samples_dir: Path) -> list[str]:
    """Get all .aep stems in a samples directory."""
    if not samples_dir.exists():
        return []
    return [f.stem for f in samples_dir.glob("*.aep")]


def get_comp_from_json(expected: dict) -> dict:
    """Extract first composition from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition":
                return item
    return {}


def get_layer_from_json(expected: dict) -> dict:
    """Extract first layer from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if "layers" in item and len(item["layers"]) > 0:
                return item["layers"][0]
    return {}


def get_footage_from_json(expected: dict) -> dict:
    """Extract first footage item from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Footage":
                return item
    return {}


def get_folder_from_json(expected: dict) -> dict:
    """Extract first folder from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Folder":
                return item
    return {}


def get_first_layer(project: Project):  # type: ignore[no-untyped-def]
    """Get the first layer from the first composition that has layers."""
    assert len(project.compositions) >= 1
    for comp in project.compositions:
        if len(comp.layers) >= 1:
            return comp.layers[0]
    raise AssertionError("No composition with layers found")


def get_first_footage(project: Project):  # type: ignore[no-untyped-def]
    """Get the first footage item."""
    if project.footages:
        return project.footages[0]
    return None


def get_first_folder(project: Project):  # type: ignore[no-untyped-def]
    """Get the first user-created folder (not root)."""
    for folder in project.folders:
        if folder.name != "root":
            return folder
    return None


def get_comp_marker_from_json(expected: dict) -> dict:
    """Extract first composition marker from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition":
                markers = item.get("markers", [])
                if isinstance(markers, list) and len(markers) > 0:
                    return markers[0]
    return {}


def get_layer_marker_from_json(expected: dict) -> dict:
    """Extract first layer marker from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition" and "layers" in item:
                for layer in item["layers"]:
                    if "markers" in layer and len(layer["markers"]) > 0:
                        return layer["markers"][0]
    return {}
