"""CSS styles for content rendering.

Separates CSS concerns from rendering logic (SoC).
Uses composable base styles to avoid repetition (DRY).
All styles are generated dynamically to support theme changes.
"""

from styles import COLORS


# =============================================================================
# Base style fragments (DRY - reusable components)
# =============================================================================

def _body_base(color: str = None, font_family: str = "'Segoe UI', sans-serif",
               font_size: str = "14px", line_height: str = "1") -> str:
    """Base body styles used by all content types."""
    if color is None:
        color = COLORS.text_primary
    return f"""
        body {{
            margin: 0;
            color: {color};
            font-family: {font_family};
            font-size: {font_size};
            line-height: {line_height};
        }}
    """


def _monospace_body(color: str = None) -> str:
    """Monospace body style for code/terminal content."""
    if color is None:
        color = COLORS.text_primary
    return _body_base(
        color=color,
        font_family="'Consolas', 'Monaco', monospace",
        font_size="13px",
        line_height="1.5"
    )


def _panel_header() -> str:
    """Common header style for tool output panels."""
    return f"""
        .panel-header {{
            padding: 8px 12px;
            background-color: {COLORS.bg_tertiary};
        }}
        .panel-header .banner {{ color: {COLORS.text_primary}; font-weight: bold; }}
        .panel-header .icon {{ margin-right: 8px; }}
    """


def _panel_content() -> str:
    """Common content area style for tool output panels."""
    return f"""
        .panel-content {{
            background-color: {COLORS.bg_code};
            padding: 8px 12px;
        }}
    """


def _panel_meta() -> str:
    """Common meta/summary row style."""
    return f"""
        .panel-meta {{
            padding: 4px 12px;
            background-color: {COLORS.bg_tertiary};
            color: {COLORS.text_secondary};
            font-size: 12px;
        }}
    """


def _success_error() -> str:
    """Success/error color classes."""
    return f"""
        .success {{ color: {COLORS.accent_success}; }}
        .error {{ color: {COLORS.accent_error}; }}
    """


def _filepath_styles() -> str:
    """Common filepath styling."""
    return f"""
        .filepath {{ color: {COLORS.accent_primary}; }}
        .directory {{ color: {COLORS.accent_primary}; }}
    """


# =============================================================================
# Dynamic CSS generators for each content type
# =============================================================================

def get_plain_text_css() -> str:
    return _body_base()


def get_thinking_css() -> str:
    return _monospace_body(color=COLORS.text_secondary)


def get_code_css() -> str:
    return _monospace_body(color=COLORS.text_primary) + f"""
    pre {{
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
"""


def get_markdown_css() -> str:
    return _body_base(line_height="1.6") + f"""
    p {{ margin: 0 0 12px 0; }}
    p:last-child {{ margin-bottom: 0; }}
    strong {{ color: {COLORS.text_primary}; }}
    em {{ color: {COLORS.text_secondary}; }}
    code {{
        background-color: {COLORS.bg_code};
        color: {COLORS.text_code};
        padding: 2px 6px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
    }}
    .code-block {{
        background-color: {COLORS.bg_code};
        padding: 12px;
        margin: 8px 0;
        overflow-x: auto;
    }}
    .code-block pre {{
        margin: 0;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        line-height: 1.4;
    }}
    h1 {{ font-size: 1.4em; color: {COLORS.text_primary}; margin: 16px 0 8px 0; }}
    h2 {{ font-size: 1.2em; color: {COLORS.text_primary}; margin: 14px 0 6px 0; }}
    h3 {{ font-size: 1.1em; color: {COLORS.text_primary}; margin: 12px 0 4px 0; }}
    ul, ol {{ margin: 8px 0; padding-left: 24px; }}
    li {{ margin: 4px 0; }}
    a {{ color: {COLORS.accent_primary}; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    blockquote {{
        border-left: 3px solid {COLORS.accent_primary};
        margin: 8px 0;
        padding: 4px 12px;
        color: {COLORS.text_secondary};
    }}
    table {{ border-collapse: collapse; margin: 8px 0; }}
    th, td {{ border: 1px solid {COLORS.border_subtle}; padding: 6px 12px; }}
    th {{ background-color: {COLORS.bg_secondary}; }}
    hr {{ border: none; border-top: 1px solid {COLORS.border_subtle}; margin: 12px 0; }}
"""


def get_diff_css() -> str:
    return _monospace_body() + _panel_header() + f"""
    .panel-header .operation {{ color: {COLORS.accent_primary}; font-weight: bold; }}
    .panel-header .filepath {{ color: {COLORS.accent_primary}; }}
    .diff-content {{
        background-color: {COLORS.bg_code};
        padding: 4px 0;
        overflow-x: auto;
        line-height: 1.3;
    }}
    .diff-line {{
        padding: 0 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
    }}
    .diff-add {{
        background-color: #1e3a1e;
        color: #4ade80;
    }}
    .diff-add .marker {{ color: #22c55e; font-weight: bold; }}
    .diff-remove {{
        background-color: #3a1e1e;
        color: #f87171;
    }}
    .diff-remove .marker {{ color: #ef4444; font-weight: bold; }}
    .diff-context {{
        color: {COLORS.text_secondary};
    }}
"""


