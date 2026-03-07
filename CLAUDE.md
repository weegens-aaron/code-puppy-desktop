# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **code-puppy-desktop**, a PySide6-based desktop GUI plugin for the code_puppy AI coding assistant. It provides a graphical chat interface for interacting with code_puppy agents, featuring streaming responses, tool visualization, file attachments, and theming support.

## Running the Application

```bash
# Direct launch (standalone)
python launch.py

# Or via code_puppy CLI (after plugin is installed)
/desktop
```

Dependencies are auto-installed from `requirements.txt` on first launch if missing.

## Architecture

### Core Components

- **app.py** - Main application window (`CodePuppyApp`). Manages UI layout, toolbar/statusbar, user interactions, and coordinates with the agent bridge. Handles streaming events via Qt signals.

- **services/agent_bridge.py** - Thread-safe bridge between GUI and agent. Forwards Qt signals from worker to main thread for UI updates.

- **services/agent_worker.py** - Runs the code_puppy agent in a separate thread with its own asyncio event loop. Handles streaming events via the code_puppy callback system and emits Qt signals. Key signals: `token_received`, `thinking_started/content/complete`, `tool_call_started/complete`, `tool_output_received`.

- **register_callbacks.py** - Plugin registration. Registers `/desktop` command with code_puppy's callback system.

### Widget Hierarchy

- **widgets/sidebar_tabs.py** - `SidebarTabs`: Tabbed container for sidebar panels (Files, Agents, Models, Skills, MCP). Forwards signals from child panels.
- **widgets/file_tree.py** - `FileTree`: File browser with drag-to-attach and context menu
- **widgets/panels/** - Sidebar panel widgets:
  - `agents_panel.py` - Agent selection with list and details view
  - `models_panel.py` - Model selection with list and details view
  - `skills_panel.py` - Skills management with enable/disable toggle
  - `mcp_panel.py` - MCP server management (start/stop/add/remove)
- **widgets/message_list.py** - `MessageListView`: Scrollable container for messages with auto-scroll behavior
- **widgets/message_bubble.py** - `MessageWidget`: Individual message rendering with role-specific styling
- **widgets/thinking_section.py** / **tool_call_section.py** - Collapsible sections for thinking/tool UI

### Data Layer

- **models/data_types.py** - Core data structures: `Message`, `MessageRole`, `ToolOutputType`, `ContentPart`
- **models/message_model.py** - `MessageModel`: Qt model for message storage with add/update signals

### Rendering Pipeline

- **utils/content_renderer.py** - Main renderer: converts messages to HTML, handles markdown, code blocks, diffs, shell output
- **utils/markdown_renderer.py** - Markdown to HTML conversion with Pygments syntax highlighting
- **utils/tool_output_extractor.py** - Extracts structured output from tool results (diffs, file listings, grep results)
- **utils/css_styles.py** - CSS generation for rendered content
- **utils/html_utils.py** - HTML escaping and utilities

### Theming

- **styles.py** - Centralized theme system with `ThemeManager` singleton. Contains 7 preset themes (Dark, Light, Dracula, Nord, Monokai, Solarized Dark, GitHub Dark). Use `get_theme_manager()` to access; widgets should use style functions like `get_main_window_style()` rather than static constants for theme reactivity.

### Dialogs

Located in `windows/dialogs/`:
- `settings_dialog.py` - Theme selection and preferences
- `session_dialog.py` - Session resume functionality
- `help_dialog.py` - Help/keyboard shortcuts
- `mcp_dialog.py` - Contains `AddServerDialog` for adding new MCP servers (used by MCP panel)
- `question_dialog.py` - User question prompts

## Key Patterns

### Threading Model
Agent execution runs in a dedicated thread (`AgentWorker`) with its own asyncio event loop. Communication with the main Qt thread happens via Qt signals. Never call agent methods directly from the main thread.

### Streaming Updates
Token buffering in `app.py` (`_token_buffer` + `_token_timer`) throttles UI updates to every 50ms for performance. Messages are tracked by index (`_assistant_message_index`, `_current_tool_indices`) for in-place updates.

### Theme System
Widgets should call style functions (e.g., `get_send_button_style()`) rather than using static style constants. Register theme change listeners via `ThemeManager.add_listener()` to update styles dynamically.

## Dependencies

- PySide6 >= 6.8.0 (Qt bindings)
- Pygments >= 2.17.0 (syntax highlighting)
- markdown >= 3.5.0 (markdown rendering)
- code_puppy (parent project - provides agents, callbacks, config)
