from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel
from View.CustomStyleSheetApplier import CustomStyleSheetApplier


class DiffsWidget(QWidget):

    def __init__(self, diffs: str, file_name: str):
        super().__init__()
        self.setWindowTitle(file_name)
        self.text = QTextEdit()
        layout = QVBoxLayout(self)

        self.text.setReadOnly(True)
        self.text.setText(diffs)
        layout.addWidget(self.text)

        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.text, colour="White", textColour="Black")
