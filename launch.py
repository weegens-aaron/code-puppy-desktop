#!/usr/bin/env python
"""Direct launcher for the desktop plugin.

This script allows launching the desktop GUI directly without
going through the code-puppy CLI. Useful for development and
creating shortcuts.

Usage:
    python ~/.code_puppy/plugins/desktop/launch.py
"""
import sys
from pathlib import Path

# Add the plugin directory to sys.path so imports work
plugin_dir = Path(__file__).parent
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

# Also ensure code_puppy is importable
# This handles the case where code_puppy isn't installed system-wide
try:
    import code_puppy
except ImportError:
    # Try to find code_puppy in common locations
    possible_paths = [
        Path.home() / ".code_puppy",
        Path.cwd() / "code_puppy",
    ]
    for p in possible_paths:
        if p.exists() and (p / "__init__.py").exists():
            sys.path.insert(0, str(p.parent))
            break


def main():
    """Launch the desktop application."""
    from main import launch_desktop
    return launch_desktop()


if __name__ == "__main__":
    sys.exit(main())
