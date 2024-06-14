from PySide6.QtWidgets import QMainWindow


class BaseWindow(QMainWindow):
    def __init__(self, title: str, width=500,  height=800):
        super().__init__()
        self.width = width
        self.height = height
        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

    def open(self):
        self.show()

    def close(self):
        self.hide()
