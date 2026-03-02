"""Entry point for Code Puppy Desktop application."""

import sys
import logging


def setup_logging():
    """Configure logging for desktop application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def launch_desktop():
    """Launch the desktop application.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
    except ImportError:
        print("Error: PySide6 not installed.")
        print("Install with: pip install PySide6 PySide6-Essentials Pygments markdown")
        return 1

    setup_logging()

    from desktop.app import CodePuppyApp

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Code Puppy")
    app.setOrganizationName("Code Puppy")

    # Create and show main window
    window = CodePuppyApp()
    window.show()

    return app.exec()


def main():
    """Main entry point."""
    sys.exit(launch_desktop())


if __name__ == "__main__":
    main()
