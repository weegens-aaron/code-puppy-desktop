#!/usr/bin/env python
"""Direct launcher for the desktop plugin (no console).

This script allows launching the desktop GUI directly without
going through the code-puppy CLI and without showing a terminal.

Usage:
    Double-click launch.pyw
"""
import sys
import traceback
from pathlib import Path
from datetime import datetime

# Log file for errors (since we have no console)
LOG_FILE = Path(__file__).parent / "launch_errors.log"


def log_error(msg: str):
    """Write error to log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")


try:
    # Add the plugin directory to sys.path so imports work
    plugin_dir = Path(__file__).parent
    if str(plugin_dir) not in sys.path:
        sys.path.insert(0, str(plugin_dir))

    # Also ensure code_puppy is importable
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

    from main import launch_desktop
    sys.exit(launch_desktop())

except Exception as e:
    # Log the full traceback
    log_error("=" * 60)
    log_error(f"Launch failed at {datetime.now()}")
    log_error(traceback.format_exc())

    # Also try to show a message box
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Failed to launch Code Puppy Desktop.\n\nError: {e}\n\nSee launch_errors.log for details.",
            "Launch Error",
            0x10  # MB_ICONERROR
        )
    except:
        pass

    sys.exit(1)
