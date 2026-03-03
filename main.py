"""Entry point for Code Puppy Desktop application."""

import sys
import logging
import subprocess
from pathlib import Path


def setup_logging():
    """Configure logging for desktop application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def _install_dependencies():
    """Install missing dependencies from requirements.txt."""
    import shutil

    requirements_path = Path(__file__).parent / "requirements.txt"
    if not requirements_path.exists():
        print("Error: requirements.txt not found")
        return False

    print("Installing desktop GUI dependencies...")

    # Try uv first (faster and may be the active package manager)
    if shutil.which("uv"):
        try:
            subprocess.check_call([
                "uv", "pip", "install", "-r", str(requirements_path)
            ])
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            pass  # Fall through to pip

    # Fall back to pip
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
        ])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def launch_desktop():
    """Launch the desktop application.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
    except ImportError:
        print("PySide6 not found. Installing dependencies...")
        if not _install_dependencies():
            return 1
        # Retry import after installation
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
        except ImportError:
            print("Error: Failed to import PySide6 after installation.")
            print("Please restart the application and try again.")
            return 1

    setup_logging()

    from .app import CodePuppyApp

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
