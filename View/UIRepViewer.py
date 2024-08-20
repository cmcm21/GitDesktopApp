from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QFileSystemModel,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QApplication
)
from PySide6.QtCore import QModelIndex, Qt, Signal, QRect
from PySide6 import QtGui
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
import os


class RepositoryViewerWidget(QWidget):

    file_selected = Signal(str)

    def __init__(self, repository_path: str):
        super().__init__()

        # Set up the layout
        self.layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        # Create a file system model
        self.model = QFileSystemModel()
        self.repository_path = os.path.join(repository_path, "../")
        self.model.setRootPath(self.repository_path)
        # Create a tree view and set the model
        self.tree = QTreeView()
        self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.repository_path))
        self.tree.setAutoScroll(True)
        self.tree.setFont(QtGui.QFont("Courier New", 10))
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 150)
        self.tree.setColumnWidth(3, 150)
        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.tree)

        # Connect the tree view's clicked signal to a slot
        self.tree.doubleClicked.connect(self.on_tree_view_clicked)

        # Add the tree view and label to the layout
        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.tree)

        # Set the layout for the main widget
        self.setLayout(self.layout)

    def on_tree_view_clicked(self, index: QModelIndex):
        # Get the file path from the model
        file_path = self.model.filePath(index)
        self.file_selected.emit(file_path)

    def set_root_directory(self):
        self.model.setRootPath(self.repository_path)
        self.tree.setRootIndex(self.model.index(self.repository_path))

    def resizeEvent(self, event):
        self.buttons_layout.setGeometry(QRect(0, 0, self.buttons_layout.sizeHint().width(),
                                               self.buttons_layout.sizeHint().height()))
        super().resizeEvent(event)
