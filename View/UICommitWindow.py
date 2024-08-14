from View.BaseWindow import BaseWindow
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget, QMainWindow
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from View.WindowID import WindowID
from View.CustomStyleSheetApplier import CustomStyleSheetApplier


class CommitWindow(QMainWindow):
    accept_clicked_signal = Signal(str)
    cancel_clicked_signal = Signal()

    def __init__(self, title, label="Insert a commit message", width=400, height=300):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        """Layouts"""
        self.main_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        """Buttons"""
        self.accept_button = BaseWindow.create_button(self, "checkmark.png", "Accept")
        self.cancel_button = BaseWindow.create_button(self, "cross.png", "Cancel")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.cancel_button, "Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.accept_button, "Blue")
        "Others"
        self.input_message = QLineEdit()
        self.input_message.setFont(QFont("Courier New", 10))
        self.input_message.setPlaceholderText("")
        self.input_label = QLabel(label)
        self.input_label.setFont(QFont("Courier New", 10))
        self._build()
        self._connect_buttons()

    def _build(self):
        """Build Buttons Layout"""
        self.buttons_layout.addWidget(self.accept_button, 0, Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout.addWidget(self.cancel_button, 0, Qt.AlignmentFlag.AlignCenter)
        """Build Main Layout"""
        self.main_layout.addWidget(self.input_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.input_message)
        self.main_layout.addLayout(self.buttons_layout)
        """Set Main Layout"""
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def _connect_buttons(self):
        self.accept_button.clicked.connect(self, self._on_accept_clicked_signal)
        self.cancel_button.clicked.connect(self, self._on_cancel_clicked_signal)

    def _on_accept_clicked_signal(self):
        if self.input_message.text() == "":
            self.input_message.setPlaceholderText("Enter a commit message!!!")
        else:
            message: str = self.input_message.text()
            self.accept_clicked_signal.emit(message)

    def _on_cancel_clicked_signal(self):
        self.cancel_clicked_signal.emit()
