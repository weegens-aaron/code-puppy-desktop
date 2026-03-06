"""SVG icon utilities for the desktop GUI."""

import os
from pathlib import Path
from functools import lru_cache

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QSize
from PySide6.QtSvg import QSvgRenderer

# Icons directory
ICONS_DIR = Path(__file__).parent.parent / "assets" / "icons"


@lru_cache(maxsize=64)
def get_icon(name: str, color: str | None = None, size: int = 24) -> QIcon:
    """Load an SVG icon, optionally recoloring it.

    Args:
        name: Icon name (without .svg extension)
        color: Optional hex color to apply (e.g., "#ffffff")
        size: Icon size in pixels

    Returns:
        QIcon instance
    """
    svg_path = ICONS_DIR / f"{name}.svg"

    if not svg_path.exists():
        # Return empty icon if not found
        return QIcon()

    if color:
        # Render with custom color
        pixmap = render_svg_colored(svg_path, color, size)
        return QIcon(pixmap)
    else:
        return QIcon(str(svg_path))


def render_svg_colored(svg_path: Path, color: str, size: int = 24) -> QPixmap:
    """Render an SVG with a custom color.

    Args:
        svg_path: Path to SVG file
        color: Hex color (e.g., "#ffffff")
        size: Output size in pixels

    Returns:
        QPixmap with the colored icon
    """
    # Read SVG content
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # Replace fill colors with our color
    # This is a simple approach that works for single-color icons
    import re
    # Replace fill="..." and stroke="..."
    svg_content = re.sub(r'fill="[^"]*"', f'fill="{color}"', svg_content)
    svg_content = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', svg_content)
    # Also handle style attributes
    svg_content = re.sub(r'fill:[^;"]*', f'fill:{color}', svg_content)

    # Render to pixmap
    renderer = QSvgRenderer(svg_content.encode('utf-8'))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return pixmap


def get_pixmap(name: str, color: str | None = None, size: int = 24) -> QPixmap:
    """Load an SVG icon as a QPixmap.

    Args:
        name: Icon name (without .svg extension)
        color: Optional hex color to apply
        size: Icon size in pixels

    Returns:
        QPixmap instance
    """
    svg_path = ICONS_DIR / f"{name}.svg"

    if not svg_path.exists():
        return QPixmap()

    if color:
        return render_svg_colored(svg_path, color, size)
    else:
        pixmap = QPixmap(str(svg_path))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        return pixmap


def has_icon(name: str) -> bool:
    """Check if an icon exists.

    Args:
        name: Icon name (without .svg extension)

    Returns:
        True if the icon file exists
    """
    return (ICONS_DIR / f"{name}.svg").exists()


# Icon name mappings for sidebar tabs
SIDEBAR_ICONS = {
    'files': 'folder',
    'sessions': 'chat',
    'agents': 'dog',      # Code Puppy mascot
    'models': 'robot',
    'skills': 'lightning',
    'mcp': 'plug',
}

# Fallback emoji icons if SVG not available
FALLBACK_ICONS = {
    'files': '📁',
    'sessions': '💬',
    'agents': '🐕',
    'models': '🤖',
    'skills': '⚡',
    'mcp': '🔌',
}


def get_sidebar_icon(tab_name: str, color: str = "#a0a0a0", size: int = 20) -> QIcon | str:
    """Get icon for a sidebar tab.

    Returns QIcon if SVG available, otherwise returns emoji string.

    Args:
        tab_name: Tab identifier (files, sessions, agents, etc.)
        color: Icon color
        size: Icon size

    Returns:
        QIcon or emoji string
    """
    icon_name = SIDEBAR_ICONS.get(tab_name)
    if icon_name and has_icon(icon_name):
        return get_icon(icon_name, color, size)
    return FALLBACK_ICONS.get(tab_name, '?')
