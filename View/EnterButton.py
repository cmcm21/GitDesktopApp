from PySide6.QtWidgets import  QPushButton
from PySide6.QtCore import Qt

class EnterButton(QPushButton):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            print("Enter key pressed on the button!")
            self.click()  # Simulate button click if Enter is pressed
        else:
            super().keyPressEvent(event)  # Call the base class method for other keys
