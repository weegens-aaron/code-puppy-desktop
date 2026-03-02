"""HTML utility functions for content rendering."""


def escape_html(text: str) -> str:
    """Escape HTML special characters and preserve whitespace.

    Args:
        text: Raw text to escape

    Returns:
        HTML-safe text with preserved whitespace
    """
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
        .replace("  ", "&nbsp;&nbsp;"))


def wrap_html_body(content: str, style: str = "") -> str:
    """Wrap content in a basic HTML document structure.

    Args:
        content: HTML content for the body
        style: Optional inline style for the body tag

    Returns:
        Complete HTML document string
    """
    style_attr = f' style="{style}"' if style else ''
    return f"""
    <html>
    <body{style_attr}>
    {content}
    </body>
    </html>
    """


def wrap_html_with_css(content: str, css: str) -> str:
    """Wrap content in HTML with a style block.

    Args:
        content: HTML content for the body
        css: CSS styles to include

    Returns:
        Complete HTML document string with styles
    """
    return f"""
    <html>
    <head>
    <style>
    {css}
    </style>
    </head>
    <body>
    {content}
    </body>
    </html>
    """
