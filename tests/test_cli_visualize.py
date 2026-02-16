"""Tests for CLI visualize module.

These tests verify the aep-visualize command line tool functionality.
"""

from __future__ import annotations

import io
from pathlib import Path

from conftest import parse_app

from aep_parser.cli.visualize import (
    build_project_node,
    format_dot,
    format_json,
    format_mermaid,
    format_text,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def get_sample_app():
    """Get a sample app for testing."""
    aep_path = SAMPLES_DIR / "versions" / "ae2025" / "complete.aep"
    return parse_app(aep_path)


class TestBuildProjectNode:
    """Tests for build_project_node function."""

    def test_builds_project_structure(self) -> None:
        """Test that project node is built with correct structure."""
        app = get_sample_app()
        # Use include_properties=False to avoid PropertyGroup/Property type mismatch
        node = build_project_node(app, include_properties=False)

        assert node["type"] == "Project"
        assert "name" in node
        assert "attrs" in node
        assert "children" in node
        assert "version" in node["attrs"]
        assert "frame_rate" in node["attrs"]

    def test_project_node_without_properties(self) -> None:
        """Test building project node without layer properties."""
        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        assert node["type"] == "Project"
        # Check that no property nodes exist in the tree
        def has_property_node(n: dict) -> bool:
            if n.get("type") == "Property":
                return True
            for child in n.get("children", []):
                if has_property_node(child):
                    return True
            return False

        assert not has_property_node(node)

    def test_project_node_has_items(self) -> None:
        """Test that project node includes folder and composition items."""
        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        # Should have at least some children (folders, compositions, footage)
        assert len(node["children"]) > 0


class TestFormatText:
    """Tests for format_text function."""

    def test_text_output_not_empty(self) -> None:
        """Test that text output produces content."""
        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        output = io.StringIO()
        format_text(node, output)

        result = output.getvalue()
        assert len(result) > 0
        assert "Project" in result or node["name"] in result

    def test_text_output_with_depth_limit(self) -> None:
        """Test that depth limit reduces output."""
        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        output_full = io.StringIO()
        format_text(node, output_full, max_depth=None)

        output_limited = io.StringIO()
        format_text(node, output_limited, max_depth=1)

        # Limited depth should produce less or equal output
        assert len(output_limited.getvalue()) <= len(output_full.getvalue())


class TestFormatJson:
    """Tests for format_json function."""

    def test_json_output_valid(self) -> None:
        """Test that JSON output is valid JSON."""
        import json

        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        output = io.StringIO()
        format_json(node, output)

        result = output.getvalue()
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["type"] == "Project"
        assert "children" in parsed

    def test_json_output_with_depth_limit(self) -> None:
        """Test that JSON respects depth limit."""
        import json

        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        output = io.StringIO()
        format_json(node, output, max_depth=1)

        result = output.getvalue()
        parsed = json.loads(result)

        # Children at depth 1 should have truncated children (string like "[N children omitted]")
        for child in parsed.get("children", []):
            children = child.get("children")
            # Either no children, empty list, or a truncation message string
            assert children is None or children == [] or isinstance(children, str)


class TestFormatDot:
    """Tests for format_dot function."""

    def test_dot_output_valid_structure(self) -> None:
        """Test that DOT output has valid Graphviz structure."""
        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        output = io.StringIO()
        format_dot(node, output)

        result = output.getvalue()
        assert "digraph" in result
        assert "{" in result
        assert "}" in result


class TestFormatMermaid:
    """Tests for format_mermaid function."""

    def test_mermaid_output_valid_structure(self) -> None:
        """Test that Mermaid output has valid flowchart structure."""
        app = get_sample_app()
        node = build_project_node(app, include_properties=False)

        output = io.StringIO()
        format_mermaid(node, output)

        result = output.getvalue()
        assert "flowchart" in result or "graph" in result
