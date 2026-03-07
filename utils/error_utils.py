"""Centralized error handling utilities.

Consolidates error detection, categorization, and parsing logic
that was previously duplicated across app.py, content_renderer.py,
and agent_worker.py.
"""

import re
import threading
from typing import Optional


# Centralized error detection keywords
ERROR_KEYWORDS = [
    'error', 'failed', 'status_code', 'unexpected',
    'bad request', 'unauthorized', 'forbidden',
    'does not appear to support', 'api error',
    'usage limit', 'mcp server error', 'connection',
    'timeout', 'timed out'
]

# HTTP status code mappings
HTTP_ERROR_CATEGORIES = {
    "400": "API Error (400)",
    "401": "Auth Error (401)",
    "403": "Access Denied (403)",
    "404": "Not Found (404)",
    "429": "Rate Limited (429)",
    "500": "Server Error (500)",
    "502": "Server Error (502)",
    "503": "Server Error (503)",
    "504": "Server Error (504)",
}

# Error hints for user-friendly messages
ERROR_HINTS = {
    "does not appear to support": "This model may not support the requested feature (e.g., image inputs). Try a different model.",
    "400": "The request was malformed. Check your input format.",
    "bad request": "The request was malformed. Check your input format.",
    "401": "Authentication failed. Check your API key configuration.",
    "unauthorized": "Authentication failed. Check your API key configuration.",
    "403": "Access denied. You may not have permission for this operation.",
    "forbidden": "Access denied. You may not have permission for this operation.",
    "429": "Rate limit exceeded. Wait a moment and try again.",
    "rate limit": "Rate limit exceeded. Wait a moment and try again.",
    "500": "The server encountered an error. Try again later.",
    "internal server error": "The server encountered an error. Try again later.",
    "502": "Server is temporarily unavailable. Try again in a moment.",
    "bad gateway": "Server is temporarily unavailable. Try again in a moment.",
    "503": "Service is temporarily overloaded. Try again later.",
    "service unavailable": "Service is temporarily overloaded. Try again later.",
    "timeout": "The request timed out. Check your connection and try again.",
    "timed out": "The request timed out. Check your connection and try again.",
    "connection": "Could not connect to the server. Check your internet connection.",
}


def is_error_message(content: str) -> bool:
    """Check if content looks like an error message.

    Args:
        content: Text to check for error indicators

    Returns:
        True if content appears to be an error message
    """
    if not content:
        return False
    content_lower = content.lower()
    return any(kw in content_lower for kw in ERROR_KEYWORDS)


def categorize_error(error: str) -> str:
    """Categorize an error message into a user-friendly type.

    Args:
        error: The error message text

    Returns:
        A categorized error type string (e.g., "API Error (400)")
    """
    error_lower = error.lower()

    # Check HTTP status codes first
    for code, category in HTTP_ERROR_CATEGORIES.items():
        if code in error:
            return category

    # Check keyword-based categories
    if "bad request" in error_lower:
        return "API Error (400)"
    elif "unauthorized" in error_lower:
        return "Auth Error (401)"
    elif "forbidden" in error_lower:
        return "Access Denied (403)"
    elif "rate limit" in error_lower:
        return "Rate Limited (429)"
    elif "timeout" in error_lower or "timed out" in error_lower:
        return "Timeout"
    elif "connection" in error_lower:
        return "Connection Error"

    return "Error"


def get_error_hint(error: str) -> Optional[str]:
    """Get a user-friendly hint for an error message.

    Args:
        error: The error message text

    Returns:
        A helpful hint string, or None if no hint is available
    """
    error_lower = error.lower()

    for pattern, hint in ERROR_HINTS.items():
        if pattern in error_lower:
            return hint

    return None


def parse_error_message(error_message: str) -> dict:
    """Parse an error message to extract structured information.

    Args:
        error_message: Raw error message text

    Returns:
        Dict with keys: status_code, model_name, body, raw_message
    """
    result = {
        "status_code": None,
        "model_name": None,
        "body": None,
        "raw_message": error_message
    }

    if not error_message:
        return result

    # Clean up tuple formatting like ('...',) or ("...",)
    cleaned = error_message.strip()
    if cleaned.startswith("(") and cleaned.endswith(",)"):
        cleaned = cleaned[1:-2].strip()
        if (cleaned.startswith("'") and cleaned.endswith("'")) or \
           (cleaned.startswith('"') and cleaned.endswith('"')):
            cleaned = cleaned[1:-1]

    # Remove "Unexpected error: " prefix
    if cleaned.lower().startswith("unexpected error:"):
        cleaned = cleaned[17:].strip()

    # Parse status_code: NNN pattern
    status_match = re.search(r'status_code:\s*(\d+)', cleaned, re.IGNORECASE)
    if status_match:
        result["status_code"] = status_match.group(1)

    # Parse model_name: ... pattern
    model_match = re.search(r'model_name:\s*([^,]+)', cleaned, re.IGNORECASE)
    if model_match:
        result["model_name"] = model_match.group(1).strip()

    # Parse body: ... pattern (rest of message after body:)
    body_match = re.search(r'body:\s*(.+)$', cleaned, re.IGNORECASE)
    if body_match:
        result["body"] = body_match.group(1).strip()

    # If no structured format found, use cleaned message
    if not any([result["status_code"], result["model_name"], result["body"]]):
        result["body"] = cleaned

    return result


class ErrorCapturer:
    """Captures error messages from MessageQueue for later retrieval.

    Thread-safe error collection that can patch the MessageQueue
    to intercept error messages during agent execution.
    """

    def __init__(self):
        self.captured_errors: list[str] = []
        self._lock = threading.Lock()
        self._original_emit = None
        self._patched = False

    def capture(self, msg: str):
        """Capture an error message if it matches error patterns.

        Args:
            msg: Message to potentially capture
        """
        if msg and is_error_message(msg):
            with self._lock:
                if msg not in self.captured_errors:
                    self.captured_errors.append(msg)

    def patch_message_queue(self):
        """Patch the MessageQueue.emit to capture error messages."""
        if self._patched:
            return

        try:
            from code_puppy.messaging import get_global_queue, MessageType

            queue = get_global_queue()
            self._original_emit = queue.emit

            def patched_emit(message):
                self._original_emit(message)
                if hasattr(message, 'type') and hasattr(message, 'content'):
                    if message.type in (MessageType.ERROR, MessageType.WARNING, MessageType.INFO):
                        content = str(message.content) if message.content else ""
                        self.capture(content)

            queue.emit = patched_emit
            self._patched = True
        except Exception:
            pass

    def unpatch_message_queue(self):
        """Restore original MessageQueue.emit."""
        if not self._patched or self._original_emit is None:
            return

        try:
            from code_puppy.messaging import get_global_queue
            queue = get_global_queue()
            queue.emit = self._original_emit
            self._patched = False
        except Exception:
            pass

    def get_last_error(self) -> Optional[str]:
        """Get the most recently captured error."""
        with self._lock:
            return self.captured_errors[-1] if self.captured_errors else None

    def get_all_errors(self) -> list[str]:
        """Get all captured errors."""
        with self._lock:
            return list(self.captured_errors)

    def clear(self):
        """Clear all captured errors."""
        with self._lock:
            self.captured_errors.clear()


# Global error capturer instance
_error_capturer: Optional[ErrorCapturer] = None


def get_error_capturer() -> ErrorCapturer:
    """Get or create the global error capturer."""
    global _error_capturer
    if _error_capturer is None:
        _error_capturer = ErrorCapturer()
        _error_capturer.patch_message_queue()
    return _error_capturer
