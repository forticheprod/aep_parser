#!/usr/bin/env python
"""
AEP/AEPX File Comparison Tool.

This is a development wrapper script. After installing the package,
use the `aep-compare` command instead.

Usage:
    python scripts/compare_aep.py file1.aepx file2.aepx
    python scripts/compare_aep.py file1.aep file2.aep
    python scripts/compare_aep.py file1.aep file2.aep --json
    python scripts/compare_aep.py file1.aep file2.aep --filter ldta
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aep_parser.cli.compare import main

if __name__ == "__main__":
    sys.exit(main())
