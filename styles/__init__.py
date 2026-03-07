"""Styles package for the desktop application.

This package provides a single source of truth for all colors, fonts,
and widget styles used throughout the desktop app.

All exports are available directly from this package:
    from styles import COLORS, get_theme_manager, get_button_style, ...
"""

# Colors and theme management
from styles.colors import (
    ColorScheme,
    THEME_DARK,
    THEME_LIGHT,
    THEME_NEUMORPHIC_DARK,
    THEME_NEUMORPHIC_LIGHT,
    THEMES,
    ThemeManager,
    get_theme_manager,
    COLORS,
)

# Base styles
from styles.base import (
    get_main_window_style,
    get_scroll_area_style,
    get_content_browser_style,
)

# Button styles
from styles.buttons import (
    get_button_style,
    icon_button,
    action_button,
    get_send_button_style,
    get_cancel_button_style,
    get_attach_button_style,
)

# Input styles
from styles.inputs import (
    get_modern_input_container_style,
    get_modern_input_field_style,
)

# Message and role styles
from styles.messages import (
    RoleStyle,
    get_role_style,
    get_thinking_section_style,
    get_tool_call_section_style,
    get_collapsible_toggle_style,
    get_section_icon_style,
    get_section_title_style,
    get_thinking_text_style,
    get_tool_args_text_style,
    get_message_bubble_style,
    get_bubble_content_style,
    get_bubble_header_style,
    get_shadow_effect_params,
)

# Sidebar and file tree styles
from styles.sidebar import (
    get_file_tree_filter_style,
    get_file_tree_view_style,
    get_context_menu_style,
    get_tab_widget_style,
    get_sidebar_container_style,
    get_icon_rail_style,
    get_sidebar_outer_style,
    get_sidebar_toggle_button_style,
    get_sidebar_icon_button_style,
)

# Dialog styles
from styles.dialogs import (
    get_dialog_style,
    get_section_label_style,
    get_panel_title_style,
    get_subsection_label_style,
    get_validation_error_style,
)

# Component styles
from styles.components import (
    get_attachment_chip_style,
    get_attachment_label_style,
    get_attachment_remove_style,
    get_status_label_style,
    get_status_activity_style,
    get_status_separator_style,
    get_progress_bar_style,
    get_toggle_switch_style,
)

# Primitives (DRY building blocks)
from styles.primitives import (
    SIDEBAR_MATERIAL,
    SIDEBAR_HOVER,
    SIDEBAR_SELECTED,
    INSET_DARK,
    INSET_LIGHT,
    flat_icon_label_style,
    inset_container_style,
    inset_panel_style,
)

__all__ = [
    # Colors
    "ColorScheme",
    "THEME_DARK",
    "THEME_LIGHT",
    "THEME_NEUMORPHIC_DARK",
    "THEME_NEUMORPHIC_LIGHT",
    "THEMES",
    "ThemeManager",
    "get_theme_manager",
    "COLORS",
    # Base
    "get_main_window_style",
    "get_scroll_area_style",
    "get_content_browser_style",
    # Buttons
    "get_button_style",
    "icon_button",
    "action_button",
    "get_send_button_style",
    "get_cancel_button_style",
    "get_attach_button_style",
    # Inputs
    "get_modern_input_container_style",
    "get_modern_input_field_style",
    # Messages
    "RoleStyle",
    "get_role_style",
    "get_thinking_section_style",
    "get_tool_call_section_style",
    "get_collapsible_toggle_style",
    "get_section_icon_style",
    "get_section_title_style",
    "get_thinking_text_style",
    "get_tool_args_text_style",
    "get_message_bubble_style",
    "get_bubble_content_style",
    "get_bubble_header_style",
    "get_shadow_effect_params",
    # Sidebar
    "get_file_tree_filter_style",
    "get_file_tree_view_style",
    "get_context_menu_style",
    "get_tab_widget_style",
    "get_sidebar_container_style",
    "get_icon_rail_style",
    "get_sidebar_outer_style",
    "get_sidebar_toggle_button_style",
    "get_sidebar_icon_button_style",
    # Dialogs
    "get_dialog_style",
    "get_section_label_style",
    "get_panel_title_style",
    "get_subsection_label_style",
    "get_validation_error_style",
    # Components
    "get_attachment_chip_style",
    "get_attachment_label_style",
    "get_attachment_remove_style",
    "get_status_label_style",
    "get_status_activity_style",
    "get_status_separator_style",
    "get_progress_bar_style",
    "get_toggle_switch_style",
    # Primitives
    "SIDEBAR_MATERIAL",
    "SIDEBAR_HOVER",
    "SIDEBAR_SELECTED",
    "INSET_DARK",
    "INSET_LIGHT",
    "flat_icon_label_style",
    "inset_container_style",
    "inset_panel_style",
]
