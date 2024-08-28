from PySide6.QtCore import Qt, QAbstractTableModel, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QTableView,
    QMessageBox,
    QMenu,
    QListWidget,
    QVBoxLayout,
    QMainWindow
)
from Model.UserModel import UserModel
from Model.UserRolesModel import UserRolesModel
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from Utils.Environment import RoleID
from enum import Enum


class INDEX_NAME(Enum):
    USERNAME = 'User'
    EMAIL = 'Email'
    ROLE = 'Role'


class UserTableView(QTableView):
    message_log = Signal(str)
    error_log = Signal(str)
    refresh = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.user_model = UserModel()

    def show_context_menu(self, position):
        indexes = self.selectedIndexes()
        if indexes:
            # Create a QMenu
            menu = QMenu()

            # Add actions to the menu
            edit_action = menu.addAction("Edit")
            delete_action = menu.addAction("Delete")

            # Connect actions to methods
            edit_action.triggered.connect(lambda: self.edit_row(indexes[0].row()))
            delete_action.triggered.connect(lambda: self.delete_row(indexes[0].row()))

            # Show the context menu at the cursor position
            menu.exec_(self.viewport().mapToGlobal(position))

    def edit_row(self, row):
        row_data = self.get_row_data(row)

    def delete_row(self, row):
        row_data = self.get_row_data(row)

        if INDEX_NAME.ROLE.value not in row_data:
            self.error_log.emit(f" Error trying to get row data row:{row} ")

        roles_model = UserRolesModel()

        role = roles_model.get_role_by_name(row_data[INDEX_NAME.ROLE.value])
        if role is None:
            self.message_log(f" Error trying to get row data!!, role: {row_data[INDEX_NAME.value]}")

        role_id = role[0]
        if role_id == RoleID.ADMIN.value:
            self.show_info_message("You can not delete an admin account")
        else:
            reply = QMessageBox.question(
                self,
                "Quit",
                "Are you sure you want to delete user?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.delete_user(row_data)

    def delete_user(self, row_data):
        self.user_model.delete_user(row_data[INDEX_NAME.USERNAME.value])
        self.refresh.emit()

    def get_row_data(self, row):
        model = self.model()
        data = {}
        for column in range(model.columnCount()):
            index = model.index(row, column)
            data[model.headerData(column, Qt.Orientation.Horizontal)] = model.data(index)
        return data

    def show_info_message(self, message: str):
        # Create a QMessageBox instance
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Information")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


class TableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return len(self._data[0]) if len(self._data) > 0 else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return super().headerData(section, orientation, role)

    def clear(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()


class AdminWindow(BaseWindow):
    def __init__(self):
        super().__init__("Admin Window", WindowID.ADMIN, 600, 400)
        self.main_layout = QHBoxLayout(self)
        self.title = QLabel("Users")
        self.table_frame = self.create_default_frame("TableFrame")
        self.users_table = UserTableView()
        self.table_model = None
        self.user_model = UserModel()
        self.build()
        self.apply_styles()
        self.connect_signals()

    def build(self):
        all_users = self.user_model.get_all_users_table()
        headers = ["User", "Email", "Role"]
        self.table_model = TableModel(all_users, headers)
        self.users_table.setModel(self.table_model)

        self.table_frame.setLayout(self.main_layout)
        self.table_frame.layout().addWidget(self.title)
        self.table_frame.layout().addWidget(self.users_table)
        self.table_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.users_table.setColumnWidth(1, 300)
        self.users_table.adjustSize()

        widget = QWidget()
        widget.setLayout(self.table_frame.layout())
        self.setCentralWidget(widget)

    def connect_signals(self):
        self.users_table.refresh.connect(self.refresh)
        return

    def refresh(self):
        if self.table_model:
            self.table_model.clear()

        all_users = self.user_model.get_all_users_table()
        headers = ["User", "Email", "Role"]
        self.table_model = TableModel(all_users, headers)
        self.users_table.setModel(self.table_model)

    def apply_styles(self):
        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.users_table, colour="White", textColour="Black")
