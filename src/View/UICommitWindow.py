from .BaseWindow import BaseWindow
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget
from PySide6.QtCore import Signal, Qt
from .WindowID import WindowID


class CommitWindow(BaseWindow):
    accept_clicked_signal = Signal(str)
    cancel_clicked_signal = Signal()

    def __init__(self):
        super().__init__("Commit Windows", WindowID.COMMIT, 300, 150)
        """Layouts"""
        self.main_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        """Buttons"""
        self.accept_button = self._create_button("checkmark.png", "Accept")
        self.cancel_button = self._create_button("cross.png", "Cancel")
        "Others"
        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("")
        self.input_label = QLabel("Insert a commit message")
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
        return

    def _on_accept_clicked_signal(self):
        if self.input_message.text() == "":
            self.input_message.setPlaceholderText("Enter a commit message!!!")
        else:
            message: str = self.input_message.text()
            print(message)
            self.accept_clicked_signal[str].emit(message)
        return

    def _on_cancel_clicked_signal(self):
        self.cancel_clicked_signal.emit()
        return


