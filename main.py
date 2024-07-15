from App import Application
from PySide6.QtGui import QIcon
from Utils.FileManager import FileManager
import os

if __name__ == "__main__":
    application = Application()
    icon_path = os.path.join(FileManager.get_img_path(), "default_icon.ico")
    application.setWindowIcon(QIcon(icon_path))
    application.run()
