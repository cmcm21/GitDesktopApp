from App import Application
from PySide6.QtGui import QIcon
from Utils.FileManager import FileManager
import os

if __name__ == "__main__":
    application = Application()
    application.setWindowIcon(QIcon(FileManager.get_img_path("default_icon.ico")))
    application.run()
