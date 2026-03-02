"""File tree sidebar widget for browsing project files."""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
    QFileSystemModel, QPushButton, QLabel, QLineEdit,
    QMenu, QFileDialog,
)
from PySide6.QtCore import Qt, Signal, QDir, QModelIndex
from PySide6.QtGui import QAction


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

        # Header
        header = QHBoxLayout()
        header.setSpacing(4)

        self._title = QLabel("Files")
        self._title.setStyleSheet("font-weight: bold; color: #e0e0e0; padding: 4px;")
        header.addWidget(self._title)

        header.addStretch()

        # Folder button
        self._folder_btn = QPushButton("\U0001f4c1")  # Folder icon
        self._folder_btn.setFixedSize(28, 28)
        self._folder_btn.setToolTip("Open folder")
        self._folder_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-radius: 4px;
            }
        """)
        self._folder_btn.clicked.connect(self._on_open_folder)
        header.addWidget(self._folder_btn)

        # Refresh button
        self._refresh_btn = QPushButton("\u21bb")  # Refresh icon
        self._refresh_btn.setFixedSize(28, 28)
        self._refresh_btn.setToolTip("Refresh")
        self._refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-radius: 4px;
            }
        """)
        self._refresh_btn.clicked.connect(self._on_refresh)
        header.addWidget(self._refresh_btn)

        layout.addLayout(header)

        # Filter input
        self._filter_input = QLineEdit()
        self._filter_input.setPlaceholderText("Filter files...")
        self._filter_input.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 4px 8px;
                margin: 0 4px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """)
        self._filter_input.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self._filter_input)

        # Tree view
        self._tree = QTreeView()
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)
        self._tree.setStyleSheet("""
            QTreeView {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: none;
            }
            QTreeView::item {
                padding: 4px;
            }
            QTreeView::item:hover {
                background-color: #2d2d2d;
            }
            QTreeView::item:selected {
                background-color: #1a73e8;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(none);
            }
        """)
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
        self._menu_style = """
            QMenu {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """

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

    def _on_open_folder(self):
        """Handle open folder button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self._root_path,
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.set_root_path(folder)

    def _on_refresh(self):
        """Handle refresh button click."""
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
