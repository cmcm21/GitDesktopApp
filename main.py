from App import Application
from PySide6.QtGui import QIcon
import os

if __name__ == "__main__":
    application = Application()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "/Resources/Img/", "default_icon.ico")
    application.setWindowIcon(QIcon(icon_path))
    application.run()
