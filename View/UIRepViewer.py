from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QFileSystemModel,
    QHBoxLayout,
    QSizePolicy,
    QMenu,
    QMessageBox,
    QAbstractItemView
)
from PySide6.QtCore import QModelIndex, Qt, Signal, QRect, QPoint, QFileSystemWatcher
from PySide6.QtGui import QFont, QAction
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.BaseWindow import BaseWindow
import os


class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)

    def data(self, index: QModelIndex, role: Qt.DisplayRole):
        # Get the default data
        if role == Qt.ItemDataRole.DisplayRole:
            return super().data(index, role)

        # Provide tooltip text for each item
        if role == Qt.ItemDataRole.ToolTipRole:
            file_path = self.filePath(index)
            file_info = self.fileInfo(index)
            tooltip_text = f"Name: {file_info.fileName()}\nSize: {file_info.size()} bytes\nPath: {file_path}"
            return tooltip_text

        return super().data(index, role)

class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set default to single selection mode
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def keyPressEvent(self, event):
        # Enable multi-selection mode when Shift is pressed
        if event.key() == Qt.Key.Key_Shift:
            self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        # Revert to single selection mode when Shift is released
        if event.key() == Qt.Key.Key_Shift:
            self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        super().keyReleaseEvent(event)

class RepositoryViewerWidget(QWidget):

    open_file = Signal(str)
    open_explorer = Signal(str)
    delete_file = Signal(str)
    repo_updated = Signal()

    def __init__(self, repository_path: str):
        super().__init__()

        # Set up the layout
        self.watcher = None
        self.layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        # Create a file system model
        self.model = CustomFileSystemModel()
        self.raw_repository_path = repository_path
        self.repository_path = os.path.join(self.raw_repository_path, "./")
        self.model.setRootPath(self.repository_path)
        # Create a tree view and set the model
        self.tree = CustomTreeView()

        self.setup_tree()
        self.setup_watcher()

        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.tree)
        # Add the tree view and label to the layout
        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.tree)

        # Set the layout for the main widget
        self.setLayout(self.layout)

    def setup_tree(self):
        self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.repository_path))
        self.tree.setAutoScroll(True)

        self.tree.setFont(QFont("Courier New", 10))
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 150)
        self.tree.setColumnWidth(3, 150)

        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)

    def setup_watcher(self):
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.raw_repository_path)

        for root, dirs, files in os.walk(self.raw_repository_path):
            for dir_name in dirs:
                full_dir = os.path.join(root, dir_name)
                self.watcher.addPath(full_dir)

        self.watcher.fileChanged.connect(self.repo_updated, Qt.ConnectionType.QueuedConnection)
        # self.watcher.directoryChanged.connect(self.repo_updated, Qt.ConnectionType.QueuedConnection)

    def on_repo_updated(self):
        self.repo_updated.emit()

    def open_menu(self, position: QPoint):
        index = self.tree.indexAt(position)
        menu = QMenu()

        file_path = self.model.filePath(index)
        file_name = self.model.fileName(index)

        if ".gitignore" in file_name:
            return

        # create a context menu
        type_path = "Directory" if os.path.isdir(file_path) else "File"
        open_file = QAction(f"Open {type_path}", self)
        open_explorer = QAction("Open In Explorer", self)
        delete_file =  QAction(f"Delete {type_path}", self)

        if os.path.isdir(file_path):
            menu.addAction(open_explorer)
        else:
            menu.addAction(open_file)
        menu.addAction(delete_file)

        open_file.triggered.connect(lambda: self.on_open_file(file_path))
        open_explorer.triggered.connect(lambda: self.open_explorer.emit(file_path))
        delete_file.triggered.connect(lambda: self.on_delete_file(file_path))

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def on_open_file(self, file):
        selected_files = self.get_selected_files()
        if len(selected_files) > 0:
            for file in selected_files:
                self.open_file.emit(file)
        else:
            self.open_file.emit(file)

    def on_delete_file(self, file):
        selected_files = self.get_selected_files()
        box_message = \
            f"Are you sure to Delete file(s) : {len(selected_files)}" \
                if len(selected_files) > 0 else f"Are you sure to Delete file: {file}"

        if BaseWindow.throw_message_box(f"Delete file", box_message, self, QMessageBox.Icon.Warning):
            for file in selected_files:
                self.delete_file.emit(file)

            self.on_repo_updated()

    def on_tree_view_clicked(self, index: QModelIndex):
        # Get the file path from the model
        file_path = self.model.filePath(index)
        self.open_file.emit(file_path)

    def get_selected_files(self) -> list:
        files = []
        indexes = self.tree.selectedIndexes()
        for index in indexes:
            file_path = self.model.filePath(index)
            if not file_path in files:
                files.append(file_path)

        self.on_repo_updated()
        return files

    def set_root_directory(self, path: str):
        self.model.setRootPath(path)
        self.tree.setRootIndex(self.model.index(path))

    def resizeEvent(self, event):
        self.buttons_layout.setGeometry(
            QRect(0, 0, self.buttons_layout.sizeHint().width(),self.buttons_layout.sizeHint().height()))
        super().resizeEvent(event)