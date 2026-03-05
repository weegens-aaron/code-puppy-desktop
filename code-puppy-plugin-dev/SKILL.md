---
name: code-puppy-plugin-dev
description: Build plugins for Code Puppy, the agentic coding CLI. Use when creating extensions via lifecycle hooks, adding custom /commands, registering new tools, intercepting shell commands, injecting system prompts, or adding model providers. Triggers on plugin development, hook registration, callback system, or extending code-puppy functionality.
---

# Code Puppy Plugin Development

Build plugins for code-puppy using the callback-based lifecycle hook system.

## Quick Start

Create `~/.code_puppy/plugins/my_plugin/register_callbacks.py`:

```python
from code_puppy.callbacks import register_callback

def _on_startup():
    print("my_plugin loaded!")

register_callback("startup", _on_startup)
```

Restart code-puppy. Plugin loads automatically.

## Plugin Structure

```
my_plugin/
├── __init__.py               # Can be empty
├── register_callbacks.py     # REQUIRED - hook registrations
└── other_modules.py          # Optional logic files
```

**Locations:**
- Built-in: `code_puppy/plugins/<name>/`
- User: `~/.code_puppy/plugins/<name>/`

## Core API

```python
from code_puppy.callbacks import register_callback

# Register at module scope (bottom of file)
register_callback("<phase_name>", callback_function)
```

**Messaging:**
```python
from code_puppy.messaging import emit_info, emit_success, emit_warning, emit_error
```

**Config:**
```python
from code_puppy.config import get_value, set_value
```

## Common Tasks

### Add a /command

```python
def _help():
    return [("mycommand", "Description")]

def _handle(command: str, name: str):
    if name != "mycommand":
        return None  # Not handled
    emit_success("Done!")
    return True  # Handled, no model

register_callback("custom_command_help", _help)
register_callback("custom_command", _handle)
```

### Add a tool

```python
def _register_tool(agent):
    @agent.tool_plain
    async def my_tool(arg: str) -> str:
        """Tool description for LLM."""
        return f"Result: {arg}"

def _tools():
    return [{"name": "my_tool", "register_func": _register_tool}]

register_callback("register_tools", _tools)
```

### Block shell commands

```python
async def _check_cmd(context, command, cwd=None, timeout=60):
    if "dangerous" in command:
        return {"blocked": True, "error_message": "Blocked"}
    return None  # Allow

register_callback("run_shell_command", _check_cmd)
```

### Inject into system prompt

```python
def _inject(model_name, default_prompt, user_prompt):
    return {
        "instructions": f"{default_prompt}\n\nExtra rules here.",
        "user_prompt": user_prompt,
        "handled": False,
    }

register_callback("get_model_system_prompt", _inject)
```

## Hook Categories

| Category | Hooks | Async |
|----------|-------|-------|
| App lifecycle | `startup`, `shutdown` | Yes |
| Agent lifecycle | `invoke_agent`, `agent_exception`, `agent_run_start`, `agent_run_end`, `agent_reload` | Mixed |
| Model config | `load_model_config`, `load_models_config`, `register_model_type`, `register_model_providers`, `get_model_system_prompt` | No |
| Tool calls | `pre_tool_call`, `post_tool_call`, `stream_event` | Yes |
| File ops | `edit_file`, `delete_file`, `file_permission` | No |
| Shell | `run_shell_command` | Yes |
| Commands | `custom_command`, `custom_command_help` | No |
| Registration | `register_tools`, `register_agents`, `register_mcp_catalog_servers`, `register_browser_types` | No |

**Full hook reference:** See [references/hooks.md](references/hooks.md)
**Complete patterns:** See [references/patterns.md](references/patterns.md)

## Best Practices

**Do:**
- Register callbacks at module scope
- Return `None` from commands you don't handle
- Use lazy imports inside callbacks to avoid circular imports
- Wrap risky operations in try/except
- Keep files under 600 lines

**Don't:**
- Block async hooks with sync operations
- Invoke model directly from commands (return string instead)
- Skip error handling (broken plugins shouldn't crash the app)
