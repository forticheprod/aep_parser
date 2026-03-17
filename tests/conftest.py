"""Shared test fixtures and helpers for aep_parser tests."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from aep_parser import Application, Project
from aep_parser import parse as _parse_aep

if TYPE_CHECKING:
    from aep_parser.models.items.folder import FolderItem
    from aep_parser.models.items.footage import FootageItem
    from aep_parser.models.layers.layer import Layer

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


@lru_cache(maxsize=None)
def parse_project(aep_file_path: str | os.PathLike[str]) -> Project:
    """Parse an AEP file and return the Project object.

    Results are cached for the session so the same file is only parsed once.
    """
    return parse_app(aep_file_path).project


@lru_cache(maxsize=None)
def parse_app(aep_file_path: str | os.PathLike[str]) -> Application:
    """Parse an AEP file and return the Application object.

    Results are cached for the session so the same file is only parsed once.
    """
    return _parse_aep(aep_file_path)


@lru_cache(maxsize=None)
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


def get_first_layer(project: Project) -> Layer:
    """Get the first layer from the first composition that has layers."""
    assert len(project.compositions) >= 1
    for comp in project.compositions:
        if len(comp.layers) >= 1:
            return comp.layers[0]
    raise AssertionError("No composition with layers found")


def get_first_footage(project: Project) -> FootageItem | None:
    """Get the first footage item."""
    if project.footages:
        return project.footages[0]
    return None


def get_first_folder(project: Project) -> FolderItem | None:
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
    """Extract first layer marker value from expected JSON.

    Looks for the ADBE Marker property in the layer's properties array
    and returns the first keyframe's value.
    """
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition" and "layers" in item:
                for layer in item["layers"]:
                    for prop in layer.get("properties", []):
                        if prop.get("matchName") == "ADBE Marker":
                            kfs = prop.get("keyframes", [])
                            if kfs:
                                return kfs[0].get("value", {})
    return {}
