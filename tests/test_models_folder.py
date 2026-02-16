"""Tests for Folder model parsing."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import (
    get_first_folder,
    get_folder_from_json,
    get_sample_files,
    load_expected,
)

from aep_parser import Project, parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "folder"


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_folder_sample(sample_name: str) -> None:
    """Each folder sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


class TestFolderBasic:
    """Tests for basic folder attributes."""

    def test_empty(self) -> None:
        expected = load_expected(SAMPLES_DIR, "empty")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "empty.aep"))
        assert folder is not None
        assert folder.name == folder_json["name"] == "EmptyFolder"

    def test_name_renamed(self) -> None:
        expected = load_expected(SAMPLES_DIR, "name_renamed")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "name_renamed.aep"))
        assert folder is not None
        assert folder.name == folder_json["name"] == "RenamedFolder"

    def test_comment(self) -> None:
        expected = load_expected(SAMPLES_DIR, "comment")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "comment.aep"))
        assert folder is not None
        assert folder.comment == folder_json["comment"] == "Folder comment"


class TestFolderLabel:
    """Tests for folder label attribute."""

    def test_label_1(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_1")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "label_1.aep"))
        assert folder is not None
        assert folder.label.value == folder_json["label"] == 1

    def test_label_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_5")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "label_5.aep"))
        assert folder is not None
        assert folder.label.value == folder_json["label"] == 5

    def test_label_10(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_10")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "label_10.aep"))
        assert folder is not None
        assert folder.label.value == folder_json["label"] == 10


class TestFolderNesting:
    """Tests for folder nesting."""

    def test_parentFolder_nested(self) -> None:
        project = parse_project(SAMPLES_DIR / "parentFolder_nested.aep")
        assert len(project.folders) > 2
        nested = [f for f in project.folders if f.parent_folder]
        assert bool(nested)

    def test_numItems_3(self) -> None:
        expected = load_expected(SAMPLES_DIR, "numItems_3")
        folder_json = get_folder_from_json(expected)
        folder = get_first_folder(parse_project(SAMPLES_DIR / "numItems_3.aep"))
        assert folder is not None
        assert folder_json["numItems"] == 3
        assert len(folder.items) == folder_json["numItems"]
        assert all(hasattr(item, "id") for item in folder.items)
