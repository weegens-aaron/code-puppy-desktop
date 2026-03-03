# code-puppy-desktop

A PySide6-based desktop GUI plugin for the [code_puppy](https://github.com/your-repo/code_puppy) AI coding assistant. Provides a graphical chat interface for interacting with code_puppy agents.

## Features

- **Streaming Chat Interface** - Real-time token streaming with throttled UI updates for smooth performance
- **Tool Visualization** - Collapsible sections showing tool calls, outputs, and agent reasoning
- **File Browser** - Drag-and-drop file attachments with context menu support
- **Multiple Themes** - 7 built-in themes: Dark, Light, Dracula, Nord, Monokai, Solarized Dark, GitHub Dark
- **Agent Selection** - Switch between different code_puppy agents
- **Model Selection** - Choose from available AI models
- **Skills Management** - Enable/disable agent skills
- **MCP Server Management** - Start, stop, add, and remove MCP servers
- **Session Resume** - Continue previous conversations

## Installation

### Prerequisites

- Python 3.10+
- [code_puppy](https://github.com/your-repo/code_puppy) installed

### Quick Start

Clone or copy this plugin to your code_puppy plugins directory:

```bash
# The plugin auto-installs dependencies on first launch
~/.code_puppy/plugins/code-puppy-desktop/
```

## Usage

### Via code_puppy CLI

```bash
# After plugin is registered
/desktop
```

### Standalone Launch

```bash
python ~/.code_puppy/plugins/code-puppy-desktop/launch.py
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Send message |
| `Ctrl+N` | New conversation |
| `Ctrl+O` | Attach file |
| `Ctrl+,` | Open settings |
| `Escape` | Cancel current operation |
| `F1` | Help dialog |

## Architecture

```
code-puppy-desktop/
├── app.py                 # Main application window
├── launch.py              # Standalone launcher
├── main.py                # Entry point
├── register_callbacks.py  # Plugin registration
├── styles.py              # Theme system
├── models/
│   └── data_types.py      # Core data structures
├── services/
│   ├── agent_bridge.py    # Thread-safe GUI/agent bridge
│   └── agent_worker.py    # Background agent thread
├── utils/
│   ├── content_renderer.py    # Message rendering
│   ├── markdown_renderer.py   # Markdown/syntax highlighting
│   ├── tool_output_extractor.py
│   └── html_utils.py
├── widgets/
│   ├── message_list.py    # Chat message container
│   ├── message_bubble.py  # Individual messages
│   ├── file_tree.py       # File browser
│   ├── sidebar_tabs.py    # Tabbed sidebar
│   ├── thinking_section.py
│   ├── tool_call_section.py
│   └── panels/            # Sidebar panel widgets
└── windows/
    └── dialogs/           # Settings, help, etc.
```

### Threading Model

Agent execution runs in a dedicated `QThread` with its own asyncio event loop. Communication with the main Qt thread happens via Qt signals, ensuring thread safety.

### Theme System

Themes are defined in `styles.py` using `ColorScheme` named tuples. Access the current theme via `get_theme_manager()` and register listeners for dynamic updates.

## Dependencies

- PySide6 >= 6.8.0
- Pygments >= 2.17.0
- markdown >= 3.5.0
- code_puppy (parent project)

## License

See the [code_puppy](https://github.com/your-repo/code_puppy) project for license information.
