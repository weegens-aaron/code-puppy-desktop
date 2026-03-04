"""Tool output extraction for desktop UI rendering.

Separates tool result parsing from transport/worker concerns (SoC).
Single responsibility: transform tool results into UI-renderable data.
"""

from typing import Any


class ToolOutputExtractor:
    """Extracts structured output data from tool results.

    Implements Open/Closed principle - add new extractors without modifying
    existing code by registering them in EXTRACTORS.
    """

    # Tool name -> extractor function mapping
    # Allows extension without modifying class (Open/Closed)
    EXTRACTORS: dict[str, callable] = {}

    @classmethod
    def register(cls, *tool_names: str):
        """Decorator to register an extractor for tool names."""
        def decorator(func):
            for name in tool_names:
                cls.EXTRACTORS[name] = func
            return func
        return decorator

    @classmethod
    def extract(
        cls, tool_name: str, tool_args: dict, result: Any
    ) -> tuple[str, dict]:
        """Extract structured output from a tool result.

        Args:
            tool_name: Name of the tool that produced the result
            tool_args: Arguments passed to the tool
            result: The tool's return value

        Returns:
            Tuple of (output_type, metadata) or ("", {}) if not applicable.
        """
        extractor = cls.EXTRACTORS.get(tool_name)
        if extractor:
            return extractor(tool_args, result)
        return "", {}


# =============================================================================
# Extractor implementations (registered via decorator)
# =============================================================================

@ToolOutputExtractor.register("edit_file", "write_file", "create_file", "delete_file")
def _extract_file_edit(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract file edit data from file operation results.
    
    Handles both diff-based edits and content-based writes.
    """
    if not isinstance(result, dict):
        return "", {}
    
    # Get file path from result or args
    filepath = result.get("path", "")
    if not filepath:
        # Try to get from args (handle nested payload structure)
        payload = tool_args.get("payload", tool_args)
        filepath = payload.get("file_path", payload.get("path", ""))
    
    # Determine operation type
    message = result.get("message", "")
    if "created" in message.lower():
        operation = "create"
    elif "deleted" in message.lower():
        operation = "delete"
    elif result.get("diff"):
        operation = "modify"
    else:
        operation = "write"
    
    metadata = {
        "filepath": filepath,
        "operation": operation,
        "success": result.get("success", True),
        "message": message,
        "changed": result.get("changed", True),
    }
    
    # Include diff if available
    if result.get("diff"):
        metadata["diff_text"] = result.get("diff", "")
    
    return "file_edit", metadata


@ToolOutputExtractor.register("run_shell_command", "execute_command", "shell", "bash")
def _extract_shell(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract shell command output."""
    if isinstance(result, dict):
        return "shell", {
            "command": tool_args.get("command", ""),
            "output": result.get("output", result.get("stdout", "")),
            "exit_code": result.get("exit_code", result.get("return_code", 0)),
            "cwd": result.get("cwd", ""),
            "background": result.get("background", False),
        }
    elif isinstance(result, str):
        return "shell", {
            "command": tool_args.get("command", ""),
            "output": result,
            "exit_code": 0,
            "cwd": "",
            "background": False,
        }
    return "", {}


@ToolOutputExtractor.register("list_directory", "list_files", "ls")
def _extract_file_listing(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract directory listing data."""
    if isinstance(result, dict):
        entries = result.get("entries", result.get("files", []))
        return "file_listing", {
            "directory": tool_args.get("path", tool_args.get("directory", ".")),
            "entries": entries,
            "recursive": tool_args.get("recursive", False),
            "total_size": result.get("total_size", 0),
            "dir_count": result.get("dir_count", 0),
            "file_count": result.get("file_count", len(entries)),
        }
    return "", {}


@ToolOutputExtractor.register("grep", "search_files", "search", "find_in_files")
def _extract_grep(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract grep/search results."""
    if isinstance(result, dict):
        matches = result.get("matches", result.get("results", []))
        return "grep", {
            "search_term": tool_args.get("pattern", tool_args.get("query", "")),
            "directory": tool_args.get("path", tool_args.get("directory", ".")),
            "matches": matches,
            "total_matches": result.get("total_matches", len(matches)),
        }
    return "", {}


@ToolOutputExtractor.register("read_file", "view_file", "cat")
def _extract_file_header(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract file read header info."""
    filepath = tool_args.get("file_path", tool_args.get("path", ""))
    if filepath:
        line_info = ""
        if "start_line" in tool_args or "end_line" in tool_args:
            start = tool_args.get("start_line", 1)
            end = tool_args.get("end_line", "")
            line_info = f"lines {start}-{end}" if end else f"from line {start}"
        return "file_header", {
            "filepath": filepath,
            "line_info": line_info,
        }
    return "", {}


@ToolOutputExtractor.register("list_or_search_skills")
def _extract_skill_list(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract skill list results."""
    # Handle Pydantic model or dict
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif hasattr(result, "dict"):
        result = result.dict()

    if isinstance(result, dict):
        skills = result.get("skills", [])
        return "skill_list", {
            "skills": skills,
            "total_count": result.get("total_count", len(skills)),
            "query": result.get("query") or tool_args.get("query", ""),
            "error": result.get("error"),
        }
    return "", {}


@ToolOutputExtractor.register("activate_skill")
def _extract_skill_activate(tool_args: dict, result: Any) -> tuple[str, dict]:
    """Extract skill activation results."""
    # Handle Pydantic model or dict
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif hasattr(result, "dict"):
        result = result.dict()

    if isinstance(result, dict):
        return "skill_activate", {
            "skill_name": result.get("skill_name", tool_args.get("skill_name", "")),
            "content": result.get("content", ""),
            "resources": result.get("resources", []),
            "error": result.get("error"),
        }
    return "", {}
