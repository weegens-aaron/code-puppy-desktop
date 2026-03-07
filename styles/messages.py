"""Message, thinking, and tool call styles.

This module contains:
- RoleStyle dataclass and get_role_style function
- Thinking section styles
- Tool call section styles
- Message bubble styles
- Shadow effect parameters
"""

from dataclasses import dataclass

from styles.colors import get_theme_manager

_theme_manager = get_theme_manager()


# =============================================================================
# Role Styles
# =============================================================================

@dataclass
class RoleStyle:
    """Style configuration for a message role."""
    background_color: str
    text_color: str
    font_family: str = "'Segoe UI', -apple-system, sans-serif"
    font_size: str = "14px"


def get_role_style(role: str) -> RoleStyle:
    """Get the style for a message role (uses current theme)."""
    colors = _theme_manager.current

    role_styles = {
        "user": RoleStyle(
            background_color=colors.role_user_bg,
            text_color=colors.role_user_text,
        ),
        "assistant": RoleStyle(
            background_color=colors.role_assistant_bg,
            text_color=colors.role_assistant_text,
        ),
        "thinking": RoleStyle(
            background_color=colors.role_thinking_bg,
            text_color=colors.role_thinking_text,
            font_family="'Consolas', 'Monaco', monospace",
            font_size="13px",
        ),
        "tool_call": RoleStyle(
            background_color=colors.role_tool_bg,
            text_color=colors.role_tool_text,
            font_family="'Consolas', 'Monaco', monospace",
            font_size="13px",
        ),
        "tool_output": RoleStyle(
            background_color=colors.role_tool_output_bg,
            text_color=colors.role_tool_output_text,
            font_family="'Consolas', 'Monaco', monospace",
            font_size="13px",
        ),
        "error": RoleStyle(
            background_color=colors.role_error_bg,
            text_color=colors.role_error_text,
        ),
        "question": RoleStyle(
            background_color=colors.bg_secondary,
            text_color=colors.accent_primary,
        ),
    }
    return role_styles.get(role, role_styles["assistant"])


# =============================================================================
# Thinking & Tool Call Section Styles
# =============================================================================

def get_thinking_section_style() -> str:
    """Get thinking section frame style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled inset style for thinking sections
        return f"""
            ThinkingSection {{
                background-color: {colors.role_thinking_bg};
                border-top: 1px solid {colors.shadow_dark};
                border-left: 1px solid {colors.shadow_dark};
                border-bottom: 1px solid {colors.shadow_light};
                border-right: 1px solid {colors.shadow_light};
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }}
            ThinkingSection QWidget {{
                background: transparent;
            }}
            ThinkingSection QLabel {{
                background: transparent;
            }}
            ThinkingSection QPushButton {{
                background: transparent;
            }}
        """
    else:
        return f"""
            ThinkingSection {{
                background-color: {colors.role_thinking_bg};
                border-left: 2px solid {colors.role_thinking_text}60;
                border-radius: 0;
                padding-left: 8px;
            }}
        """


def get_tool_call_section_style() -> str:
    """Get tool call section frame style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        # Beveled inset style for tool call sections
        return f"""
            ToolCallSection {{
                background-color: {colors.role_tool_bg};
                border-top: 1px solid {colors.shadow_dark};
                border-left: 1px solid {colors.shadow_dark};
                border-bottom: 1px solid {colors.shadow_light};
                border-right: 1px solid {colors.shadow_light};
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }}
            ToolCallSection QWidget {{
                background: transparent;
            }}
            ToolCallSection QLabel {{
                background: transparent;
            }}
            ToolCallSection QPushButton {{
                background: transparent;
            }}
        """
    else:
        return f"""
            ToolCallSection {{
                background-color: {colors.role_tool_bg};
                border-left: 2px solid {colors.role_tool_text}60;
                border-radius: 0;
                padding-left: 8px;
            }}
        """


def get_collapsible_toggle_style(accent_color: str) -> str:
    """Get collapsible toggle button style."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {accent_color};
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_light},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_dark}
                );
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {accent_color};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {accent_color}33;
                border-radius: 4px;
            }}
        """


def get_section_icon_style(color: str) -> str:
    """Get section icon label style."""
    return f"color: {color}; font-size: 14px;"


def get_section_title_style(color: str) -> str:
    """Get section title label style."""
    return f"color: {color}; font-weight: bold; font-size: 13px;"


def get_thinking_text_style() -> str:
    """Get thinking section text edit style for current theme."""
    colors = _theme_manager.current
    return f"""
        QPlainTextEdit {{
            background-color: transparent;
            border: none;
            color: {colors.text_secondary};
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
        }}
    """


