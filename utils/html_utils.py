"""HTML utility functions for content rendering."""

import base64
import mimetypes
import os
from typing import Optional


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


def render_image_html(
    image_path: str,
    max_height: int = 300,
    border_color: str = "#444",
    alt_text: Optional[str] = None,
) -> Optional[str]:
    """Render an image as an HTML img tag with embedded base64 data.

    This approach guarantees the image displays in QTextBrowser regardless
    of file:// URL security restrictions.

    Args:
        image_path: Path to the image file (absolute or relative)
        max_height: Maximum height in pixels for resizing (default 300)
        border_color: CSS color for the border (default #444)
        alt_text: Alternative text for the image (defaults to filename)

    Returns:
        HTML string with embedded image, or None if image couldn't be loaded
    """
    # Resolve to absolute path
    if not os.path.isabs(image_path):
        abs_path = os.path.abspath(image_path)
    else:
        abs_path = image_path

    if not os.path.isfile(abs_path):
        return None

    try:
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(abs_path)
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"

        # Read image data
        with open(abs_path, "rb") as f:
            image_data = f.read()

        # Try to resize large images using PIL (if available)
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_data))
            if img.height > max_height:
                ratio = max_height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                # Convert to RGB if necessary (for PNG with alpha)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(output, format="JPEG", quality=85)
                image_data = output.getvalue()
                mime_type = "image/jpeg"
        except ImportError:
            pass  # PIL not available, use original

        # Encode as base64
        b64_data = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_data}"

        # Build alt text
        if alt_text is None:
            alt_text = os.path.basename(image_path)

        return (
            f'<img src="{data_url}" alt="{escape_html(alt_text)}" '
            f'style="max-width: 100%; max-height: {max_height}px; '
            f'border-radius: 4px; border: 1px solid {border_color}; display: block;"/>'
        )

    except Exception:
        return None
