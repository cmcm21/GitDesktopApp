from PySide6.QtWidgets import (
    QListWidget,
    QMenu,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QListWidgetItem,
    QWidget,
    QPushButton,
    QTextEdit
)
from PySide6.QtGui import QAction, QFont, QColor
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt, QSize
from View import CustomStyleSheetApplier
from View.BaseWindow import BaseWindow


class ChangesWidget(QWidget):
    restore_file_clicked = Signal(str)
    item_double_clicked = Signal(QListWidgetItem)
    push_and_commit_clicked = Signal(str, list)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.build_list_widget()
        self.build_text_edit()
        self.build_upload_button()

        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.commit_txt_edit)
        self.layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item is None:
            return

        context_menu = QMenu(self)
        checkbox: QCheckBox = QCheckBox(self.list_widget.itemWidget(item).layout().itemAt(0).widget())

        if checkbox is None:
            print("Error trying to get checkbox from list widget")
        else:
            restore_file_action = QAction("Restore file", self)
            restore_file_action.triggered.connect(lambda: self.restore_file_clicked.emit(checkbox.text()))
            context_menu.addAction(restore_file_action)

            context_menu.exec_(self.mapToGlobal(pos))

    def build_list_widget(self):
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Courier New", 10))
        self.list_widget.setSpacing(2)
        self.list_widget.doubleClicked.connect(lambda item: self.item_double_clicked.emit(item))

    def build_text_edit(self):
        self.commit_txt_edit = QTextEdit()
        self.commit_txt_edit.setPlaceholderText("Add a commit message")
        self.commit_txt_edit.setFixedHeight(80)
        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.commit_txt_edit, "White")
        self.commit_txt_edit.setTextColor(QColor("Black"))

    def build_upload_button(self):
        self.upload_btn: QPushButton = BaseWindow.create_button(
            self, "arrowUp.png", "Commit and Push")

        self.upload_btn.clicked.connect(self.on_push_and_commit_clicked)
        self.upload_btn.setFixedSize(QSize(200, 35))
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.upload_btn, "Blue")

    def on_push_and_commit_clicked(self):
        commit_message = self.commit_txt_edit.toPlainText()
        selected_files = self.get_selected_items()

        if commit_message == "":
            self.commit_txt_edit.setPlaceholderText("Add a commit message to commit and push!!!")
        else:
            self.push_and_commit_clicked.emit(commit_message, selected_files)

    def add_item(self, item:QListWidgetItem):
        self.list_widget.addItem(item)
        widget = QWidget()

        checkbox = QCheckBox(item.text())
        CustomStyleSheetApplier.set_combo_box_style_and_colour(checkbox)

        widget_layout = QHBoxLayout()
        widget_layout.addWidget(checkbox)
        widget_layout.setContentsMargins(25, 0, 0, 0)
        widget.setLayout(widget_layout)

        item.setSizeHint(widget.sizeHint())
        self.list_widget.setItemWidget(item, widget)

    def add_check_all(self):
        text = "Check all"
        item = QListWidgetItem(self.list_widget)
        widget = QWidget()

        checkbox: QCheckBox = QCheckBox(text)
        CustomStyleSheetApplier.set_combo_box_style_and_colour(checkbox)
        checkbox.checkStateChanged.connect(self._on_check_all_state_change)

        widget_layout = QHBoxLayout()
        widget_layout.addWidget(checkbox)
        widget_layout.setContentsMargins(0, 0, 0, 0)

        widget.setLayout(widget_layout)

        item.setSizeHint(widget.sizeHint())
        self.list_widget.setItemWidget(item, widget)

    def _on_check_all_state_change(self, state):
        for i in range(self.list_widget.count()):
            # Get the widget at each QListWidgetItem
            item = self.list_widget.item(i)
            if item is None:
                continue

            checkbox: QCheckBox = self.list_widget.itemWidget(item).layout().itemAt(0).widget()
            if checkbox is not None:
                checkbox.setCheckState(state)

    def get_selected_items(self) -> list[tuple[str,str]]:
        files = []

        for i in range(self.list_widget.count()):
            # Get the widget at each QListWidgetItem
            item = self.list_widget.item(i)
            item_data: tuple[str,str] = self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            if item is None:
                continue

            checkbox: QCheckBox = self.list_widget.itemWidget(item).layout().itemAt(0).widget()
            if checkbox is None:
                print("Error trying to get checkbox from list widget")
            elif checkbox.isChecked() and checkbox.text() != "Check all":
                files.append(item_data)

        return files

    def clear(self):
        self.list_widget.clear()

    def count(self) -> int:
        return self.list_widget.count()

    def check_if_emtpy(self):
        if self.list_widget.count() == 0:
            self.list_widget.addItem("No Changes yet")
            self.upload_btn.setText("Push local commits")
        else:
            self.upload_btn.setText("Commit and Push")
