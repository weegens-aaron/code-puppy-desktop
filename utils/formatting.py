"""Shared formatting utilities for the desktop app.

DRY: Reusable formatting functions used across renderers.
"""

import os


def format_size(size_bytes: int) -> str:
    """Format byte size into human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string like "1.5 KB" or "2.3 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# File type icons mapping
FILE_ICONS = {
    '.py': '\U0001F40D',    # Snake
    '.js': '\U0001F4DC',    # Scroll
    '.ts': '\U0001F4DC',    # Scroll
    '.html': '\U0001F310',  # Globe
    '.css': '\U0001F3A8',   # Palette
    '.json': '\u2699\ufe0f', # Gear
    '.md': '\U0001F4DD',    # Memo
    '.txt': '\U0001F4DD',   # Memo
    '.yaml': '\u2699\ufe0f', # Gear
    '.yml': '\u2699\ufe0f',  # Gear
    '.toml': '\u2699\ufe0f', # Gear
}

DEFAULT_FILE_ICON = '\U0001F4C4'  # Page
DIR_ICON = '\U0001F4C1'  # Folder


def get_file_icon(filepath: str, is_dir: bool = False) -> str:
    """Get emoji icon for a file based on extension.

    Args:
        filepath: Path to the file
        is_dir: Whether this is a directory

    Returns:
        Emoji icon string
    """
    if is_dir:
        return DIR_ICON
    ext = os.path.splitext(filepath)[1].lower()
    return FILE_ICONS.get(ext, DEFAULT_FILE_ICON)


# Operation icons for diffs
OPERATION_ICONS = {
    "create": "\u2728",      # Sparkles
    "modify": "\u270f\ufe0f", # Pencil
    "delete": "\U0001F5D1\ufe0f",  # Wastebasket
}

DEFAULT_OPERATION_ICON = "\U0001F4DD"  # Memo


def get_operation_icon(operation: str) -> str:
    """Get emoji icon for a file operation.

    Args:
        operation: One of 'create', 'modify', 'delete'

    Returns:
        Emoji icon string
    """
    return OPERATION_ICONS.get(operation, DEFAULT_OPERATION_ICON)
