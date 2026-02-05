#!/usr/bin/env python
"""
Visualize an After Effects project structure.

This is a development wrapper script. After installing the package,
use the `aep-visualize` command instead.

Usage:
    python scripts/visualize_project.py samples/models/composition/bgColor_custom.aep
    python scripts/visualize_project.py samples/models/composition/bgColor_custom.aep --format dot > project.dot
    python scripts/visualize_project.py samples/models/composition/bgColor_custom.aep --format mermaid
    python scripts/visualize_project.py samples/models/composition/bgColor_custom.aep --depth 2
    python scripts/visualize_project.py samples/models/composition/bgColor_custom.aep --no-properties
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aep_parser.cli.visualize import main

if __name__ == "__main__":
    main()
