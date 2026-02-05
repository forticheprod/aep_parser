#!/usr/bin/env python
"""
AEP Parser Validation Tool.

This is a development wrapper script. After installing the package,
use the `aep-validate` command instead.

Usage:
    python scripts/validate_aep.py project.aep expected.json
    python scripts/validate_aep.py project.aep expected.json --verbose
    python scripts/validate_aep.py project.aep expected.json --category layers
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aep_parser.cli.validate import main

if __name__ == "__main__":
    sys.exit(main())
