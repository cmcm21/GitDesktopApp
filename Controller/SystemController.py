from PySide6.QtCore import QObject, Signal, Slot
from Utils.ConfigFileManager import ConfigFileManager
from pathlib import Path
import shutil
import winreg
import os
import subprocess
import platform
import urllib.request
import sys

from Utils.FileManager import FileManager


class SystemController(QObject):
    """Signals"""
    setup_started = Signal()
    maya_checked = Signal(bool)
    git_checked = Signal(bool)
    git_installed = Signal(bool)
    log_message = Signal(str)
    error_message = Signal(str)
    setup_finished = Signal()

    maya_paths = [
        "C://Program Files/Autodesk/Maya2022/bin/maya.exe",
        "C://Program Files/Autodesk/Maya2024/bin/maya.exe",
        "C://Program Files/Autodesk/Maya2025/bin/maya.exe"
    ]
    maya_bin = ""

    def __init__(self):
        super(SystemController, self).__init__()
        self.bat_bin = None
        self.config_manager = ConfigFileManager()
        config = self.config_manager.get_config()

        self.git_path = config["general"]["git_path"]
        self.git_installer_url = config["general"]["git_installer_url"]
        self.git_token = config["git"]["personal_access_token"]
        self.git_api_url = config["git"]["gitlab_api_url"]
        self.git_user = config["git"]["username"]
        self.working_path = config["general"]["working_path"]
        self.maya_installed = False

    def _check_for_maya(self):
        for path in self.maya_paths:
            if Path(path).exists():
                self.maya_bin = path
                self.maya_installed = True
                self.maya_checked.emit(True)

        self.maya_checked.emit(False)

    def check_registry_key(self, hkey, path):
        try:
            reg_key = winreg.OpenKey(hkey, path)
            winreg.CloseKey(reg_key)
            self.git_checked.emit(True)
            return True
        except FileNotFoundError:
            pass

        self.git_checked.emit(True)
        return False

    def _check_for_git(self) -> bool:
        # Check if 'git' is in the system PATH
        if shutil.which("git"):
            self.git_checked.emit(True)
            return True

        # Check the registry
        registry_paths = [
            r"SOFTWARE\GitForWindows",
            r"SOFTWARE\WOW6432Node\GitForWindows"
        ]

        for path in registry_paths:
            if self.check_registry_key(winreg.HKEY_LOCAL_MACHINE, path):
                self.git_checked.emit(True)
                return True

        self.git_checked.emit(False)
        return False

    def download_git_installer(self, url, save_path):
        try:
            self.log_message.emit(f"Downloading Git installer from {url}...")
            urllib.request.urlretrieve(url, save_path)
            self.log_message.emit("Download completed.")
        except Exception as e:
            self.error_message.emit(f"Error downloading Git installer: {e}")
            return False
        return True

    def run_git_installer(self, installer_path):
        try:
            self.log_message.emit(f"Running Git installer: {installer_path}")
            # Run the installer silently with default options
            subprocess.run([installer_path, '/SILENT'], check=True)
            self.log_message.emit("Git installation completed.")
        except subprocess.CalledProcessError as e:
            self.log_message.emit(f"Error during Git installation: {e}")
            return False
        return True

    def install_git(self):
        self.log_message.emit("Git wasn't found in the system, Start Installing git")
        installer_path = os.path.join(os.getcwd(), "git_installer.exe")

        # Download the Git installer
        if not self.download_git_installer(self.git_installer_url, installer_path):
            self.git_installed.emit(False)
            return False

        # Run the Git installer
        if self.run_git_installer(installer_path):
            self.log_message.emit("Git successfully installed.")
            self.git_installed.emit(True)
        else:
            self.git_installed.emit(False)
            self.log_message.emit("Git installation failed.")

        # Clean up by removing the installer
        try:
            os.remove(installer_path)
            self.log_message.emit("Installer removed.")
        except OSError as e:
            self.error_message.emit(f"Error removing installer: {e}")

    def delete_py_files(self):
        for root, dirs, files in os.walk(self.working_path):
            for file in files:
                if file.endswith('.py'):
                    os.remove(os.path.join(root, file))

    def run_command(self, command: str):
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True,
            )
            stdout, stderr = process.communicate()
            if stdout or "push" in command or "pull" in command:
                self.log_message.emit(stdout)
                return True
            elif stderr:
                if "fatal" in stderr:
                    self.error_message.emit(f"An error occurred executing command: {command}, {stderr}")
                    return False
                else:
                    self.log_message.emit(f"{stderr}")
                    return True

        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred executing command: {command}, error: {e.stderr}")
            raise subprocess.CalledProcessError(e.returncode, e.stderr)

    @Slot()
    def setup(self):
        self.setup_started.emit()
        self._check_for_maya()
        if not self._check_for_git():
            self.install_git()
        self.setup_finished.emit()

    @Slot()
    def open_maya(self):
        if not self.maya_installed:
            return
        self.bat_bin = self.config_manager.get_config()['general']['selected_maya_bat']

        self.log_message.emit("Opening Maya...")
        if self.bat_bin != "":
            self.run_command(self.bat_bin)
        else:
            self.run_command(self.maya_bin)

    @Slot(str)
    def open_file(self, file_path: str):
        if not os.path.isfile(file_path):
            self.error_message.emit(f"File not found: {file_path}")
            return

        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
        except Exception as e:
            self.error_message.emit(f"Failed to open file: {e}")

    @Slot(str)
    def delete_file(self, path: str):
        if not os.path.exists(path):
            return
        if not os.path.isdir(path):
            os.remove(path)
        else:
            FileManager.erase_dir_files(path)
            FileManager.erase_dir(path)

    @Slot(str)
    def open_in_explorer(self, path: str):
        if os.path.isdir(path):
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])

    @Slot(str)
    def select_maya_version(self, maya_bin: str, bat_bin = ""):
        self.maya_bin = maya_bin
        self.bat_bin = bat_bin

