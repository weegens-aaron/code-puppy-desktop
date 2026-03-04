"""Markdown to HTML renderer with syntax highlighting."""

import re
from typing import Optional

import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class CodeBlockExtension(markdown.extensions.Extension):
    """Extension to handle fenced code blocks with syntax highlighting."""

    def extendMarkdown(self, md):
        md.preprocessors.register(
            CodeBlockPreprocessor(md),
            'code_block_highlighter',
            25
        )


class CodeBlockPreprocessor(markdown.preprocessors.Preprocessor):
    """Preprocessor that highlights fenced code blocks."""

    FENCED_BLOCK_RE = re.compile(
        r'^```(?P<lang>\w+)?\s*\n(?P<code>.*?)^```\s*$',
        re.MULTILINE | re.DOTALL
    )

    def __init__(self, md, dark_mode: bool = True):
        super().__init__(md)
        self.dark_mode = dark_mode
        self.formatter = HtmlFormatter(
            style='monokai' if dark_mode else 'default',
            noclasses=True,
            nowrap=False,
            cssclass='highlight'
        )

    def run(self, lines):
        text = '\n'.join(lines)
        text = self.FENCED_BLOCK_RE.sub(self._highlight_match, text)
        return text.split('\n')

    def _highlight_match(self, match):
        lang = match.group('lang') or ''
        code = match.group('code')

        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except ClassNotFound:
            lexer = TextLexer()

        highlighted = highlight(code, lexer, self.formatter)
        return f'\n{highlighted}\n'


class MarkdownRenderer:
    """Renders Markdown to styled HTML for Qt widgets."""

    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self._md = markdown.Markdown(
            extensions=[
                'tables',
                'nl2br',
                CodeBlockExtension(),
            ]
        )

    def render(self, text: str) -> str:
        """Convert markdown to HTML with syntax highlighting."""
        self._md.reset()
        html = self._md.convert(text)
        return self._wrap_html(html)

    def _wrap_html(self, html: str) -> str:
        """Wrap HTML with styles for dark/light theme."""
        if self.dark_mode:
            bg = "#1e1e1e"
            fg = "#e0e0e0"
            code_bg = "#2d2d2d"
            link_color = "#4fc3f7"
            border_color = "#3d3d3d"
        else:
            bg = "#ffffff"
            fg = "#333333"
            code_bg = "#f5f5f5"
            link_color = "#1a73e8"
            border_color = "#e0e0e0"

        return f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: {fg};
    background-color: {bg};
    margin: 0;
    padding: 8px;
}}
p {{
    margin: 0 0 12px 0;
}}
code {{
    background-color: {code_bg};
    padding: 2px 6px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
}}
pre {{
    background-color: {code_bg};
    padding: 12px;
    overflow-x: auto;
    margin: 8px 0;
}}
pre code {{
    background: none;
    padding: 0;
}}
.highlight {{
    background-color: {code_bg};
    padding: 12px;
    overflow-x: auto;
    margin: 8px 0;
}}
.highlight pre {{
    margin: 0;
    padding: 0;
    background: none;
}}
a {{
    color: {link_color};
    text-decoration: none;
}}
a:hover {{
    text-decoration: underline;
}}
h1, h2, h3, h4, h5, h6 {{
    margin: 16px 0 8px 0;
    font-weight: 600;
}}
h1 {{ font-size: 1.5em; }}
h2 {{ font-size: 1.3em; }}
h3 {{ font-size: 1.1em; }}
ul, ol {{
    margin: 8px 0;
    padding-left: 24px;
}}
li {{
    margin: 4px 0;
}}
blockquote {{
    border-left: 4px solid {border_color};
    margin: 8px 0;
    padding: 8px 16px;
    color: #888;
}}
table {{
    border-collapse: collapse;
    margin: 8px 0;
    width: 100%;
}}
th, td {{
    border: 1px solid {border_color};
    padding: 8px;
    text-align: left;
}}
th {{
    background-color: {code_bg};
}}
hr {{
    border: none;
    border-top: 1px solid {border_color};
    margin: 16px 0;
}}
</style>
</head>
<body>
{html}
</body>
</html>
"""

    def render_plain(self, text: str) -> str:
        """Convert markdown to HTML without wrapper (for embedding)."""
        self._md.reset()
        return self._md.convert(text)


# Global instance for convenience
_default_renderer: Optional[MarkdownRenderer] = None


def get_markdown_renderer(dark_mode: bool = True) -> MarkdownRenderer:
    """Get or create the default markdown renderer."""
    global _default_renderer
    if _default_renderer is None or _default_renderer.dark_mode != dark_mode:
        _default_renderer = MarkdownRenderer(dark_mode=dark_mode)
    return _default_renderer


def render_markdown(text: str, dark_mode: bool = True) -> str:
    """Convenience function to render markdown to HTML."""
    return get_markdown_renderer(dark_mode).render(text)
