"""CSS styles for content rendering.

Separates CSS concerns from rendering logic (SoC).
Uses composable base styles to avoid repetition (DRY).
"""

from ..styles import COLORS


# =============================================================================
# Base style fragments (DRY - reusable components)
# =============================================================================

def _body_base(
    color: str = COLORS.text_primary,
    font_family: str = "'Segoe UI', sans-serif",
    font_size: str = "14px",
    line_height: str = "1.5"
) -> str:
    """Base body styles used by all content types."""
    return f"""
        body {{
            margin: 0;
            color: {color};
            font-family: {font_family};
            font-size: {font_size};
            line-height: {line_height};
        }}
    """


def _monospace_body(color: str = COLORS.text_primary) -> str:
    """Monospace body style for code/terminal content."""
    return _body_base(
        color=color,
        font_family="'Consolas', 'Monaco', monospace",
        font_size="13px",
        line_height="1.5"
    )


def _panel_header() -> str:
    """Common header style for tool output panels."""
    return """
        .panel-header {
            padding: 8px 12px;
            background-color: #1e3a5f;
            border-radius: 6px 6px 0 0;
        }
        .panel-header .banner { color: white; font-weight: bold; }
        .panel-header .icon { margin-right: 8px; }
    """


def _panel_content() -> str:
    """Common content area style for tool output panels."""
    return f"""
        .panel-content {{
            background-color: {COLORS.bg_code};
            border-radius: 0 0 6px 6px;
            padding: 8px 12px;
        }}
    """


def _panel_meta() -> str:
    """Common meta/summary row style."""
    return f"""
        .panel-meta {{
            padding: 4px 12px;
            background-color: #162a40;
            color: {COLORS.text_secondary};
            font-size: 12px;
        }}
    """


def _success_error() -> str:
    """Success/error color classes."""
    return """
        .success { color: #4ade80; }
        .error { color: #f87171; }
    """


def _filepath_styles() -> str:
    """Common filepath styling."""
    return """
        .filepath { color: #60a5fa; }
        .directory { color: #60a5fa; }
    """


# =============================================================================
# Composed CSS for each content type
# =============================================================================

PLAIN_TEXT_CSS = _body_base()

THINKING_CSS = _monospace_body(color="#c4b99a")

CODE_CSS = _monospace_body(color="#b0bec5") + """
    pre {
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
"""

MARKDOWN_CSS = _body_base(line_height="1.6") + f"""
    p {{ margin: 0 0 12px 0; }}
    p:last-child {{ margin-bottom: 0; }}
    strong {{ color: #ffffff; }}
    em {{ color: #b0b0b0; }}
    code {{
        background-color: {COLORS.bg_code};
        color: {COLORS.text_code};
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
    }}
    .code-block {{
        background-color: {COLORS.bg_code};
        border-radius: 6px;
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
    h1 {{ font-size: 1.4em; color: #ffffff; margin: 16px 0 8px 0; }}
    h2 {{ font-size: 1.2em; color: #ffffff; margin: 14px 0 6px 0; }}
    h3 {{ font-size: 1.1em; color: #ffffff; margin: 12px 0 4px 0; }}
    ul, ol {{ margin: 8px 0; padding-left: 24px; }}
    li {{ margin: 4px 0; }}
    a {{ color: {COLORS.accent_info}; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    blockquote {{
        border-left: 3px solid {COLORS.accent_info};
        margin: 8px 0;
        padding: 4px 12px;
        color: {COLORS.text_secondary};
    }}
    table {{ border-collapse: collapse; margin: 8px 0; }}
    th, td {{ border: 1px solid {COLORS.border_subtle}; padding: 6px 12px; }}
    th {{ background-color: {COLORS.bg_secondary}; }}
    hr {{ border: none; border-top: 1px solid {COLORS.border_subtle}; margin: 12px 0; }}
"""

