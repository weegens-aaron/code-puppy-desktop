# Code Puppy Lifecycle Hooks Reference

Complete reference for all 27 lifecycle hooks available in code-puppy's plugin system.

## Table of Contents

- [Application Lifecycle](#application-lifecycle)
- [Agent Lifecycle](#agent-lifecycle)
- [Model Configuration](#model-configuration)
- [Tool Calls](#tool-calls)
- [File Operations](#file-operations)
- [Shell Commands](#shell-commands)
- [Custom Commands](#custom-commands)
- [Registration Hooks](#registration-hooks)
- [Other Hooks](#other-hooks)

---

## Application Lifecycle

### startup

**When:** Application boot, after the plugin loader runs
**Async:** Yes
**Signature:** `() -> None`
**Use for:** One-time initialization, creating directories, loading caches

```python
from code_puppy.callbacks import register_callback

async def _on_startup():
    from pathlib import Path
    data_dir = Path.home() / ".my_plugin_data"
    data_dir.mkdir(parents=True, exist_ok=True)

register_callback("startup", _on_startup)
```

### shutdown

**When:** Application is exiting gracefully
**Async:** Yes
**Signature:** `() -> None`
**Use for:** Flushing buffers, closing connections, cleanup

```python
async def _on_shutdown():
    global _db_conn
    if _db_conn:
        _db_conn.close()
        _db_conn = None

register_callback("shutdown", _on_shutdown)
```

---

## Agent Lifecycle

### invoke_agent

**When:** An agent is invoked (sub-agent calls, etc.)
**Async:** Yes
**Signature:** `(*args, **kwargs) -> None`
**Use for:** Logging, analytics, auditing agent invocations

```python
async def _on_invoke_agent(*args, **kwargs):
    agent_name = kwargs.get("agent_name") or (args[0] if args else "unknown")
    logger.info("Agent invoked: %s", agent_name)

register_callback("invoke_agent", _on_invoke_agent)
```

### agent_exception

**When:** An agent run throws an unhandled exception
**Async:** Yes
**Signature:** `(exception: Exception, *args, **kwargs) -> None`
**Use for:** Error reporting, crash telemetry, Sentry integration

```python
async def _on_agent_exception(exception, *args, **kwargs):
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exception)
    except ImportError:
        pass

register_callback("agent_exception", _on_agent_exception)
```

### agent_run_start

**When:** At the top of `run_with_mcp`, before the agent task is created
**Async:** Yes
**Signature:** `(agent_name: str, model_name: str, session_id: str | None) -> None`
**Use for:** Starting background tasks, resource allocation, heartbeats

```python
_run_timers = {}

async def _on_agent_run_start(agent_name, model_name, session_id=None):
    key = session_id or "default"
    _run_timers[key] = time.monotonic()

register_callback("agent_run_start", _on_agent_run_start)
```

### agent_run_end

**When:** At the end of `run_with_mcp` (in `finally` — always fires)
**Async:** Yes
**Signature:**
```python
(
    agent_name: str,
    model_name: str,
    session_id: str | None = None,
    success: bool = True,
    error: Exception | None = None,
    response_text: str | None = None,
    metadata: dict | None = None,
) -> None
```
**Use for:** Stopping heartbeats, logging duration, workflow orchestration

```python
async def _on_agent_run_end(
    agent_name, model_name, session_id=None,
    success=True, error=None, response_text=None, metadata=None,
):
    key = session_id or "default"
    start = _run_timers.pop(key, None)
    if start:
        elapsed = time.monotonic() - start
        status = "ok" if success else "fail"
        logger.info("%s %s finished in %.1fs [%s]", status, agent_name, elapsed, model_name)

register_callback("agent_run_end", _on_agent_run_end)
```

### agent_reload

**When:** The current agent is being reloaded (e.g. after model switch)
**Async:** No (sync)
**Signature:** `(*args, **kwargs) -> None`
**Use for:** Clearing caches, re-initializing state that depends on the model

```python
def _on_agent_reload(*args, **kwargs):
    _prompt_cache.clear()
    logger.debug("Prompt cache cleared on agent reload")

register_callback("agent_reload", _on_agent_reload)
```

---

## Model Configuration

### load_model_config

**When:** A single model's configuration is loaded
**Async:** No (sync)
**Signature:** `(*args, **kwargs) -> Any`
**Use for:** Patching individual model configs at load time

```python
def _patch_model_config(*args, **kwargs):
    config = args[0] if args else kwargs.get("config", {})
    if isinstance(config, dict) and "custom_endpoint" in config:
        endpoint = config["custom_endpoint"]
        if isinstance(endpoint, dict) and "url" not in endpoint:
            endpoint["url"] = "https://llm-proxy.corp.internal/v1"
    return config

register_callback("load_model_config", _patch_model_config)
```

### load_models_config

**When:** The full model catalogue is loaded (merged with `models.json`)
**Async:** No (sync)
**Signature:** `() -> dict`
**Use for:** Injecting additional model definitions from an external source

```python
def _load_extra_models():
    return {
        "internal-llama-70b": {
            "name": "llama-70b",
            "context_length": 131072,
            "custom_endpoint": {
                "url": "https://llm.corp.internal/v1",
                "api_key_env": "INTERNAL_LLM_KEY",
            },
        }
    }

register_callback("load_models_config", _load_extra_models)
```

### register_model_type

**When:** Model factory is resolving a model config with a custom `type` field
**Async:** No (sync)
**Signature:** `() -> list[dict]`
**Use for:** Teaching Code Puppy how to instantiate a new kind of model

Each dict has `"type"` (str) and `"handler"` (callable receiving `model_name, model_config, config`).

```python
def _create_ollama_model(model_name, model_config, config):
    from pydantic_ai.models.openai import OpenAIModel
    return OpenAIModel(
        model_name=model_config["name"],
        base_url=model_config.get("base_url", "http://localhost:11434/v1"),
        api_key="ollama",
    )

def _register_model_types():
    return [{"type": "ollama", "handler": _create_ollama_model}]

register_callback("register_model_type", _register_model_types)
```

### register_model_providers

**When:** Model providers are being collected during model factory init
**Async:** No (sync)
**Signature:** `() -> dict[str, type]`
**Use for:** Registering an entirely new model provider class

```python
def _register_providers():
    from my_plugin.groq_model import GroqModel
    return {"groq": GroqModel}

register_callback("register_model_providers", _register_providers)
```

### get_model_system_prompt

**When:** The system prompt is being resolved for a specific model
**Async:** No (sync)
**Signature:** `(model_name: str, default_system_prompt: str, user_prompt: str) -> dict | None`
**Use for:** Overriding or augmenting the system prompt per model

Return a dict with `"instructions"`, `"user_prompt"`, and `"handled"` keys, or `None` to pass through.

```python
def _custom_system_prompt(model_name, default_system_prompt, user_prompt):
    if not model_name.startswith("prod-"):
        return None
    return {
        "instructions": f"{default_system_prompt}\n\nSAFETY: Never suggest deleting production data.",
        "user_prompt": user_prompt,
        "handled": False,  # Let other handlers also process
    }

register_callback("get_model_system_prompt", _custom_system_prompt)
```

---

## Tool Calls

### pre_tool_call

**When:** Immediately before any tool is executed by the agent
**Async:** Yes
**Signature:** `(tool_name: str, tool_args: dict, context: Any = None) -> Any`
**Use for:** Logging, argument validation, metrics, modifying args

```python
_tool_starts = {}

async def _on_pre_tool_call(tool_name, tool_args, context=None):
    call_id = id(tool_args)
    _tool_starts[call_id] = time.monotonic()
    logger.debug("Tool starting: %s", tool_name)

register_callback("pre_tool_call", _on_pre_tool_call)
```

### post_tool_call

**When:** Immediately after a tool finishes executing
**Async:** Yes
**Signature:**
```python
(
    tool_name: str,
    tool_args: dict,
    result: Any,
    duration_ms: float,
    context: Any = None,
) -> Any
```
**Use for:** Metrics collection, result logging, post-processing

```python
async def _on_post_tool_call(tool_name, tool_args, result, duration_ms, context=None):
    if duration_ms > 5000:
        logger.warning("Slow tool: %s took %.1fs", tool_name, duration_ms / 1000)

register_callback("post_tool_call", _on_post_tool_call)
```

### stream_event

**When:** During agent response streaming (tokens generated, tool calls, etc.)
**Async:** Yes
**Signature:** `(event_type: str, event_data: Any, agent_session_id: str | None) -> None`
**Use for:** Real-time UIs, progress indicators, streaming to external systems

```python
async def _on_stream_event(event_type, event_data, agent_session_id=None):
    if event_type == "text_delta":
        await websocket_broadcast({
            "type": "token",
            "text": event_data,
            "session": agent_session_id,
        })

register_callback("stream_event", _on_stream_event)
```

---

## File Operations

### edit_file

**When:** A file edit operation is about to be performed
**Async:** No (sync)
**Signature:** `(*args, **kwargs) -> Any`
**Use for:** Logging edits, enforcing policies, triggering side-effects

```python
def _on_edit_file(*args, **kwargs):
    file_path = args[0] if args else kwargs.get("file_path", "unknown")
    logger.info("File edited: %s", file_path)

register_callback("edit_file", _on_edit_file)
```

### delete_file

**When:** A file deletion is about to be performed
**Async:** No (sync)
**Signature:** `(*args, **kwargs) -> Any`
**Use for:** Blocking deletions of protected files, audit logging

```python
def _on_delete_file(*args, **kwargs):
    file_path = str(args[0]) if args else kwargs.get("file_path", "")
    if file_path.endswith(".lock"):
        emit_error(f"Blocked deletion of lock file: {file_path}")
        return {"blocked": True}
    return None

register_callback("delete_file", _on_delete_file)
```

### file_permission

**When:** Before a file operation, to ask the user for permission
**Async:** No (sync)
**Signature:**
```python
(
    context: Any,
    file_path: str,
    operation: str,
    preview: str | None = None,
    message_group: str | None = None,
    operation_data: Any = None,
) -> bool
```
**Use for:** Interactive approval prompts, diff previews, auto-approve rules

Return `True` to grant permission, `False` to deny.

```python
def _auto_approve_test_files(context, file_path, operation, preview=None,
                              message_group=None, operation_data=None):
    if "/tests/" in file_path or file_path.startswith("tests/"):
        return True  # Always allow test file edits
    return None  # Fall through to default handler

register_callback("file_permission", _auto_approve_test_files)
```

---

## Shell Commands

### run_shell_command

**When:** Before a shell command is executed
**Async:** Yes
**Signature:** `(context: Any, command: str, cwd: str | None, timeout: int) -> dict | None`
**Use for:** Safety checks, command rewriting, blocking dangerous commands

Return `None` to allow the command. Return a dict with `{"blocked": True, ...}` to prevent execution.

```python
async def _check_shell_command(context, command, cwd=None, timeout=60):
    if "git push" in command and "main" in command:
        emit_error("Blocked: direct push to main is not allowed")
        return {"blocked": True, "error_message": "Push to main blocked by policy"}
    return None

register_callback("run_shell_command", _check_shell_command)
```

---

## Custom Commands

### custom_command

**When:** A user types a `/slash` command that isn't a built-in
**Async:** No (sync)
**Signature:** `(command: str, name: str) -> True | str | None`
**Use for:** Adding new slash commands from plugins

Return values:
- `None` — not handled, try next plugin
- `True` — handled, no model invocation
- `str` — handled, string sent to model as user input

```python
def _handle_custom_command(command, name):
    if name != "ping":
        return None
    emit_success("Pong!")
    return True

register_callback("custom_command", _handle_custom_command)
```

### custom_command_help

**When:** The `/help` menu is being built
**Async:** No (sync)
**Signature:** `() -> list[tuple[str, str]]`
**Use for:** Advertising your plugin's slash commands in `/help`

Return a list of `(command_name, description)` tuples.

```python
def _custom_help():
    return [
        ("ping", "Check if Code Puppy is alive"),
        ("stats", "Show session statistics"),
    ]

register_callback("custom_command_help", _custom_help)
```

---

## Registration Hooks

### register_tools

**When:** The agent is being constructed and tool registration is collected
**Async:** No (sync)
**Signature:** `() -> list[dict]`
**Use for:** Adding new tools the LLM can call

Each dict must have `"name"` (str) and `"register_func"` (callable that takes an agent instance).

```python
def _register_my_tool(agent):
    @agent.tool_plain
    async def query_database(sql: str) -> str:
        """Run a read-only SQL query against the project database."""
        # ... implementation ...
        return result

def _register_tools():
    return [{"name": "query_database", "register_func": _register_my_tool}]

register_callback("register_tools", _register_tools)
```

### register_agents

**When:** The agent catalogue is being built
**Async:** No (sync)
**Signature:** `() -> list[dict]`
**Use for:** Registering entirely new agents (Python classes or JSON defs)

```python
def _register_agents():
    from my_plugin.code_review_agent import CodeReviewAgent
    return [
        {"name": "code-reviewer", "class": CodeReviewAgent},
        {"name": "sql-helper", "json_path": "/path/to/sql_agent.json"},
    ]

register_callback("register_agents", _register_agents)
```

### register_mcp_catalog_servers

**When:** The MCP server catalogue/marketplace is being built
**Async:** No (sync)
**Signature:** `() -> list[MCPServerTemplate]`
**Use for:** Adding custom MCP servers to the install catalogue

```python
def _register_mcp_servers():
    from code_puppy.command_line.mcp.base import MCPServerTemplate
    return [
        MCPServerTemplate(
            name="internal-jira",
            description="Query JIRA issues via MCP",
            command="npx",
            args=["-y", "@corp/mcp-jira"],
            env={"JIRA_URL": "https://jira.corp.internal"},
        ),
    ]

register_callback("register_mcp_catalog_servers", _register_mcp_servers)
```

### register_browser_types

**When:** Browser manager is collecting available browser providers
**Async:** No (sync)
**Signature:** `() -> dict[str, callable]`
**Use for:** Adding custom browser backends (stealth, headless, etc.)

Each value is an async init function: `async (manager, **kwargs) -> None`.

```python
async def _init_camoufox(manager, **kwargs):
    from camoufox.async_api import AsyncCamoufox
    cm = AsyncCamoufox(headless=True)
    browser = await cm.__aenter__()
    manager._browser = browser
    manager._context = await browser.new_context()
    manager._page = await manager._context.new_page()

def _register_browser_types():
    return {"camoufox": _init_camoufox}

register_callback("register_browser_types", _register_browser_types)
```

---

## Other Hooks

### version_check

**When:** Periodic or on-demand version check
**Async:** Yes
**Signature:** `(*args, **kwargs) -> None`
**Use for:** Custom update channels, enterprise version pinning

### load_prompt

**When:** The system prompt is being assembled
**Async:** No (sync)
**Signature:** `() -> str | None`
**Use for:** Appending extra instructions, injecting context

```python
def _inject_project_rules():
    from pathlib import Path
    rules_file = Path(".puppy-rules.md")
    if rules_file.exists():
        return rules_file.read_text()
    return None

register_callback("load_prompt", _inject_project_rules)
```

### get_motd

**When:** The message-of-the-day banner is being rendered
**Async:** No (sync)
**Signature:** `() -> tuple[str, str] | None`
**Use for:** Custom banners, team announcements, tip of the day

Return `(message, version_string)` or `None`.

```python
import random

_TIPS = [
    "Tip: Use /set yolo_mode true to skip confirmations",
    "Tip: Use /agent to switch between agents",
]

def _get_motd():
    return (random.choice(_TIPS), "")

register_callback("get_motd", _get_motd)
```

### message_history_processor_start

**When:** At the start of `message_history_accumulator`, before dedup
**Async:** No (sync)
**Signature:**
```python
(
    agent_name: str,
    session_id: str | None,
    message_history: list,
    incoming_messages: list,
) -> None
```
**Use for:** Observing raw incoming messages, analytics, debugging

### message_history_processor_end

**When:** After dedup and filtering in `message_history_accumulator`
**Async:** No (sync)
**Signature:**
```python
(
    agent_name: str,
    session_id: str | None,
    message_history: list,
    messages_added: int,
    messages_filtered: int,
) -> None
```
**Use for:** Dedup analytics, context-window monitoring, alerting

```python
def _on_history_end(agent_name, session_id, message_history, messages_added, messages_filtered):
    total = len(message_history)
    if total > 200:
        emit_warning(f"Context growing large ({total} messages). Consider /clear.")

register_callback("message_history_processor_end", _on_history_end)
```
