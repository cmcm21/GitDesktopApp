from View.BaseWindow import BaseWindow
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget, QMainWindow
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.WindowID import WindowID


class PublishWindow(QMainWindow):
    compile_all_signal = Signal(str)
    compile_just_change_list_signal = Signal(str)
    cancel_signal = Signal()

    def __init__(self, title, label="Insert a commit message", width=300, height=150):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        """Layouts"""
        self.main_layout = QVBoxLayout(self)
        self.publish_buttons_layout = QHBoxLayout(self)
        self.buttons_layout = QVBoxLayout(self)
        """Buttons"""
        self.compile_all_button = BaseWindow.create_button(self, button_text="Compile and publish all")
        self.cancel_button = BaseWindow.create_button(self, button_text="Cancel")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.compile_all_button, "Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.cancel_button, "Brown")
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
        self.publish_buttons_layout.addWidget(self.compile_all_button, 0, Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout.addLayout(self.publish_buttons_layout)
        self.buttons_layout.addWidget(self.cancel_button)
        """Build Main Layout"""
        self.main_layout.addWidget(self.input_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.input_message)
        self.main_layout.addLayout(self.buttons_layout)
        """Set Main Layout"""
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def _connect_buttons(self):
        self.compile_all_button.clicked.connect(self._on_compile_all_button_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_button)

    def _on_compile_all_button_clicked(self):
        if self.input_message.text() == "":
            self.input_message.setPlaceholderText("Enter a publish message!!!")
        else:
            message: str = self.input_message.text()
            self.compile_all_signal.emit(message)

    def _on_compile_just_change_list(self):
        if self.input_message.text() == "":
            self.input_message.setPlaceholderText("Enter a publish message!!!")
        else:
            message: str = self.input_message.text()
            self.compile_just_change_list_signal.emit(message)

    def _on_cancel_button(self):
        self.cancel_signal.emit()

