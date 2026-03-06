"""OS integration helpers.

Keep platform-specific nonsense out of widgets.

Primary API:
- open_with_default_app(path): open file/folder using the OS default handler.

Uses Qt's QDesktopServices which is cross-platform and delegates to the OS.
"""

from __future__ import annotations

import os
from pathlib import Path


def open_with_default_app(path: str) -> bool:
    """Open the given file/folder using the system default application.

    Returns:
        True if the open request was accepted by Qt/OS, otherwise False.

    Notes:
        We intentionally do not raise on failure because this is a UI action.
        Callers can show a toast/status message if False.
    """

    if not path:
        return False

    normalized = str(Path(path).expanduser())
    if not os.path.exists(normalized):
        return False

    # Import lazily so unit tests can mock PySide6 without needing a Qt runtime.
    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        return bool(QDesktopServices.openUrl(QUrl.fromLocalFile(normalized)))
    except Exception:
        # Fallback: try Python stdlib for Windows, otherwise punt.
        try:
            if os.name == "nt":
                os.startfile(normalized)  # type: ignore[attr-defined]
                return True
        except Exception:
            return False

    return False
