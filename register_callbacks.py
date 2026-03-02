"""Desktop GUI plugin for code_puppy."""

from code_puppy.callbacks import register_callback


def _custom_help():
    """Return help for the /desktop command."""
    return [("desktop", "Launch the desktop GUI application")]


def _handle_custom_command(command: str, name: str):
    """Handle the /desktop command."""
    if name == "desktop":
        from desktop.main import launch_desktop
        launch_desktop()
        return True
    return None


register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_custom_command)
