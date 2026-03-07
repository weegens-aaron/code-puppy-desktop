"""Session management for conversation history.

Separates session/history concerns from the main application (SRP/SoC).
"""

from typing import Optional, Callable

from PySide6.QtCore import QTimer, QObject

from models.data_types import Message, MessageRole
from models.message_model import MessageModel
from code_puppy.agents import get_current_agent
from code_puppy.config import get_owner_name, get_puppy_name


class SessionManager(QObject):
    """Manages conversation sessions and history.

    Responsibilities:
    - Starting new sessions
    - Loading/displaying session history
    - Converting agent history to UI messages
    """

    def __init__(
        self,
        message_model: MessageModel,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._model = message_model

    def set_message_model(self, model: MessageModel):
        """Switch to a different message model (for tab switching).

        Args:
            model: The new message model to use
        """
        self._model = model

    # -------------------------------------------------------------------------
    # Session Management
    # -------------------------------------------------------------------------

    def start_new_session(self, clear_agent_history_callback: Callable[[], None]):
        """Start a new session.

        Args:
            clear_agent_history_callback: Function to clear agent's conversation history
        """
        # Clear agent conversation history
        clear_agent_history_callback()

        # Clear UI message list
        self._model.clear()

        # Show welcome message
        self.add_welcome_message()

    def add_welcome_message(self):
        """Add a welcome message for the current agent."""
        owner_name = get_owner_name()
        agent = get_current_agent()
        agent_name = agent.display_name if agent else get_puppy_name()
        description = agent.description if agent else "your AI coding assistant"

        self._model.add_message(
            Message(
                role=MessageRole.ASSISTANT,
                content=f"Hello {owner_name}! I'm {agent_name}. {description}. How can I help you today?"
            )
        )

    # -------------------------------------------------------------------------
    # History Display
    # -------------------------------------------------------------------------

    def display_history(self, history: list, max_messages: int = 20):
        """Display recent messages from loaded history in the UI.

        Args:
            history: The full message history from agent
            max_messages: Maximum number of recent messages to display
        """
        if not history:
            return

        # Skip system message (first message) and get recent messages
        displayable = history[1:] if len(history) > 1 else []
        if not displayable:
            return

        # Take last N messages
        messages_to_show = displayable[-max_messages:] if len(displayable) > max_messages else displayable

        for msg in messages_to_show:
            try:
                self._add_history_message(msg)
            except Exception:
                continue  # Skip messages that fail to render

    def _add_history_message(self, msg):
        """Add a single history message to the UI.

        Args:
            msg: A pydantic-ai message object from history
        """
        # Determine role and content from message parts
        part_kinds = [getattr(p, "part_kind", "unknown") for p in msg.parts]

        if msg.kind == "request":
            if all(pk == "tool-return" for pk in part_kinds):
                role = MessageRole.TOOL_OUTPUT
            else:
                role = MessageRole.USER
        else:
            if all(pk == "tool-call" for pk in part_kinds):
                role = MessageRole.TOOL_CALL
            elif any(pk == "thinking" for pk in part_kinds):
                role = MessageRole.THINKING
            else:
                role = MessageRole.ASSISTANT

        # Extract content
        content_parts = []
        metadata = {}

        for part in msg.parts:
            part_kind = getattr(part, "part_kind", "unknown")

            if part_kind == "tool-call":
                tool_name = getattr(part, "tool_name", "tool")
                args = getattr(part, "args", {})
                metadata["tool_name"] = tool_name
                content_parts.append(f"{tool_name}: {str(args)[:200]}")

            elif part_kind == "tool-return":
                tool_name = getattr(part, "tool_name", "tool")
                result = getattr(part, "content", "")
                metadata["tool_name"] = tool_name
                if isinstance(result, str):
                    content_parts.append(result[:500])

            elif part_kind == "thinking":
                content = getattr(part, "content", "")
                if isinstance(content, str):
                    content_parts.append(content)

            elif hasattr(part, "content"):
                content = part.content
                if isinstance(content, str) and content.strip():
                    content_parts.append(content)

        content = "\n".join(content_parts) if content_parts else "..."

        # Create and add message
        message = Message(role=role, content=content, metadata=metadata)
        self._model.add_message(message)

    def load_session(
        self,
        session_name: str,
        history: list,
        scroll_to_bottom_callback: Callable[[], None]
    ) -> bool:
        """Load a session from history.

        Args:
            session_name: Name of the session being loaded
            history: The message history to load
            scroll_to_bottom_callback: Function to scroll UI to bottom

        Returns:
            True if session was loaded successfully
        """
        if not history:
            return False

        # Clear current UI
        self._model.clear()

        # Load history into agent
        agent = get_current_agent()
        if agent:
            agent.set_message_history(history)

            # Set the autosave session ID to continue this session
            try:
                from code_puppy.config import set_current_autosave_from_session_name
                set_current_autosave_from_session_name(session_name)
            except Exception:
                pass

        # Display recent messages in UI
        self.display_history(history)

        # Scroll to bottom after a short delay
        QTimer.singleShot(50, scroll_to_bottom_callback)

        return True

    # -------------------------------------------------------------------------
    # User Messages
    # -------------------------------------------------------------------------

    def add_user_message(self, content: str, attachments: list[str] | None = None) -> int:
        """Add a user message.

        Args:
            content: The message content
            attachments: Optional list of attachment file paths

        Returns:
            The message index
        """
        return self._model.add_message(
            Message(
                role=MessageRole.USER,
                content=content,
                attachments=attachments or []
            )
        )
