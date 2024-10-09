from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QSizePolicy,
    QHeaderView
)
from View import CustomStyleSheetApplier


class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Description", "Date"])
        self.table.setVerticalHeaderLabels([])
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        CustomStyleSheetApplier.set_qtableview_style_and_colour(self.table)

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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

    def clear(self):
        self.table.clearContents()
        self.table.setRowCount(0)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Description", "Date"])

    def invert_row_labels(self):
        row_count = self.table.rowCount()

        # Set the vertical header labels from greatest to lowest
        for row in range(row_count):
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(row_count - row)))