def get_shell_css() -> str:
    return (
        _monospace_body() +
        _panel_header() +
        _panel_meta() +
        _success_error() +
        f"""
    .panel-header .command {{ color: {COLORS.accent_primary}; }}
    .shell-output {{
        background-color: {COLORS.bg_code};
        padding: 8px 12px;
        color: {COLORS.text_secondary};
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 300px;
        overflow-y: auto;
    }}
"""
    )


def get_file_listing_css() -> str:
    return (
        _body_base(font_size="13px", line_height="1.6") +
        _panel_header() +
        _panel_content() +
        _filepath_styles() +
        f"""
    .file-entry {{
        padding: 2px 0;
    }}
    .file-entry .icon {{ margin-right: 6px; }}
    .file-entry.directory {{ font-weight: bold; }}
    .file-entry.file {{ color: {COLORS.text_primary}; }}
    .file-size {{ color: {COLORS.text_secondary}; font-size: 12px; }}
    .listing-summary {{
        padding: 8px 12px;
        background-color: {COLORS.bg_secondary};
        color: {COLORS.text_secondary};
        font-size: 12px;
    }}
"""
    )


def get_grep_css() -> str:
    return (
        _monospace_body() +
        _panel_header() +
        _panel_content() +
        _filepath_styles() +
        f"""
    .panel-header .search-term {{ color: {COLORS.accent_warning}; }}
    .grep-file {{
        color: {COLORS.text_secondary};
        padding: 8px 0 4px 0;
        border-bottom: 1px solid {COLORS.border_subtle};
        margin-bottom: 4px;
    }}
    .grep-file .count {{ color: {COLORS.text_muted}; }}
    .grep-match {{
        padding: 2px 0;
    }}
    .grep-match .line-num {{
        color: {COLORS.text_muted};
        min-width: 40px;
        display: inline-block;
    }}
    .grep-match .content {{ color: {COLORS.text_secondary}; }}
    .grep-match .highlight {{ color: {COLORS.accent_warning}; font-weight: bold; }}
    .grep-summary {{
        padding: 8px 0 0 0;
        color: {COLORS.text_secondary};
        font-size: 12px;
    }}
"""
    )


def get_file_header_css() -> str:
    return (
        _body_base(font_size="13px") +
        f"""
    .file-header {{
        padding: 8px 12px;
        background-color: {COLORS.bg_tertiary};
    }}
    .file-header .banner {{ color: {COLORS.text_primary}; font-weight: bold; }}
    .file-header .filepath {{ color: {COLORS.accent_primary}; }}
    .file-header .line-info {{ color: {COLORS.text_secondary}; }}
"""
    )


def get_tool_call_css() -> str:
    return (
        _body_base(font_size="13px") +
        _filepath_styles() +
        f"""
    .tool-content {{
        padding: 4px 0;
    }}
    .tool-param {{
        margin: 4px 0;
        line-height: 1.4;
    }}
    .tool-param .param-name {{
        color: {COLORS.accent_warning};
        font-weight: bold;
    }}
    .tool-param .param-value {{
        color: {COLORS.text_secondary};
        margin-left: 8px;
    }}
    .tool-param .param-value.code {{
        font-family: 'Consolas', 'Monaco', monospace;
        background-color: {COLORS.bg_secondary};
        padding: 2px 6px;
    }}
    .tool-preview {{
        margin-top: 8px;
        padding: 8px;
        background-color: {COLORS.bg_secondary};
        border-left: 3px solid {COLORS.accent_primary};
    }}
    .tool-preview .label {{
        color: {COLORS.text_muted};
        font-size: 11px;
        margin-bottom: 4px;
    }}
    .tool-preview .content {{
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
        color: {COLORS.text_secondary};
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    .tool-preview .old {{ color: {COLORS.accent_error}; }}
    .tool-preview .new {{ color: {COLORS.accent_success}; }}
    .tool-preview .arrow {{ color: {COLORS.text_muted}; margin: 0 8px; }}
    .reasoning-text {{
        color: {COLORS.text_secondary};
        line-height: 1.5;
        margin-bottom: 8px;
    }}
    .next-steps {{
        margin-top: 8px;
    }}
    .next-steps .label {{
        color: {COLORS.text_muted};
        font-size: 11px;
        margin-bottom: 4px;
    }}
    .next-steps ul {{
        margin: 0;
        padding-left: 20px;
        color: {COLORS.text_secondary};
    }}
    .next-steps li {{
        margin: 2px 0;
    }}
"""
    )


