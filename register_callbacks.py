"""Desktop GUI plugin for code_puppy."""

import sys
import logging
from pathlib import Path

from code_puppy.callbacks import register_callback

logger = logging.getLogger(__name__)

# Add plugin directory to sys.path for imports
# (hyphenated directory name breaks Python's relative imports)
_plugin_dir = str(Path(__file__).parent)
if _plugin_dir not in sys.path:
    sys.path.insert(0, _plugin_dir)

# -------------------------------------------------------------------------
# Plugin State (for communication between hooks and GUI)
# -------------------------------------------------------------------------

# Signal emitter for notifying GUI of events from hooks
_gui_signal_emitter = None


def set_gui_signal_emitter(emitter):
    """Set the GUI signal emitter for hook-to-GUI communication."""
    global _gui_signal_emitter
    _gui_signal_emitter = emitter
    logger.debug("GUI signal emitter registered")


def get_gui_signal_emitter():
    """Get the GUI signal emitter."""
    return _gui_signal_emitter


# -------------------------------------------------------------------------
# Custom Command Hooks
# -------------------------------------------------------------------------

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


# -------------------------------------------------------------------------
# Lifecycle Hooks
# -------------------------------------------------------------------------

async def _on_startup():
    """Handle application startup."""
    logger.info("Desktop plugin startup hook fired")


async def _on_shutdown():
    """Handle application shutdown - cleanup resources."""
    global _gui_signal_emitter
    logger.info("Desktop plugin shutdown hook fired")
    _gui_signal_emitter = None


# -------------------------------------------------------------------------
# Agent Lifecycle Hooks
# -------------------------------------------------------------------------

def _on_agent_reload(*args, **kwargs):
    """Handle agent reload - notify GUI to refresh panels."""
    logger.debug("Agent reload detected")
    emitter = get_gui_signal_emitter()
    if emitter and hasattr(emitter, 'agent_reloaded'):
        emitter.agent_reloaded.emit()


async def _on_agent_exception(exception, *args, **kwargs):
    """Handle agent exceptions - capture for GUI error display."""
    logger.info(f"Agent exception captured: {type(exception).__name__}: {exception}")
    emitter = get_gui_signal_emitter()
    if emitter and hasattr(emitter, 'agent_exception_occurred'):
        emitter.agent_exception_occurred.emit(str(exception))


# -------------------------------------------------------------------------
# Register All Callbacks
# -------------------------------------------------------------------------

register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_custom_command)
register_callback("startup", _on_startup)
register_callback("shutdown", _on_shutdown)
register_callback("agent_reload", _on_agent_reload)
register_callback("agent_exception", _on_agent_exception)
