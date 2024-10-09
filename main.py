from App import Application
from PySide6.QtGui import QIcon
from Utils import FileManager
import sys
import win32event
import win32api
import win32con
import win32gui
import winerror

# Function to bring the window to the foreground
def bring_window_to_front(window_title):
    def enum_window_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == window_title:
                # Bring window to front
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)

    win32gui.EnumWindows(enum_window_callback, None)

if __name__ == "__main__":
    # Create a mutex
    mutex = win32event.CreateMutex(None, False, "SingleInstanceMutex")

    # Check if the mutex already exists
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        print("An instance is already running.")
        # If another instance is detected, bring the window to the front
        bring_window_to_front("Single Instance App")
        sys.exit(0)
    else:
        application = Application()
        application.setWindowIcon(QIcon(FileManager.get_img_path("default_icon.ico")))
        application.run()