DIFF_CSS = _monospace_body() + _panel_header() + f"""
    .panel-header .operation {{ color: #4fc3f7; font-weight: bold; }}
    .panel-header .filepath {{ color: #60a5fa; }}
    .diff-content {{
        background-color: {COLORS.bg_code};
        border-radius: 0 0 6px 6px;
        padding: 8px 0;
        overflow-x: auto;
    }}
    .diff-line {{
        padding: 1px 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
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

SHELL_CSS = (
    _monospace_body() +
    _panel_header() +
    _panel_meta() +
    _success_error() +
    f"""
    .panel-header .command {{ color: #4fc3f7; }}
    .shell-output {{
        background-color: {COLORS.bg_code};
        border-radius: 0 0 6px 6px;
        padding: 8px 12px;
        color: {COLORS.text_secondary};
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 300px;
        overflow-y: auto;
    }}
"""
)

FILE_LISTING_CSS = (
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
    .file-entry.file {{ color: #4ade80; }}
    .file-size {{ color: {COLORS.text_secondary}; font-size: 12px; }}
    .listing-summary {{
        padding: 8px 12px;
        background-color: {COLORS.bg_secondary};
        border-radius: 0 0 6px 6px;
        color: {COLORS.text_secondary};
        font-size: 12px;
    }}
"""
)

GREP_CSS = (
    _monospace_body() +
    _panel_header() +
    _panel_content() +
    _filepath_styles() +
    f"""
    .panel-header .search-term {{ color: #fbbf24; }}
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
    .grep-match .highlight {{ color: #fbbf24; font-weight: bold; }}
    .grep-summary {{
        padding: 8px 0 0 0;
        color: {COLORS.text_secondary};
        font-size: 12px;
    }}
"""
)

FILE_HEADER_CSS = (
    _body_base(font_size="13px") +
    f"""
    .file-header {{
        padding: 8px 12px;
        background-color: #1e3a5f;
        border-radius: 6px;
    }}
    .file-header .banner {{ color: white; font-weight: bold; }}
    .file-header .filepath {{ color: #60a5fa; }}
    .file-header .line-info {{ color: {COLORS.text_secondary}; }}
"""
)

# CSS for tool call display (no header - MessageWidget provides it)
TOOL_CALL_CSS = (
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
        color: #fbbf24;
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
        border-radius: 3px;
    }}
    .tool-preview {{
        margin-top: 8px;
        padding: 8px;
        background-color: {COLORS.bg_secondary};
        border-radius: 4px;
        border-left: 3px solid #4fc3f7;
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
    .tool-preview .old {{ color: #f87171; }}
    .tool-preview .new {{ color: #4ade80; }}
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

# CSS for error display
ERROR_CSS = (
    _body_base(font_size="13px") +
    f"""
    .error-container {{
        padding: 12px;
        background-color: #3a1e1e;
        border-radius: 6px;
        border-left: 4px solid #f87171;
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
        color: #f87171;
        font-weight: bold;
        font-size: 14px;
    }}
    .error-message {{
        color: {COLORS.text_secondary};
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
        line-height: 1.4;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    .error-hint {{
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid #5c2a2a;
        color: {COLORS.text_muted};
        font-size: 11px;
    }}
"""
)

# CSS for skill list output
SKILL_LIST_CSS = (
    _body_base(font_size="13px", line_height="1.6") +
    _panel_header() +
    _panel_content() +
    f"""
    .panel-header .search-term {{ color: #fbbf24; }}
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
        color: #4ade80;
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
        color: #60a5fa;
        padding: 2px 8px;
        border-radius: 12px;
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
        border-radius: 0 0 6px 6px;
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

# CSS for skill activation output
SKILL_ACTIVATE_CSS = (
    _body_base(font_size="13px", line_height="1.6") +
    _panel_header() +
    _panel_content() +
    _success_error() +
    f"""
    .skill-activated {{
        padding: 12px;
    }}
    .skill-activated .skill-name {{
        color: #4ade80;
        font-weight: bold;
        font-size: 16px;
    }}
    .skill-activated .status {{
        margin-top: 8px;
        padding: 8px 12px;
        background-color: #1e3a1e;
        border-radius: 4px;
        color: #4ade80;
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
        color: #60a5fa;
        font-size: 12px;
    }}
    .skill-content-preview {{
        margin-top: 12px;
        padding: 8px 12px;
        background-color: {COLORS.bg_secondary};
        border-radius: 4px;
        border-left: 3px solid #4ade80;
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
