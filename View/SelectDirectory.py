from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QSizePolicy
)
from PySide6.QtCore import Signal
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from PySide6.QtCore import Qt
from View.CustomStyleSheetApplier import CustomStyleSheetApplier


class SelectDirectoryWindow(BaseWindow):
    directory_selected = Signal(str)

    def __init__(self):
        super().__init__("Select Rep Directory", WindowID.SELECT_DIRECTORY,350, 150)
        self.select_directory = None
        self.directory = None

        # Remove close, minimize, maximize buttons, and the title bar
        self.setWindowFlags( Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTitleHint )

        # Ensure the window is focusable and accepts input events
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Button to open the file dialog
        self.chose_dir_button = QPushButton("Choose Directory", self)
        self.chose_dir_button.clicked.connect(self.on_select_directory)

        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.clicked.connect(self.confirm)

        # Layout setup
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chose_dir_button)
        main_layout.addWidget(self.confirm_button)

        # Label to display the selected path
        self.directory_label = QLabel("Directory: ")
        self.directory_input = QLineEdit(self)
        self.directory_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.directory_input.setReadOnly(True)
        directory_layout = QHBoxLayout(self)

        directory_layout.addWidget(self.directory_label, alignment=Qt.AlignmentFlag.AlignLeft)
        directory_layout.addWidget(self.directory_input)

        main_layout.addLayout(directory_layout)
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.apply_styles()

    def on_select_directory(self):
        # Open a directory selection dialog
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.directory:
            # If the user selected a directory, display it in the label
            self.directory_input.setText(self.directory)

    def confirm(self):
        if self.directory:
            self.directory_selected.emit(self.directory)
            self.automatic_close = True
            self.close()
        else:
            self.directory_input.setText("Select a directory to continue with the setup...")

    def apply_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.directory_input)
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.chose_dir_button)
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.confirm_button)

    def show(self):
        self.directory_input.setText("")
        super().show()
