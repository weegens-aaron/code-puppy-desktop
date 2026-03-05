# Code Puppy Plugin Patterns

Common patterns and complete examples for building code-puppy plugins.

## Table of Contents

- [Pattern 1: Custom Slash Command](#pattern-1-custom-slash-command)
- [Pattern 2: Registering Tools](#pattern-2-registering-tools)
- [Pattern 3: Shell Command Interceptor](#pattern-3-shell-command-interceptor)
- [Pattern 4: System Prompt Injection](#pattern-4-system-prompt-injection)
- [Pattern 5: Custom Model Provider](#pattern-5-custom-model-provider)
- [Pattern 6: Tool Call Telemetry](#pattern-6-tool-call-telemetry)
- [Pattern 7: File Permission Handler](#pattern-7-file-permission-handler)
- [Pattern 8: TUI Menu Command](#pattern-8-tui-menu-command)

---

## Pattern 1: Custom Slash Command

Add `/mycommand` and `/mc` alias to code-puppy.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
from code_puppy.messaging import emit_info, emit_success, emit_error

_COMMAND_NAME = "mycommand"
_ALIASES = ("mc",)

def _custom_help():
    """Advertise commands in /help."""
    return [
        ("mycommand", "Do something useful"),
        ("mc", "Alias for /mycommand"),
    ]

def _handle_custom_command(command: str, name: str):
    """Handle /mycommand and /mc.

    Args:
        command: Full command string (e.g., "/mycommand arg1 arg2")
        name: Command name without slash (e.g., "mycommand")

    Returns:
        - None: Not handled, try next plugin
        - True: Handled, no model invocation
        - str: Handled, string sent to model as input
    """
    if name not in (_COMMAND_NAME, *_ALIASES):
        return None

    parts = command.split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else ""

    if not args:
        emit_info("Usage: /mycommand <args>")
        return True

    # Option A: Just emit output, don't invoke model
    emit_success(f"Processed: {args}")
    return True

    # Option B: Return string to send to model
    # return f"Please help me with: {args}"

register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_custom_command)
```

---

## Pattern 2: Registering Tools

Add a new tool that the LLM can call.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback

def _register_my_tool(agent):
    """Register tool on the agent instance."""

    @agent.tool_plain
    async def search_jira(query: str, max_results: int = 10) -> str:
        """Search JIRA issues matching the query.

        Args:
            query: JQL query string
            max_results: Maximum number of results to return

        Returns:
            Formatted list of matching issues
        """
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://jira.company.com/rest/api/2/search",
                params={"jql": query, "maxResults": max_results},
                headers={"Authorization": f"Bearer {os.environ['JIRA_TOKEN']}"}
            ) as resp:
                data = await resp.json()

        issues = data.get("issues", [])
        if not issues:
            return "No issues found."

        lines = []
        for issue in issues:
            key = issue["key"]
            summary = issue["fields"]["summary"]
            status = issue["fields"]["status"]["name"]
            lines.append(f"- {key}: {summary} [{status}]")

        return "\n".join(lines)

def _register_tools():
    return [{"name": "search_jira", "register_func": _register_my_tool}]

register_callback("register_tools", _register_tools)
```

---

## Pattern 3: Shell Command Interceptor

Block or modify shell commands before execution.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
from code_puppy.messaging import emit_error, emit_warning
import re

# Dangerous patterns to block
BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",           # rm -rf /
    r"git\s+push.*--force",     # force push
    r"DROP\s+DATABASE",         # SQL drop
    r":(){ :|:& };:",           # fork bomb
]

# Patterns requiring confirmation (handled elsewhere, just warn here)
WARN_PATTERNS = [
    r"git\s+push.*main",
    r"npm\s+publish",
    r"docker\s+push",
]

async def _check_shell_command(context, command: str, cwd=None, timeout=60):
    """Intercept shell commands for safety.

    Returns:
        None: Allow command
        dict with {"blocked": True, "error_message": str}: Block command
    """
    # Check blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            emit_error(f"Blocked dangerous command matching: {pattern}")
            return {
                "blocked": True,
                "error_message": f"Command blocked by safety policy: {pattern}"
            }

    # Warn on suspicious patterns (but allow)
    for pattern in WARN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            emit_warning(f"Proceeding with sensitive command: {command[:50]}...")
            break

    return None  # Allow

register_callback("run_shell_command", _check_shell_command)
```

---

## Pattern 4: System Prompt Injection

Inject custom instructions into every system prompt.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
from pathlib import Path

def _inject_project_context(model_name, default_system_prompt, user_prompt):
    """Inject project-specific context into system prompt.

    Args:
        model_name: Name of model being used
        default_system_prompt: The base system prompt
        user_prompt: User's message

    Returns:
        dict with instructions/user_prompt/handled, or None to skip
    """
    # Load project rules if they exist
    rules_file = Path(".puppy-rules.md")
    if not rules_file.exists():
        return None

    project_rules = rules_file.read_text()

    enhanced_prompt = f"""{default_system_prompt}

## Project-Specific Rules

{project_rules}
"""

    return {
        "instructions": enhanced_prompt,
        "user_prompt": user_prompt,
        "handled": False,  # Let other handlers also process
    }

register_callback("get_model_system_prompt", _inject_project_context)
```

---

## Pattern 5: Custom Model Provider

Add a new model type that code-puppy can use.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
import os

def _create_ollama_model(model_name, model_config, config):
    """Create an Ollama model instance.

    Args:
        model_name: Name of model (e.g., "ollama-llama3")
        model_config: Config dict for this model from models.json
        config: Full models configuration

    Returns:
        Model instance or None if creation fails
    """
    from pydantic_ai.models.openai import OpenAIModel

    return OpenAIModel(
        model_name=model_config.get("name", "llama3"),
        base_url=model_config.get("base_url", "http://localhost:11434/v1"),
        api_key="ollama",  # Ollama doesn't need a real key
    )

def _load_ollama_models():
    """Add Ollama models to the model catalogue."""
    return {
        "ollama-llama3": {
            "type": "ollama",
            "name": "llama3",
            "context_length": 8192,
            "base_url": "http://localhost:11434/v1",
        },
        "ollama-codellama": {
            "type": "ollama",
            "name": "codellama",
            "context_length": 16384,
            "base_url": "http://localhost:11434/v1",
        },
    }

def _register_model_types():
    return [{"type": "ollama", "handler": _create_ollama_model}]

register_callback("register_model_type", _register_model_types)
register_callback("load_models_config", _load_ollama_models)
```

---

## Pattern 6: Tool Call Telemetry

Track and log all tool calls for analytics.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
import time
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)
_tool_starts = {}
_telemetry_file = Path.home() / ".code_puppy" / "telemetry.jsonl"

async def _on_pre_tool_call(tool_name, tool_args, context=None):
    """Record tool call start."""
    call_id = id(tool_args)
    _tool_starts[call_id] = {
        "tool": tool_name,
        "start": time.time(),
        "args_keys": list(tool_args.keys()),
    }

async def _on_post_tool_call(tool_name, tool_args, result, duration_ms, context=None):
    """Record tool call completion."""
    call_id = id(tool_args)
    start_info = _tool_starts.pop(call_id, None)

    # Log slow tools
    if duration_ms > 5000:
        logger.warning(f"Slow tool: {tool_name} took {duration_ms/1000:.1f}s")

    # Write telemetry
    _telemetry_file.parent.mkdir(parents=True, exist_ok=True)
    with open(_telemetry_file, "a") as f:
        record = {
            "tool": tool_name,
            "duration_ms": duration_ms,
            "success": result is not None,
            "timestamp": time.time(),
        }
        f.write(json.dumps(record) + "\n")

register_callback("pre_tool_call", _on_pre_tool_call)
register_callback("post_tool_call", _on_post_tool_call)
```

---

## Pattern 7: File Permission Handler

Auto-approve certain file operations.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
from pathlib import Path
import fnmatch

# Patterns to auto-approve
AUTO_APPROVE_PATTERNS = [
    "tests/**/*.py",
    "**/*.test.ts",
    "**/*.spec.js",
    ".gitignore",
    "*.md",
]

# Patterns to always deny
DENY_PATTERNS = [
    ".env*",
    "**/*secret*",
    "**/credentials*",
    "**/*.pem",
    "**/*.key",
]

def _file_permission_handler(context, file_path, operation, preview=None,
                             message_group=None, operation_data=None):
    """Handle file permission requests.

    Returns:
        True: Grant permission
        False: Deny permission
        None: Fall through to default handler
    """
    path = Path(file_path)

    # Check deny patterns first
    for pattern in DENY_PATTERNS:
        if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern):
            return False

    # Check auto-approve patterns
    for pattern in AUTO_APPROVE_PATTERNS:
        if fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern):
            return True

    return None  # Fall through to default handler

register_callback("file_permission", _file_permission_handler)
```

---

## Pattern 8: TUI Menu Command

Create a command with an interactive terminal UI.

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
from code_puppy.messaging import emit_info, emit_success

def _custom_help():
    return [("settings", "Open settings menu")]

def _handle_settings_command(command: str, name: str):
    if name != "settings":
        return None

    _show_settings_menu()
    return True

def _show_settings_menu():
    """Display interactive settings menu."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.table import Table
    from code_puppy.config import get_value, set_value

    console = Console()

    while True:
        # Build settings table
        table = Table(title="Current Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        settings = {
            "yolo_mode": get_value("yolo_mode", False),
            "model": get_value("model", "default"),
            "theme": get_value("theme", "dark"),
        }

        for key, value in settings.items():
            table.add_row(key, str(value))

        console.print(table)
        console.print()

        # Menu options
        console.print("[1] Toggle yolo_mode")
        console.print("[2] Change model")
        console.print("[3] Change theme")
        console.print("[q] Exit")
        console.print()

        choice = Prompt.ask("Select option", choices=["1", "2", "3", "q"])

        if choice == "q":
            break
        elif choice == "1":
            current = get_value("yolo_mode", False)
            set_value("yolo_mode", not current)
            emit_success(f"yolo_mode set to {not current}")
        elif choice == "2":
            model = Prompt.ask("Enter model name")
            set_value("model", model)
            emit_success(f"Model set to {model}")
        elif choice == "3":
            theme = Prompt.ask("Enter theme", choices=["dark", "light"])
            set_value("theme", theme)
            emit_success(f"Theme set to {theme}")

register_callback("custom_command_help", _custom_help)
register_callback("custom_command", _handle_settings_command)
```

---

## Multi-Module Plugin Structure

For larger plugins, split into multiple files:

```
my_plugin/
├── __init__.py
├── register_callbacks.py    # Hook registrations only
├── commands.py              # Slash command handlers
├── tools.py                 # Tool implementations
├── config.py                # Plugin configuration
├── menu.py                  # TUI menus (if any)
└── utils.py                 # Shared utilities
```

```python
# register_callbacks.py
from code_puppy.callbacks import register_callback
from .commands import handle_command, command_help
from .tools import register_tools
from .config import on_startup

register_callback("startup", on_startup)
register_callback("custom_command", handle_command)
register_callback("custom_command_help", command_help)
register_callback("register_tools", register_tools)
```

Keep `register_callbacks.py` thin—just registrations and imports.
