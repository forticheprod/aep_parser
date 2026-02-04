"""Tests for Folder model parsing using samples from models/folder/.

These tests verify that aep_parser produces the same values as the JSON
reference files exported from After Effects.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aep_parser import Project, parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "folder"


def get_sample_files() -> list[str]:
    """Get all .aep files in the folder samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def get_folder_from_json(expected: dict) -> dict:
    """Extract folder data from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Folder":
                return item
    return {}


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_folder_sample(sample_name: str) -> None:
    """Test that each folder sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


def get_first_folder(project: Project):
    """Get the first user-created folder (not root folder)."""
    for folder in project.folders:
        if folder.name != "root":
            return folder
    return None


class TestFolderBasic:
    """Tests for basic folder attributes."""

    def test_empty(self) -> None:
        """Test empty folder."""
        expected = load_expected("empty")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "empty.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["name"] == "EmptyFolder"
        assert folder.name == folder_json["name"]

    def test_name_renamed(self) -> None:
        """Test renamed folder."""
        expected = load_expected("name_renamed")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "name_renamed.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["name"] == "RenamedFolder"
        assert folder.name == folder_json["name"]

    def test_comment(self) -> None:
        """Test folder with comment."""
        expected = load_expected("comment")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "comment.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["comment"] == "Folder comment"
        assert folder.comment == folder_json["comment"]


class TestFolderLabel:
    """Tests for folder label attribute."""

    def test_label_1(self) -> None:
        """Test folder with label 1."""
        expected = load_expected("label_1")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_1.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["label"] == 1
        assert folder.label.value == folder_json["label"]

    def test_label_5(self) -> None:
        """Test folder with label 5."""
        expected = load_expected("label_5")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_5.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["label"] == 5
        assert folder.label.value == folder_json["label"]

    def test_label_10(self) -> None:
        """Test folder with label 10."""
        expected = load_expected("label_10")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_10.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["label"] == 10
        assert folder.label.value == folder_json["label"]


class TestFolderNesting:
    """Tests for folder nesting."""

    def test_parentFolder_nested(self) -> None:
        """Test nested folder structure."""
        load_expected("parentFolder_nested")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "parentFolder_nested.aep")
        assert len(project.folders) > 2
        # Verify at least one folder has a parent_id pointing to another folder
        nested = [f for f in project.folders if f.parent_id]
        assert bool(nested)

    def test_numItems_3(self) -> None:
        """Test folder with 3 items."""
        expected = load_expected("numItems_3")
        folder_json = get_folder_from_json(expected)
        project = parse_project(SAMPLES_DIR / "numItems_3.aep")
        folder = get_first_folder(project)
        assert folder is not None
        assert folder_json["numItems"] == 3
        assert len(folder.folder_items) == folder_json["numItems"]
