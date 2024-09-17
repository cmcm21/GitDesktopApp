from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from dateutil import parser


class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Description", "Date"])
        self.table.setVerticalHeaderLabels([])
        CustomStyleSheetApplier.set_qtableview_style_and_colour(self.table)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def add_commit(self, commit: str):
        commit_split = commit.split(" ")

        commit_id = commit_split[0]
        commit_description = " "
        commit_date = ""
        for word in commit_split[2:]:
            if "(20" not in word:
                commit_description += word + " "
            else:
                commit_date += word
                break

        commit_date += " " + commit_split[-1]
        row_position = self.table.rowCount()

        self.table.insertRow(row_position)

        self.table.setItem(row_position, 0, QTableWidgetItem(commit_id))
        self.table.setItem(row_position, 1, QTableWidgetItem(commit_description))
        self.table.setItem(row_position, 2, QTableWidgetItem(commit_date))

        self.table.resizeColumnsToContents()

    def clear(self):
        self.table.clear()

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Description", "Date"])


