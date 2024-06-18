from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeView, QLabel, QFileSystemModel
from PySide6.QtCore import QModelIndex, Qt
import os


class WorkspaceWidget(QWidget):
    def __init__(self, repository_path: str):
        super().__init__()

        # Set up the layout
        self.layout = QVBoxLayout()

        # Create a label to display selected file path
        self.file_label = QLabel("No file selected")

        # Create a file system model
        self.model = QFileSystemModel()
        self.repository_path = os.path.join(repository_path, "../")
        self.model.setRootPath(self.repository_path)

        # Create a tree view and set the model
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.repository_path))
        self.tree.setColumnWidth(0, 250)

        # Connect the tree view's clicked signal to a slot
        self.tree.clicked.connect(self.on_tree_view_clicked)

        # Add the tree view and label to the layout
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.file_label)

        # Set the layout for the main widget
        self.setLayout(self.layout)

    def on_tree_view_clicked(self, index: QModelIndex):
        # Get the file path from the model
        file_path = self.model.filePath(index)

        # Update the label with the selected file path
        self.file_label.setText(file_path)

    def set_root_directory(self):
        self.model.setRootPath(self.repository_path)
        self.tree.setRootIndex(self.model.index(self.repository_path))

