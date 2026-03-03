"""Desktop GUI plugin for code_puppy."""

import sys
from pathlib import Path

from code_puppy.callbacks import register_callback

# Add plugin directory to sys.path for imports
# (hyphenated directory name breaks Python's relative imports)
_plugin_dir = str(Path(__file__).parent)
if _plugin_dir not in sys.path:
    sys.path.insert(0, _plugin_dir)


def _custom_help():
    """Return help for the /desktop command."""
    return [("desktop", "Launch the desktop GUI application")]


def _handle_custom_command(command: str, name: str):
    """Handle the /desktop command."""
    if name == "desktop":
        from main import launch_desktop
        launch_desktop()
        return True
    return None


register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_custom_command)