def get_tool_args_text_style() -> str:
    """Get tool arguments text edit style for current theme."""
    colors = _theme_manager.current

    if colors.is_neumorphic:
        return f"""
            QPlainTextEdit {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors.shadow_dark},
                    stop:0.5 {colors.bg_primary},
                    stop:1 {colors.shadow_light}
                );
                border: none;
                color: {colors.text_secondary};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border-radius: 12px;
                padding: 8px;
            }}
        """
    else:
        return f"""
            QPlainTextEdit {{
                background-color: rgba(0, 0, 0, 0.2);
                border: none;
                color: {colors.text_secondary};
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border-radius: 4px;
                padding: 4px;
            }}
        """


# =============================================================================
# Modern Chat Bubble Styles
# =============================================================================

def get_message_bubble_style(is_user: bool, is_tool: bool = False, role: str = "") -> str:
    """Get message card style with neumorphic support and color accents.

    Args:
        is_user: Whether this is a user message
        is_tool: Whether this is a tool/thinking message
        role: Message role string (user, assistant, thinking, tool_call, tool_output, error)
    """
    colors = _theme_manager.current

    # Determine accent color based on role
    if role == "user":
        accent_color = colors.role_user_bg
    elif role == "assistant":
        accent_color = colors.role_assistant_bg
    elif role == "thinking":
        accent_color = colors.role_thinking_bg
    elif role in ("tool_call", "tool_output"):
        accent_color = colors.role_tool_bg
    elif role == "error":
        accent_color = colors.role_error_bg
    else:
        accent_color = colors.accent_primary if is_user else colors.role_assistant_bg

    if colors.is_neumorphic:
        # Beveled style with colored left accent strip
        if is_user:
            return f"""
                MessageWidget {{
                    background-color: {colors.bg_primary};
                    border-left: 4px solid {accent_color};
                    border-top: 1px solid {colors.shadow_light};
                    border-right: 1px solid {colors.shadow_dark};
                    border-bottom: 1px solid {colors.shadow_dark};
                    border-radius: 8px;
                    margin: 4px 12px;
                    padding: 4px;
                }}
                MessageWidget QLabel {{
                    background-color: transparent;
                    border: none;
                }}
                MessageWidget QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                MessageWidget QTextBrowser {{
                    background-color: transparent;
                    border: none;
                }}
            """
        else:
            return f"""
                MessageWidget {{
                    background-color: {colors.bg_secondary};
                    border-left: 4px solid {accent_color};
                    border-top: 1px solid {colors.shadow_dark};
                    border-right: 1px solid {colors.shadow_light};
                    border-bottom: 1px solid {colors.shadow_light};
                    border-radius: 8px;
                    margin: 4px 12px;
                    padding: 4px;
                }}
                MessageWidget QLabel {{
                    background-color: transparent;
                    border: none;
                }}
                MessageWidget QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                MessageWidget QTextBrowser {{
                    background-color: transparent;
                    border: none;
                }}
            """
    else:
        # Standard flat style
        border_color = accent_color

        return f"""
            MessageWidget {{
                background-color: {colors.bg_secondary};
                border-left: 3px solid {border_color};
                border-top: none;
                border-right: none;
                border-bottom: none;
                border-radius: 0px;
                margin: 2px 8px;
                padding: 0px;
            }}
            MessageWidget QLabel {{
                background-color: transparent;
                border: none;
            }}
            MessageWidget QPushButton {{
                background-color: transparent;
                border: none;
            }}
            MessageWidget QTextBrowser {{
                background-color: transparent;
                border: none;
            }}
        """


def get_bubble_content_style(is_user: bool) -> str:
    """Get content text style for message card."""
    colors = _theme_manager.current
    return f"""
        QTextBrowser {{
            background-color: transparent;
            color: {colors.text_primary};
            border: none;
            padding: 4px 0px;
            font-family: 'Segoe UI', -apple-system, sans-serif;
            font-size: 14px;
        }}
    """


def get_bubble_header_style(is_user: bool, role_color: str) -> str:
    """Get header style for bubble (role indicator)."""
    return f"""
        QLabel {{
            color: {role_color};
            font-size: 11px;
            font-weight: 600;
            padding: 8px 16px 0px 16px;
            background: transparent;
        }}
    """


def get_shadow_effect_params() -> dict:
    """Get parameters for QGraphicsDropShadowEffect."""
    colors = _theme_manager.current
    is_light = "Light" in colors.name

    if colors.is_neumorphic:
        return {
            "blur_radius": 20,
            "x_offset": 8,
            "y_offset": 8,
            "color": colors.shadow_dark,
        }
    else:
        return {
            "blur_radius": 20 if is_light else 15,
            "x_offset": 0,
            "y_offset": 4 if is_light else 2,
            "color": "rgba(0, 0, 0, 0.15)" if is_light else "rgba(0, 0, 0, 0.3)",
        }
