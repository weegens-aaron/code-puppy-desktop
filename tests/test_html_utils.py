"""Tests for HTML utility functions."""

import pytest

from utils.html_utils import escape_html, wrap_html_body, wrap_html_with_css


class TestEscapeHtml:
    """Tests for escape_html function."""

    def test_escapes_ampersand(self):
        """Test ampersand is escaped."""
        assert escape_html("a & b") == "a &amp; b"

    def test_escapes_less_than(self):
        """Test less-than is escaped."""
        assert escape_html("a < b") == "a &lt; b"

    def test_escapes_greater_than(self):
        """Test greater-than is escaped."""
        assert escape_html("a > b") == "a &gt; b"

    def test_converts_newlines_to_br(self):
        """Test newlines are converted to <br> tags."""
        assert escape_html("line1\nline2") == "line1<br>line2"

    def test_preserves_double_spaces(self):
        """Test double spaces are converted to nbsp."""
        assert escape_html("word  word") == "word&nbsp;&nbsp;word"

    def test_handles_empty_string(self):
        """Test empty string returns empty string."""
        assert escape_html("") == ""

    def test_handles_plain_text(self):
        """Test plain text passes through unchanged."""
        assert escape_html("hello world") == "hello world"

    def test_handles_complex_input(self):
        """Test complex input with multiple escapes."""
        input_text = "<script>alert('xss')</script>\n  test & more"
        result = escape_html(input_text)
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
        assert "<br>" in result
        assert "&nbsp;&nbsp;" in result
        assert "&amp;" in result

    def test_handles_multiple_newlines(self):
        """Test multiple newlines are handled."""
        assert escape_html("a\n\nb") == "a<br><br>b"


class TestWrapHtmlBody:
    """Tests for wrap_html_body function."""

    def test_wraps_content_in_html(self):
        """Test content is wrapped in HTML structure."""
        result = wrap_html_body("<p>Hello</p>")
        assert "<html>" in result
        assert "</html>" in result
        assert "<body>" in result or "<body " in result
        assert "</body>" in result
        assert "<p>Hello</p>" in result

    def test_without_style(self):
        """Test body tag without style attribute."""
        result = wrap_html_body("content")
        assert "<body>" in result
        assert "style=" not in result.split("<body>")[0]

    def test_with_style(self):
        """Test body tag with style attribute."""
        result = wrap_html_body("content", style="color: red;")
        assert 'style="color: red;"' in result

    def test_handles_empty_content(self):
        """Test handles empty content."""
        result = wrap_html_body("")
        assert "<html>" in result
        assert "</html>" in result


class TestWrapHtmlWithCss:
    """Tests for wrap_html_with_css function."""

    def test_includes_style_block(self):
        """Test CSS is included in style block."""
        css = "body { color: red; }"
        result = wrap_html_with_css("<p>test</p>", css)
        assert "<style>" in result
        assert "</style>" in result
        assert "body { color: red; }" in result

    def test_includes_head_section(self):
        """Test head section is present."""
        result = wrap_html_with_css("content", "css")
        assert "<head>" in result
        assert "</head>" in result

    def test_content_in_body(self):
        """Test content is in body section."""
        result = wrap_html_with_css("<p>content</p>", "css")
        # Content should be between body tags
        body_start = result.find("<body>")
        body_end = result.find("</body>")
        assert "<p>content</p>" in result[body_start:body_end]

    def test_proper_document_structure(self):
        """Test proper HTML document structure order."""
        result = wrap_html_with_css("content", "css")
        html_pos = result.find("<html>")
        head_pos = result.find("<head>")
        style_pos = result.find("<style>")
        body_pos = result.find("<body>")

        assert html_pos < head_pos < style_pos < body_pos