def get_error_css() -> str:
    return (
        _body_base(font_size="13px") +
        f"""
    .error-container {{
        padding: 12px;
        background-color: {COLORS.role_error_bg};
        border-left: 4px solid {COLORS.accent_error};
    }}
    .error-header {{
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }}
    .error-icon {{
        font-size: 18px;
        margin-right: 8px;
    }}
    .error-title {{
        color: {COLORS.accent_error};
        font-weight: bold;
        font-size: 14px;
    }}
    .error-message {{
        color: {COLORS.text_primary};
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 8px;
    }}
    .error-details {{
        color: {COLORS.text_muted};
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 11px;
        padding: 6px 8px;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 4px;
        margin-bottom: 8px;
    }}
    .error-details b {{
        color: {COLORS.text_secondary};
    }}
    .error-hint {{
        padding-top: 8px;
        border-top: 1px solid {COLORS.border_subtle};
        color: {COLORS.accent_warning};
        font-size: 12px;
        font-style: italic;
    }}
"""
    )


def get_skill_list_css() -> str:
    return (
        _body_base(font_size="13px", line_height="1.6") +
        _panel_header() +
        _panel_content() +
        f"""
    .panel-header .search-term {{ color: {COLORS.accent_warning}; }}
    .skill-list {{
        padding: 0;
    }}
    .skill-entry {{
        padding: 10px 12px;
        border-bottom: 1px solid {COLORS.border_subtle};
        background-color: {COLORS.bg_secondary};
    }}
    .skill-entry:last-child {{
        border-bottom: none;
    }}
    .skill-entry:hover {{
        background-color: {COLORS.bg_tertiary};
    }}
    .skill-name {{
        color: {COLORS.accent_primary};
        font-weight: bold;
        font-size: 14px;
    }}
    .skill-description {{
        color: {COLORS.text_secondary};
        font-size: 12px;
        margin-top: 4px;
        line-height: 1.4;
    }}
    .skill-tags {{
        margin-top: 6px;
    }}
    .skill-tag {{
        display: inline-block;
        background-color: {COLORS.bg_tertiary};
        color: {COLORS.accent_primary};
        padding: 2px 8px;
        font-size: 11px;
        margin-right: 6px;
    }}
    .skill-meta {{
        color: {COLORS.text_muted};
        font-size: 11px;
        margin-top: 4px;
    }}
    .skills-summary {{
        padding: 8px 12px;
        background-color: {COLORS.bg_secondary};
        color: {COLORS.text_secondary};
        font-size: 12px;
    }}
    .no-skills {{
        padding: 16px;
        color: {COLORS.text_muted};
        text-align: center;
    }}
"""
    )


def get_skill_activate_css() -> str:
    return (
        _body_base(font_size="13px", line_height="1.6") +
        _panel_header() +
        _panel_content() +
        _success_error() +
        f"""
    .skill-activated {{
        padding: 12px;
    }}
    .skill-activated .skill-name {{
        color: {COLORS.accent_primary};
        font-weight: bold;
        font-size: 16px;
    }}
    .skill-activated .status {{
        margin-top: 8px;
        padding: 8px 12px;
        background-color: {COLORS.bg_tertiary};
        color: {COLORS.accent_success};
    }}
    .skill-resources {{
        margin-top: 12px;
    }}
    .skill-resources .label {{
        color: {COLORS.text_muted};
        font-size: 11px;
        margin-bottom: 4px;
    }}
    .skill-resources .resource {{
        padding: 4px 0;
        color: {COLORS.accent_primary};
        font-size: 12px;
    }}
    .skill-content-preview {{
        margin-top: 12px;
        padding: 8px 12px;
        background-color: {COLORS.bg_secondary};
        border-left: 3px solid {COLORS.accent_primary};
        max-height: 200px;
        overflow-y: auto;
    }}
    .skill-content-preview .label {{
        color: {COLORS.text_muted};
        font-size: 11px;
        margin-bottom: 4px;
    }}
    .skill-content-preview .content {{
        color: {COLORS.text_secondary};
        font-size: 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
"""
    )


# =============================================================================
# Backwards compatibility - these call the dynamic functions
# =============================================================================

# These are kept for backwards compatibility but now call functions
# that generate CSS dynamically with current theme colors

class _DynamicCSS:
    """Proxy that generates CSS dynamically."""

    @property
    def PLAIN_TEXT_CSS(self):
        return get_plain_text_css()

    @property
    def THINKING_CSS(self):
        return get_thinking_css()

    @property
    def CODE_CSS(self):
        return get_code_css()

    @property
    def MARKDOWN_CSS(self):
        return get_markdown_css()

    @property
    def DIFF_CSS(self):
        return get_diff_css()

    @property
    def SHELL_CSS(self):
        return get_shell_css()

    @property
    def FILE_LISTING_CSS(self):
        return get_file_listing_css()

    @property
    def GREP_CSS(self):
        return get_grep_css()

    @property
    def FILE_HEADER_CSS(self):
        return get_file_header_css()

    @property
    def TOOL_CALL_CSS(self):
        return get_tool_call_css()

    @property
    def ERROR_CSS(self):
        return get_error_css()

    @property
    def SKILL_LIST_CSS(self):
        return get_skill_list_css()

    @property
    def SKILL_ACTIVATE_CSS(self):
        return get_skill_activate_css()


# Create singleton instance for backwards compatibility
# Access via css_styles.css.PLAIN_TEXT_CSS etc., or use the functions directly
css = _DynamicCSS()
