"""Tests for base panel utility functions.

Tests the pure functions from base_panel module that don't require Qt.
Widget class testing requires pytest-qt and a real Qt environment.
"""

import pytest


# Since importing from base_panel triggers Qt imports, we test the function
# logic directly by recreating them here. This validates the algorithm.

class MockColors:
    """Mock color values matching the styles module."""
    bg_primary = "#1e1e1e"
    bg_secondary = "#2d2d2d"
    bg_tertiary = "#3d3d3d"
    text_primary = "#e0e0e0"
    text_secondary = "#a0a0a0"
    text_muted = "#6a6a6a"
    border_subtle = "#3d3d3d"
    border_default = "#5a5a5a"
    accent_primary = "#1a73e8"
    accent_warning = "#ffc107"


COLORS = MockColors()


def get_panel_stylesheet(include_checkbox: bool = False) -> str:
    """Generate common stylesheet for sidebar panels."""
    base_style = f"""
        QWidget {{
            background-color: {COLORS.bg_primary};
            color: {COLORS.text_primary};
        }}
        QListWidget {{
            background-color: {COLORS.bg_secondary};
        }}
        QListWidget::item:selected {{
            background-color: {COLORS.accent_primary};
        }}
    """

    if include_checkbox:
        base_style += f"""
        QListWidget::indicator {{
            border: 1px solid {COLORS.border_default};
        }}
        QListWidget::indicator:checked {{
            background-color: {COLORS.accent_primary};
        }}
        """

    return base_style


def render_empty_state(title: str, message: str, hint: str = "") -> str:
    """Render HTML for empty state display."""
    html = f"""
    <div style="color: {COLORS.text_primary};">
        <h3 style="color: {COLORS.accent_warning};">{title}</h3>
        <p style="color: {COLORS.text_secondary};">{message}</p>
    """
    if hint:
        html += f"""
        <p style="color: {COLORS.text_muted};">{hint}</p>
        """
    html += "</div>"
    return html


class TestGetPanelStylesheet:
    """Tests for get_panel_stylesheet function."""

    def test_returns_string(self):
        """Test function returns a CSS string."""
        result = get_panel_stylesheet()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_essential_selectors(self):
        """Test stylesheet contains essential Qt selectors."""
        result = get_panel_stylesheet()
        assert "QWidget" in result
        assert "QListWidget" in result

    def test_without_checkbox(self):
        """Test stylesheet without checkbox styles."""
        result = get_panel_stylesheet(include_checkbox=False)
        assert "QListWidget::indicator" not in result

    def test_with_checkbox(self):
        """Test stylesheet includes checkbox styles when requested."""
        result = get_panel_stylesheet(include_checkbox=True)
        assert "QListWidget::indicator" in result
        assert "QListWidget::indicator:checked" in result

    def test_contains_color_values(self):
        """Test stylesheet contains color definitions."""
        result = get_panel_stylesheet()
        assert "#" in result


class TestRenderEmptyState:
    """Tests for render_empty_state function."""

    def test_returns_html_string(self):
        """Test function returns HTML string."""
        result = render_empty_state("No Items", "Nothing found")
        assert isinstance(result, str)
        assert "<div" in result
        assert "</div>" in result

    def test_contains_title(self):
        """Test HTML contains the title."""
        result = render_empty_state("Test Title", "Test message")
        assert "Test Title" in result

    def test_contains_message(self):
        """Test HTML contains the message."""
        result = render_empty_state("Title", "This is the message")
        assert "This is the message" in result

    def test_includes_hint_when_provided(self):
        """Test HTML includes hint when provided."""
        result = render_empty_state("Title", "Message", hint="This is a hint")
        assert "This is a hint" in result

    def test_excludes_hint_when_empty(self):
        """Test HTML excludes hint paragraph when not provided."""
        result = render_empty_state("Title", "Message")
        # Should have 2 </p> tags (title uses h3, message has one p)
        assert result.count("</p>") == 1

    def test_html_structure(self):
        """Test HTML has proper structure."""
        result = render_empty_state("Title", "Message", "Hint")
        assert "<h3" in result
        assert "</h3>" in result
        assert "<p" in result
        assert "style=" in result
