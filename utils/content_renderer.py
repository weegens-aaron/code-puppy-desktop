"""Content rendering utilities for different message types.

Single Responsibility: Transform content into styled HTML.
CSS and formatting concerns are delegated to separate modules (SoC).
"""

import json
import os
import re
from typing import Any

from utils.html_utils import escape_html, wrap_html_with_css, render_image_html
from utils.error_utils import parse_error_message, get_error_hint
from utils.formatting import (
    format_size, get_file_icon, get_operation_icon
)
from utils import css_styles


class ContentRenderer:
    """Renders various content types to styled HTML.

    This class focuses solely on HTML generation, delegating:
    - CSS styles to css_styles module (SoC)
    - Formatting utilities to formatting module (DRY)

    Tool call rendering uses a registry pattern (Open/Closed principle):
    new tool renderers can be added without modifying render_tool_call().
    """

    # Registry: tool_name -> (renderer_function, icon)
    # Allows extension without modifying render_tool_call() (Open/Closed)
    TOOL_RENDERERS: dict[str, tuple[callable, str]] = {}

    @classmethod
    def register_tool_renderer(cls, *tool_names: str, icon: str = "\U0001F527"):
        """Decorator to register a tool call renderer.

        Usage:
            @ContentRenderer.register_tool_renderer("my_tool", icon="🔧")
            def _render_my_tool(args: dict, icon: str) -> str:
                ...
        """
        def decorator(func):
            for name in tool_names:
                cls.TOOL_RENDERERS[name.lower()] = (func, icon)
            return func
        return decorator

    @staticmethod
    def render_plain_text(text: str) -> str:
        """Render plain text with HTML escaping."""
        escaped = escape_html(text)
        return wrap_html_with_css(escaped, css_styles.get_plain_text_css())

    @staticmethod
    def render_error(error_message: str, error_type: str = "Error") -> str:
        """Render an error message prominently.

        Args:
            error_message: The error message text
            error_type: Type of error (e.g., "API Error", "Connection Error")

        Returns:
            HTML string with styled error display
        """
        # Parse error message for structured display using shared utility
        parsed = parse_error_message(error_message)

        # Build the main message
        main_message = parsed["body"] or parsed["raw_message"]

        # Build details section
        details_parts = []
        if parsed["status_code"]:
            details_parts.append(f"<b>Status:</b> {escape_html(parsed['status_code'])}")
        if parsed["model_name"]:
            details_parts.append(f"<b>Model:</b> {escape_html(parsed['model_name'])}")

        details_html = ""
        if details_parts:
            details_html = f'<div class="error-details">{" &bull; ".join(details_parts)}</div>'

        # Get hint using shared utility
        hint = get_error_hint(error_message) or ""
        hint_html = f'<div class="error-hint">{escape_html(hint)}</div>' if hint else ''

        body = f'''
            <div class="error-container">
                <div class="error-header">
                    <span class="error-icon">\u26A0\uFE0F</span>
                    <span class="error-title">{escape_html(error_type)}</span>
                </div>
                <div class="error-message">{escape_html(main_message)}</div>
                {details_html}
                {hint_html}
            </div>
        '''
        return wrap_html_with_css(body, css_styles.get_error_css())

    @staticmethod
    def render_thinking(text: str) -> str:
        """Render thinking content (monospace)."""
        escaped = escape_html(text)
        return wrap_html_with_css(escaped, css_styles.get_thinking_css())

    @staticmethod
    def render_json(text: str) -> str:
        """Render JSON with syntax highlighting."""
        try:
            parsed = json.loads(text)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            formatted = text

        try:
            from pygments import highlight
            from pygments.lexers import JsonLexer
            from pygments.formatters import HtmlFormatter

            formatter = HtmlFormatter(style='monokai', noclasses=True, nowrap=False)
            highlighted = highlight(formatted, JsonLexer(), formatter)
        except Exception:
            highlighted = escape_html(formatted)

        return wrap_html_with_css(highlighted, css_styles.get_code_css())

    @staticmethod
    def render_markdown(text: str) -> str:
        """Render markdown to HTML with syntax highlighting."""
        def highlight_code(match):
            lang = match.group(1) or ''
            code = match.group(2)
            try:
                from pygments import highlight
                from pygments.lexers import get_lexer_by_name, TextLexer
                from pygments.formatters import HtmlFormatter
                from pygments.util import ClassNotFound

                try:
                    lexer = get_lexer_by_name(lang) if lang else TextLexer()
                except ClassNotFound:
                    lexer = TextLexer()
                formatter = HtmlFormatter(style='monokai', noclasses=True, nowrap=False)
                highlighted = highlight(code, lexer, formatter)
            except Exception:
                highlighted = escape_html(code)
            return f'<div class="code-block">{highlighted}</div>'

        text = re.sub(
            r'```(\w+)?\n(.*?)```',
            highlight_code,
            text,
            flags=re.DOTALL
        )

        try:
            import markdown
            md = markdown.Markdown(extensions=['tables', 'nl2br'])
            body = md.convert(text)
        except Exception:
            body = escape_html(text)

        return wrap_html_with_css(body, css_styles.get_markdown_css())

    @staticmethod
    def _render_diff_lines(diff_text: str) -> list[str]:
        """Render diff lines to HTML parts (DRY helper).

        Args:
            diff_text: Unified diff text

        Returns:
            List of HTML strings for diff lines
        """
        html_parts = []
        if not diff_text:
            html_parts.append('<div class="diff-line diff-context">-- no changes --</div>')
            return html_parts

        for line in diff_text.split('\n'):
            if not line:
                continue
            # Skip diff headers
            if line.startswith(('---', '+++', '@@', 'diff ', 'index ')):
                continue

            if line.startswith('+'):
                html_parts.append(
                    f'<div class="diff-line diff-add">'
                    f'<span class="marker">+ </span>{escape_html(line[1:])}</div>'
                )
            elif line.startswith('-'):
                html_parts.append(
                    f'<div class="diff-line diff-remove">'
                    f'<span class="marker">- </span>{escape_html(line[1:])}</div>'
                )
            else:
                content = line[1:] if line.startswith(' ') else line
                html_parts.append(
                    f'<div class="diff-line diff-context">'
                    f'<span class="marker">  </span>{escape_html(content)}</div>'
                )

        return html_parts

    @staticmethod
    def render_diff(diff_text: str, operation: str = "modify", filepath: str = "") -> str:
        """Render a unified diff with syntax highlighting."""
        icon = get_operation_icon(operation)

        html_parts = [
            '<div class="panel-header">',
            f'<span class="icon">{icon}</span>',
            f'<span class="operation">{operation.upper()}</span> ',
            f'<span class="filepath">{escape_html(filepath)}</span>',
            '</div>',
            '<div class="diff-content">'
        ]

        html_parts.extend(ContentRenderer._render_diff_lines(diff_text))

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_diff_css())

    @staticmethod
    def render_file_edit(
        filepath: str,
        operation: str = "modify",
        success: bool = True,
        message: str = "",
        diff_text: str = "",
        changed: bool = True,
    ) -> str:
        """Render a file edit result with diff or status.
        
        Args:
            filepath: Path to the edited file
            operation: Type of operation (create, modify, delete, write)
            success: Whether the operation succeeded
            message: Status message from the operation
            diff_text: Unified diff text (if available)
            changed: Whether the file was actually changed
        
        Returns:
            HTML string with styled file edit display
        """
        icon = get_operation_icon(operation)
        
        # Status indicator
        if not success:
            status_icon = "\u2717"  # X mark
            status_color = "#f87171"  # Red
            status_text = "Failed"
        elif not changed:
            status_icon = "\u2713"  # Checkmark
            status_color = "#a0a0a0"  # Gray
            status_text = "No changes"
        else:
            status_icon = "\u2713"  # Checkmark
            status_color = "#4ade80"  # Green
            # Proper past tense for each operation
            past_tense = {
                "create": "Created",
                "modify": "Modified",
                "delete": "Deleted",
                "write": "Written",
            }
            status_text = past_tense.get(operation.lower(), "Done")
        
        html_parts = [
            '<div class="panel-header">',
            f'<span class="icon">{icon}</span>',
            f'<span class="operation">{operation.upper()}</span> ',
            f'<span class="filepath">{escape_html(filepath)}</span>',
            f'<span class="status" style="margin-left: 12px; color: {status_color};">',
            f'{status_icon} {status_text}</span>',
            '</div>',
        ]
        
        # Show diff if available (using shared helper)
        if diff_text and changed:
            html_parts.append('<div class="diff-content">')
            html_parts.extend(ContentRenderer._render_diff_lines(diff_text))
            html_parts.append('</div>')
        
        # Always show message if available
        if message:
            html_parts.append(
                f'<div class="panel-meta" style="padding: 4px 12px; color: #a0a0a0;">'
                f'{escape_html(message)}</div>'
            )
        
        return wrap_html_with_css(''.join(html_parts), css_styles.get_diff_css())

    @staticmethod
    def render_shell_command(
        command: str,
        output: str = "",
        exit_code: int = 0,
        cwd: str = "",
        duration: float = 0.0,
        background: bool = False
    ) -> str:
        """Render shell command output."""
        bg_indicator = ' <span style="color:#d946ef">[BACKGROUND]</span>' if background else ''
        html_parts = [
            '<div class="panel-header">',
            '<span class="banner">SHELL COMMAND</span> ',
            f'\U0001F680 <span class="command">$ {escape_html(command)}</span>',
            bg_indicator,
            '</div>'
        ]

        meta_parts = []
        if cwd:
            meta_parts.append(f'\U0001F4C2 {escape_html(cwd)}')
        if duration > 0:
            meta_parts.append(f'\u23f1 {duration:.2f}s')
        if meta_parts:
            html_parts.append(f'<div class="panel-meta">{" | ".join(meta_parts)}</div>')

        if output:
            status_class = "error" if exit_code != 0 else ""
            html_parts.append(f'<div class="shell-output {status_class}">{escape_html(output)}</div>')

        if exit_code != 0:
            html_parts.append(f'<div class="panel-meta error">\u2717 Exit code: {exit_code}</div>')
        elif output:
            html_parts.append('<div class="panel-meta success">\u2713 Success</div>')

        return wrap_html_with_css(''.join(html_parts), css_styles.get_shell_css())

    @staticmethod
    def render_file_listing(
        directory: str,
        entries: list[dict[str, Any]],
        recursive: bool = False,
        total_size: int = 0,
        dir_count: int = 0,
        file_count: int = 0
    ) -> str:
        """Render a directory listing."""
        rec_flag = " (recursive)" if recursive else ""
        html_parts = [
            '<div class="panel-header">',
            '<span class="banner">DIRECTORY LISTING</span> ',
            f'\U0001F4C2 <span class="directory">{escape_html(directory)}</span>',
            f'<span style="color:#a0a0a0">{rec_flag}</span>',
            '</div>',
            '<div class="panel-content">'
        ]

        for entry in entries:
            path = entry.get('path', '')
            is_dir = entry.get('type') == 'dir'
            size = entry.get('size', 0)
            name = os.path.basename(path) or path
            icon = get_file_icon(path, is_dir)
            entry_class = "directory" if is_dir else "file"

            size_str = ""
            if not is_dir and size > 0:
                size_str = f' <span class="file-size">({format_size(size)})</span>'

            dir_suffix = "/" if is_dir else ""
            html_parts.append(
                f'<div class="file-entry {entry_class}">'
                f'<span class="icon">{icon}</span>'
                f'{escape_html(name)}{dir_suffix}{size_str}</div>'
            )

        html_parts.append('</div>')
        html_parts.append(
            f'<div class="listing-summary">'
            f'\U0001F4C1 {dir_count} directories, \U0001F4C4 {file_count} files '
            f'({format_size(total_size)} total)</div>'
        )

        return wrap_html_with_css(''.join(html_parts), css_styles.get_file_listing_css())

    @staticmethod
    def render_grep_results(
        search_term: str,
        directory: str,
        matches: list[dict[str, Any]],
        total_matches: int = 0
    ) -> str:
        """Render grep/search results."""
        html_parts = [
            '<div class="panel-header">',
            '<span class="banner">GREP</span> ',
            f'\U0001F4C2 {escape_html(directory)} for ',
            f'<span class="search-term">\'{escape_html(search_term)}\'</span>',
            '</div>',
            '<div class="panel-content">'
        ]

        if not matches:
            html_parts.append(
                f'<div style="color:#a0a0a0">No matches found for \'{escape_html(search_term)}\'</div>'
            )
        else:
            by_file: dict[str, list] = {}
            for match in matches:
                fp = match.get('file_path', 'unknown')
                by_file.setdefault(fp, []).append(match)

            for filepath, file_matches in sorted(by_file.items()):
                match_word = "match" if len(file_matches) == 1 else "matches"
                html_parts.append(
                    f'<div class="grep-file">'
                    f'\U0001F4C4 <span class="filepath">{escape_html(filepath)}</span> '
                    f'<span class="count">({len(file_matches)} {match_word})</span></div>'
                )

                for match in file_matches:
                    line_num = match.get('line_number', 0)
                    content = match.get('line_content', '')
                    highlighted = re.sub(
                        f'({re.escape(search_term)})',
                        r'<span class="highlight">\1</span>',
                        escape_html(content),
                        flags=re.IGNORECASE
                    )
                    html_parts.append(
                        f'<div class="grep-match">'
                        f'<span class="line-num">{line_num:4d}</span> \u2502 '
                        f'<span class="content">{highlighted}</span></div>'
                    )

            file_count = len(by_file)
            file_word = "file" if file_count == 1 else "files"
            match_word = "match" if total_matches == 1 else "matches"
            html_parts.append(
                f'<div class="grep-summary">'
                f'Found {total_matches} {match_word} across {file_count} {file_word}</div>'
            )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_grep_css())

    @staticmethod
    def render_file_header(path: str, line_info: str = "") -> str:
        """Render a file read header."""
        line_part = f' <span class="line-info">({line_info})</span>' if line_info else ''
        body = (
            f'<div class="file-header">'
            f'<span class="banner">READ FILE</span> '
            f'\U0001F4C2 <span class="filepath">{escape_html(path)}</span>'
            f'{line_part}</div>'
        )
        return wrap_html_with_css(body, css_styles.get_file_header_css())

    @classmethod
    def render_tool_call(cls, tool_name: str, tool_args: str | dict) -> str:
        """Render a tool call with formatted arguments.

        Uses registry pattern - new renderers can be added via
        @ContentRenderer.register_tool_renderer() decorator.

        Args:
            tool_name: Name of the tool being called
            tool_args: Tool arguments (JSON string or dict)

        Returns:
            HTML string with styled tool call
        """
        # Parse args if string
        if isinstance(tool_args, str):
            try:
                args = json.loads(tool_args) if tool_args.strip() else {}
            except json.JSONDecodeError:
                # JSON incomplete (streaming) - try partial extraction
                args = {"_raw": tool_args}
        else:
            args = tool_args or {}

        # Normalize tool name for matching
        tool_lower = tool_name.lower()

        # Look up renderer in registry
        if tool_lower in cls.TOOL_RENDERERS:
            renderer, icon = cls.TOOL_RENDERERS[tool_lower]
            return renderer(tool_name, args, icon)

        # Fallback to generic renderer
        return cls._render_generic_tool_call(tool_name, args, "\U0001F527")

    @staticmethod
    def _extract_file_path_from_partial(text: str) -> str:
        """Extract file_path from partial/streaming JSON."""
        # Try to find file_path in incomplete JSON
        patterns = [
            r'"file_path"\s*:\s*"([^"]+)"',
            r'"path"\s*:\s*"([^"]+)"',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ""

    @staticmethod
    def _render_edit_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render edit_file, write_file, or create_file tool call."""
        # Check for partial/streaming JSON
        raw_json = args.get("_raw", "")

        # Handle nested payload structure
        payload = args.get("payload", args)
        file_path = payload.get("file_path", payload.get("path", ""))

        # If no file_path from parsed JSON, try extracting from raw
        if not file_path and raw_json:
            file_path = ContentRenderer._extract_file_path_from_partial(raw_json)

        html_parts = [
            '<div class="tool-content">',
        ]

        # Show file path if we have it
        if file_path:
            html_parts.append(
                f'<div class="tool-param">'
                f'<span class="param-name">file:</span>'
                f'<span class="param-value filepath">{escape_html(file_path)}</span>'
                f'</div>'
            )

        # Check for different parameter formats
        replacements = payload.get("replacements", [])
        content = payload.get("content", "")
        old_string = payload.get("old_string", payload.get("old_str", ""))
        new_string = payload.get("new_string", payload.get("new_str", ""))

        if replacements:
            # Edit with replacements array - show compact summary
            change_count = len(replacements)
            html_parts.append(
                f'<div class="tool-param" style="color:#a0a0a0">'
                f'{change_count} replacement{"s" if change_count > 1 else ""}...</div>'
            )

        elif content:
            # Write/create with full content - show compact summary
            content_lines = content.split('\n')
            line_count = len(content_lines)
            html_parts.append(
                f'<div class="tool-param" style="color:#a0a0a0">'
                f'Writing {line_count} lines...</div>'
            )

        elif new_string:
            # Single edit with old_string/new_string - show compact summary
            html_parts.append(
                f'<div class="tool-param" style="color:#a0a0a0">'
                f'Applying edit...</div>'
            )

        elif raw_json:
            # Streaming - show indicator that content is being received
            html_parts.append(
                '<div class="tool-param" style="color:#a0a0a0">'
                '<span style="color:#4fc3f7">\u270D\uFE0F</span> Writing content...'
                '</div>'
            )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_shell_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render shell command tool call."""
        command = args.get("command", "")

        html_parts = [
            '<div class="tool-content">',
            f'<div class="tool-param">'
            f'<span class="param-value code">$ {escape_html(command)}</span>'
            f'</div>',
            '</div>'
        ]
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_read_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render read_file tool call."""
        file_path = args.get("file_path", args.get("path", "unknown"))
        start_line = args.get("start_line", args.get("offset"))
        end_line = args.get("end_line", args.get("limit"))

        line_info = ""
        if start_line or end_line:
            if start_line and end_line:
                line_info = f" (lines {start_line}-{end_line})"
            elif start_line:
                line_info = f" (from line {start_line})"

        html_parts = [
            '<div class="tool-content">',
            f'<div class="tool-param">'
            f'<span class="param-value filepath">{escape_html(file_path)}{line_info}</span>'
            f'</div>',
            '</div>'
        ]
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_list_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render list_directory tool call."""
        path = args.get("path", args.get("directory", "."))
        recursive = args.get("recursive", False)

        rec_flag = " (recursive)" if recursive else ""

        html_parts = [
            '<div class="tool-content">',
            f'<div class="tool-param">'
            f'<span class="param-value directory">{escape_html(path)}{rec_flag}</span>'
            f'</div>',
            '</div>'
        ]
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_search_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render grep/search tool call."""
        pattern = args.get("pattern", args.get("query", ""))
        path = args.get("path", args.get("directory", "."))

        html_parts = [
            '<div class="tool-content">',
            f'<div class="tool-param">'
            f'<span class="param-name">pattern:</span>'
            f'<span class="param-value code">{escape_html(pattern)}</span>'
            f'</div>',
            f'<div class="tool-param">'
            f'<span class="param-name">in:</span>'
            f'<span class="param-value directory">{escape_html(path)}</span>'
            f'</div>',
            '</div>'
        ]
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_skill_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render skill-related tool calls."""
        tool_lower = tool_name.lower()
        html_parts = ['<div class="tool-content">']

        if tool_lower == "list_or_search_skills":
            query = args.get("query", "")
            if query:
                html_parts.append(
                    f'<div class="tool-param">'
                    f'<span class="param-name">search:</span>'
                    f'<span class="param-value code">{escape_html(query)}</span>'
                    f'</div>'
                )
            else:
                html_parts.append(
                    '<div class="tool-param">'
                    '<span style="color:#a0a0a0;">Listing all available skills...</span>'
                    '</div>'
                )
        elif tool_lower == "activate_skill":
            skill_name = args.get("skill_name", "")
            if skill_name:
                html_parts.append(
                    f'<div class="tool-param">'
                    f'<span class="param-name">skill:</span>'
                    f'<span class="param-value" style="color:#4ade80;">{escape_html(skill_name)}</span>'
                    f'</div>'
                )
            else:
                html_parts.append(
                    '<div class="tool-param">'
                    '<span style="color:#a0a0a0;">Activating skill...</span>'
                    '</div>'
                )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_reasoning_tool_call(args: dict, icon: str) -> str:
        """Render agent_share_your_reasoning tool call."""
        reasoning = args.get("reasoning", "")
        next_steps = args.get("next_steps", [])

        # Handle next_steps being a string (wrap in list) or None
        if next_steps is None:
            next_steps = []
        elif isinstance(next_steps, str):
            next_steps = [next_steps] if next_steps else []

        html_parts = [
            '<div class="tool-content">',
            f'<div class="reasoning-text">{escape_html(reasoning)}</div>',
        ]

        if next_steps:
            html_parts.append('<div class="next-steps">')
            html_parts.append('<div class="label">Next steps:</div>')
            html_parts.append('<ul>')
            # Show ALL steps - no truncation
            for step in next_steps:
                html_parts.append(f'<li>{escape_html(step)}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_image_tool_call(args: dict, icon: str) -> str:
        """Render load_image_for_analysis tool call with embedded image preview."""
        image_path = args.get("image_path", "")

        html_parts = [
            '<div class="tool-content">',
            f'<div class="tool-param">'
            f'<span class="param-value filepath">{escape_html(image_path)}</span>'
            f'</div>',
        ]

        # Render the image using shared utility
        img_html = render_image_html(image_path)
        if img_html:
            html_parts.append(
                f'<div class="image-preview" style="margin-top: 8px;">{img_html}</div>'
            )
        elif image_path:
            html_parts.append(
                '<div class="tool-param" style="color: #a0a0a0; font-style: italic;">'
                '(image not found or failed to load)'
                '</div>'
            )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_ask_user_question_call(args: dict, icon: str) -> str:
        """Render ask_user_question tool call with formatted questions."""
        html_parts = [
            '<div class="tool-content">',
        ]

        # Get questions from args
        questions = args.get("questions", [])
        raw_json = args.get("_raw", "")

        if questions:
            for i, q in enumerate(questions):
                header = q.get("header", f"Q{i+1}")
                question_text = q.get("question", "")
                options = q.get("options", [])
                multi = q.get("multi_select", q.get("multiSelect", False))

                # Question header with icon
                html_parts.append(
                    f'<div class="tool-param" style="margin-top: 8px;">'
                    f'<span style="color: #f0b060; font-weight: bold;">{icon} {escape_html(header)}</span>'
                    f'{"  (multi-select)" if multi else ""}'
                    f'</div>'
                )

                # Question text
                if question_text:
                    html_parts.append(
                        f'<div style="margin-left: 16px; color: #e0e0e0; margin-bottom: 4px;">'
                        f'{escape_html(question_text)}'
                        f'</div>'
                    )

                # Options
                if options:
                    html_parts.append('<div style="margin-left: 24px;">')
                    for opt in options[:6]:  # Limit to 6 options
                        label = opt.get("label", "")
                        desc = opt.get("description", "")
                        html_parts.append(
                            f'<div style="color: #a0c0ff; padding: 2px 0;">'
                            f'\u2022 {escape_html(label)}'
                        )
                        if desc:
                            html_parts.append(
                                f'<span style="color: #808080; font-size: 0.9em;"> - {escape_html(desc[:50])}</span>'
                            )
                        html_parts.append('</div>')
                    if len(options) > 6:
                        html_parts.append(
                            f'<div style="color: #808080; font-style: italic;">...and {len(options) - 6} more</div>'
                        )
                    html_parts.append('</div>')

            # Summary
            html_parts.append(
                f'<div style="color: #808080; margin-top: 8px; font-style: italic;">'
                f'{len(questions)} question{"s" if len(questions) > 1 else ""} - awaiting user response...'
                f'</div>'
            )
        elif raw_json:
            # Partial/streaming - show simplified message
            html_parts.append(
                '<div class="tool-param">'
                '<span style="color: #f0b060;">Preparing questions...</span>'
                '</div>'
            )
        else:
            html_parts.append(
                '<div class="tool-param" style="color: #808080;">(no questions)</div>'
            )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def _render_generic_tool_call(tool_name: str, args: dict, icon: str) -> str:
        """Render generic tool call with key-value params."""
        html_parts = [
            '<div class="tool-content">',
        ]

        # Show params (limit to 5)
        for i, (key, value) in enumerate(list(args.items())[:5]):
            # Format value
            if isinstance(value, str):
                if len(value) > 100:
                    display_value = value[:100] + "..."
                else:
                    display_value = value
            elif isinstance(value, (list, dict)):
                display_value = json.dumps(value, ensure_ascii=False)
                if len(display_value) > 100:
                    display_value = display_value[:100] + "..."
            else:
                display_value = str(value)

            html_parts.append(
                f'<div class="tool-param">'
                f'<span class="param-name">{escape_html(key)}:</span>'
                f'<span class="param-value">{escape_html(display_value)}</span>'
                f'</div>'
            )

        if len(args) > 5:
            html_parts.append(
                f'<div class="tool-param" style="color:#a0a0a0">'
                f'...and {len(args) - 5} more params</div>'
            )

        if not args:
            html_parts.append(
                '<div class="tool-param" style="color:#a0a0a0">(no arguments)</div>'
            )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_tool_call_css())

    @staticmethod
    def render_skill_list(
        skills: list[dict[str, Any]],
        total_count: int = 0,
        query: str = "",
        error: str | None = None
    ) -> str:
        """Render a list of available skills.

        Args:
            skills: List of skill dicts with name, description, tags, etc.
            total_count: Total number of skills found
            query: Search query used (if any)
            error: Error message if skills couldn't be loaded

        Returns:
            HTML string with styled skill list
        """
        html_parts = []

        # Header
        if query:
            html_parts.append(
                '<div class="panel-header">'
                '<span class="banner">SKILLS</span> '
                f'Search: <span class="search-term">\'{escape_html(query)}\'</span>'
                '</div>'
            )
        else:
            html_parts.append(
                '<div class="panel-header">'
                '<span class="banner">SKILLS</span> '
                'Available Skills'
                '</div>'
            )

        # Error case
        if error:
            html_parts.append(
                f'<div class="panel-content">'
                f'<div class="no-skills" style="color:#f87171;">\u26A0\uFE0F {escape_html(error)}</div>'
                f'</div>'
            )
            return wrap_html_with_css(''.join(html_parts), css_styles.get_skill_list_css())

        # No skills found
        if not skills:
            msg = f"No skills found for '{escape_html(query)}'" if query else "No skills available"
            html_parts.append(
                f'<div class="panel-content">'
                f'<div class="no-skills">\U0001F50D {msg}</div>'
                f'</div>'
            )
            return wrap_html_with_css(''.join(html_parts), css_styles.get_skill_list_css())

        # Skill entries
        html_parts.append('<div class="skill-list">')
        for skill in skills[:20]:  # Limit to 20 skills
            name = skill.get("name", "Unknown")
            description = skill.get("description", "No description")
            tags = skill.get("tags", [])
            version = skill.get("version", "")
            author = skill.get("author", "")

            html_parts.append('<div class="skill-entry">')
            html_parts.append(f'<div class="skill-name">\U0001F3AF {escape_html(name)}</div>')
            html_parts.append(f'<div class="skill-description">{escape_html(description)}</div>')

            # Tags
            if tags:
                html_parts.append('<div class="skill-tags">')
                for tag in tags[:5]:  # Limit to 5 tags
                    html_parts.append(f'<span class="skill-tag">{escape_html(tag)}</span>')
                if len(tags) > 5:
                    html_parts.append(f'<span class="skill-tag">+{len(tags) - 5} more</span>')
                html_parts.append('</div>')

            # Meta info
            meta_parts = []
            if version:
                meta_parts.append(f"v{escape_html(version)}")
            if author:
                meta_parts.append(f"by {escape_html(author)}")
            if meta_parts:
                html_parts.append(f'<div class="skill-meta">{" • ".join(meta_parts)}</div>')

            html_parts.append('</div>')

        html_parts.append('</div>')

        # Summary
        if len(skills) > 20:
            html_parts.append(
                f'<div class="skills-summary">'
                f'Showing 20 of {total_count} skills'
                f'</div>'
            )
        else:
            skill_word = "skill" if total_count == 1 else "skills"
            html_parts.append(
                f'<div class="skills-summary">'
                f'\U0001F3AF Found {total_count} {skill_word}'
                f'</div>'
            )

        return wrap_html_with_css(''.join(html_parts), css_styles.get_skill_list_css())

    @staticmethod
    def render_skill_activate(
        skill_name: str,
        content: str = "",
        resources: list[str] | None = None,
        error: str | None = None
    ) -> str:
        """Render skill activation result.

        Args:
            skill_name: Name of the activated skill
            content: Full skill content (SKILL.md)
            resources: List of available resource files
            error: Error message if activation failed

        Returns:
            HTML string with styled activation result
        """
        resources = resources or []
        html_parts = [
            '<div class="panel-header">',
            '<span class="banner">SKILL ACTIVATED</span> ',
            f'\U0001F680 <span style="color:#4ade80">{escape_html(skill_name)}</span>',
            '</div>',
        ]

        # Error case
        if error:
            html_parts.append(
                f'<div class="panel-content">'
                f'<div style="color:#f87171; padding:12px;">'
                f'\u26A0\uFE0F {escape_html(error)}'
                f'</div></div>'
            )
            return wrap_html_with_css(''.join(html_parts), css_styles.get_skill_activate_css())

        html_parts.append('<div class="skill-activated">')

        # Success status
        html_parts.append(
            '<div class="status">'
            '\u2713 Skill loaded successfully'
            '</div>'
        )

        # Resources
        if resources:
            html_parts.append('<div class="skill-resources">')
            html_parts.append(f'<div class="label">\U0001F4C1 Available Resources ({len(resources)})</div>')
            for resource in resources[:10]:  # Limit to 10
                resource_name = os.path.basename(resource) if '/' in resource or '\\' in resource else resource
                html_parts.append(f'<div class="resource">\U0001F4C4 {escape_html(resource_name)}</div>')
            if len(resources) > 10:
                html_parts.append(f'<div class="resource" style="color:#a0a0a0">...and {len(resources) - 10} more</div>')
            html_parts.append('</div>')

        # Content preview
        if content:
            # Show first 500 chars as preview
            preview = content[:500]
            if len(content) > 500:
                preview += "..."
            html_parts.append(
                '<div class="skill-content-preview">'
                '<div class="label">Instructions Preview</div>'
                f'<div class="content">{escape_html(preview)}</div>'
                '</div>'
            )

        html_parts.append('</div>')
        return wrap_html_with_css(''.join(html_parts), css_styles.get_skill_activate_css())


# =============================================================================
# Tool Renderer Registrations (Open/Closed principle)
# =============================================================================

def _register_tool_renderers():
    """Register all built-in tool renderers."""
    R = ContentRenderer.register_tool_renderer

    # File operations
    @R("edit", "edit_file", "write", "write_file", "create_file", icon="\u270f\ufe0f")
    def edit_renderer(tool_name, args, icon):
        return ContentRenderer._render_edit_tool_call(tool_name, args, icon)

    @R("read", "read_file", "view_file", icon="\U0001F4C4")
    def read_renderer(tool_name, args, icon):
        return ContentRenderer._render_read_tool_call(tool_name, args, icon)

    @R("delete_file", icon="\U0001F5D1")
    def delete_renderer(tool_name, args, icon):
        return ContentRenderer._render_generic_tool_call(tool_name, args, icon)

    # Shell commands
    @R("run_shell_command", "execute_command", "shell", "bash", icon="\U0001F680")
    def shell_renderer(tool_name, args, icon):
        return ContentRenderer._render_shell_tool_call(tool_name, args, icon)

    # Directory operations
    @R("list_directory", "list_files", "ls", "glob", icon="\U0001F4C1")
    def list_renderer(tool_name, args, icon):
        return ContentRenderer._render_list_tool_call(tool_name, args, icon)

    # Search operations
    @R("grep", "search_files", "search", "find_in_files", icon="\U0001F50D")
    def search_renderer(tool_name, args, icon):
        return ContentRenderer._render_search_tool_call(tool_name, args, icon)

    # Agent reasoning
    @R("agent_share_your_reasoning", icon="\U0001F4AD")
    def reasoning_renderer(tool_name, args, icon):
        return ContentRenderer._render_reasoning_tool_call(args, icon)

    # Skills
    @R("list_or_search_skills", "activate_skill", icon="\U0001F3AF")
    def skill_renderer(tool_name, args, icon):
        return ContentRenderer._render_skill_tool_call(tool_name, args, icon)

    # Image loading
    @R("load_image_for_analysis", icon="\U0001F5BC")
    def image_renderer(tool_name, args, icon):
        return ContentRenderer._render_image_tool_call(args, icon)

    # User questions
    @R("ask_user_question", icon="\u2753")
    def question_renderer(tool_name, args, icon):
        return ContentRenderer._render_ask_user_question_call(args, icon)


# Register on module load
_register_tool_renderers()
