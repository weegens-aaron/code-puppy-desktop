"""File tree sidebar widget for browsing project files."""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView,
    QFileSystemModel, QLineEdit, QMenu,
)
from PySide6.QtCore import Qt, Signal, QDir, QModelIndex
from PySide6.QtGui import QAction

from styles import (
    get_file_tree_filter_style,
    get_file_tree_view_style,
    get_context_menu_style,
)


class FileTree(QWidget):
    """File tree widget for browsing and selecting files.

    Provides a tree view of the file system with filtering,
    context menu for common actions, and signals for file selection.
    """

    file_selected = Signal(str)  # Emits file path when a file is selected
    file_attached = Signal(str)  # Emits image path when attached via context menu
    path_referenced = Signal(str)  # Emits path when added as reference (file or folder)
    directory_changed = Signal(str)  # Emits when root directory changes

    # Image extensions that can be attached
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.ico'}

    def __init__(self, root_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._root_path = root_path or os.getcwd()

        self._setup_ui()
        self._setup_model()
        self._setup_context_menu()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Filter input
        self._filter_input = QLineEdit()
        self._filter_input.setPlaceholderText("Filter files...")
        self._filter_input.setStyleSheet(get_file_tree_filter_style())
        self._filter_input.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self._filter_input)

        # Tree view
        self._tree = QTreeView()
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.setStyleSheet(get_file_tree_view_style())
        self._tree.doubleClicked.connect(self._on_item_double_clicked)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._tree)

    def _setup_model(self):
        """Set up the file system model."""
        self._model = QFileSystemModel()
        self._model.setRootPath(self._root_path)

        # Filter to show common code files and images
        self._model.setNameFilters([
            "*.py", "*.js", "*.ts", "*.jsx", "*.tsx",
            "*.html", "*.css", "*.scss", "*.json", "*.yaml", "*.yml",
            "*.md", "*.txt", "*.rst", "*.toml", "*.ini", "*.cfg",
            "*.sh", "*.bash", "*.zsh", "*.ps1",
            "*.c", "*.cpp", "*.h", "*.hpp", "*.rs", "*.go",
            "*.java", "*.kt", "*.swift", "*.rb", "*.php",
            "Makefile", "Dockerfile", "*.dockerfile",
            ".gitignore", ".env", ".env.example",
            # Images
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp", "*.svg", "*.ico",
        ])
        self._model.setNameFilterDisables(False)

        self._tree.setModel(self._model)
        self._tree.setRootIndex(self._model.index(self._root_path))

        # Hide size, type, date columns
        self._tree.hideColumn(1)
        self._tree.hideColumn(2)
        self._tree.hideColumn(3)

    def _setup_context_menu(self):
        """Set up the context menu styling."""
        self._menu_style = get_context_menu_style()

    def _is_image_file(self, path: str) -> bool:
        """Check if the path is an image file."""
        return Path(path).suffix.lower() in self.IMAGE_EXTENSIONS

    def _show_context_menu(self, position):
        """Show context menu at position with appropriate options."""
        index = self._tree.indexAt(position)
        if not index.isValid():
            return

        self._selected_path = self._model.filePath(index)
        is_dir = os.path.isdir(self._selected_path)
        is_image = not is_dir and self._is_image_file(self._selected_path)

        # Create context menu dynamically
        context_menu = QMenu(self)
        context_menu.setStyleSheet(self._menu_style)

        # Images get attach option
        if is_image:
            attach_action = QAction("Attach image", self)
            attach_action.triggered.connect(self._on_attach)
            context_menu.addAction(attach_action)

        # All items (files and folders) get "Add as reference"
        reference_action = QAction("Add as reference", self)
        reference_action.triggered.connect(self._on_add_reference)
        context_menu.addAction(reference_action)

        context_menu.exec(self._tree.mapToGlobal(position))

    def _on_attach(self):
        """Handle attach image action."""
        if hasattr(self, '_selected_path') and self._selected_path:
            if os.path.isfile(self._selected_path) and self._is_image_file(self._selected_path):
                self.file_attached.emit(self._selected_path)

    def _on_add_reference(self):
        """Handle add as reference action - inserts path into chat input."""
        if hasattr(self, '_selected_path') and self._selected_path:
            self.path_referenced.emit(self._selected_path)

    def _on_item_double_clicked(self, index: QModelIndex):
        """Handle item double-click."""
        path = self._model.filePath(index)
        if os.path.isfile(path):
            self.file_selected.emit(path)

    def refresh(self):
        """Refresh the file tree."""
        self._model.setRootPath("")
        self._model.setRootPath(self._root_path)
        self._tree.setRootIndex(self._model.index(self._root_path))

    def _on_filter_changed(self, text: str):
        """Handle filter text change."""
        if text:
            # Add filter pattern
            patterns = [f"*{text}*"]
            self._model.setNameFilters(patterns)
        else:
            # Reset to default filters
            self._setup_model()

    def set_root_path(self, path: str):
        """Set the root directory path."""
        if os.path.isdir(path):
            self._root_path = path
            self._model.setRootPath(path)
            self._tree.setRootIndex(self._model.index(path))
            self.directory_changed.emit(path)

    def get_root_path(self) -> str:
        """Get the current root path."""
        return self._root_path
