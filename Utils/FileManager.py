import io
import os
import sys
import fnmatch
from PySide6.QtCore import QObject, Signal, SignalInstance
from pathlib import Path
import shutil
import compileall
import tomli


class FileManager:

    @staticmethod
    def path_exists(path: str) -> bool:
        return os.path.isdir(path)

    @staticmethod
    def get_local_path() -> str:
        this_file_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(this_file_path, "../")

    @staticmethod
    def get_img_path(img_path: str) -> str:
        local_path = FileManager.get_local_path()
        icon_path = os.path.join(local_path, "Resources/Img/", img_path)
        return icon_path

    @staticmethod
    def file_exist(file: str) -> bool:
        local_path = FileManager.get_local_path()
        file_path = os.path.join(local_path, file)
        return Path(file_path).exists()

    @staticmethod
    def in_path(path: str) -> bool:
        return os.curdir == path

    @staticmethod
    def join_with_local_path(path: str) -> str:
        return os.path.join(FileManager.get_local_path(), "Data/")

    @staticmethod
    def create_dir(path:str):
        os.mkdir(path)

    @staticmethod
    def dir_exist(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def move_to(path: str):
        if not FileManager.in_path(path):
            os.chdir(path)

    @staticmethod
    def move_to_local_dir():
        if not FileManager.in_path(FileManager.get_local_path()):
            FileManager.move_to(FileManager.get_local_path())

    @staticmethod
    def move_dir(source_path: str, dist_path: str):
        if not os.path.exists(dist_path):
            os.mkdir(dist_path)
        if os.path.exists(source_path) and os.path.isdir(source_path):
            try:
                shutil.move(source_path, dist_path)
            except Exception as e:
                print(f"Error moving directory from {source_path} to {dist_path}: {e}")

    @staticmethod
    def erase_dir(source_path: str):
        if os.path.exists(source_path) and os.path.isdir(source_path):
            shutil.rmtree(source_path)

    @staticmethod
    def ensure_all_files_extension(directory, extension) -> bool:
        files = os.listdir(directory)
        return all(file.endswith(extension) for file in files)

    @staticmethod
    def dir_empty(path: str):
        return not os.listdir(path)

    @staticmethod
    def get_dir_files_count(path: str):
        return len(os.listdir(path))

    @staticmethod
    def compile_python_files(source_path: str, log_signal: SignalInstance):
        # WARNING: if you don't move to the working path before continue all the project files will be deleted
        FileManager.move_to(source_path)
        files = os.listdir(source_path)
        # Create sys.stdout to the StringIO object
        output = io.StringIO()

        # Redirect sys.stdout to the StringIO object
        old_stdout = sys.stdout
        sys.stdout = output
        try:
            for file in files:
                if os.path.isdir(file):
                    compileall.compile_dir(file, maxlevels=5, force=True)
            compileall.compile_dir(source_path, maxlevels=5)
        finally:
            # Reset sys.stdout to its original state
            sys.stdout = old_stdout

        # Get the output from the StringIO object
        captured_output = output.getvalue()
        log_signal.emit(captured_output)
        output.close()

    @staticmethod
    def find_files(pattern, extension, directory) -> list:
        matches = []
        # Traverse the directory tree
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(f".{extension}") and pattern in file:
                    print(file)
                    full_path = os.path.join(root, fr"{file}")
                    matches.append(full_path)

        return matches

    @staticmethod
    def get_files_extension(extension, directory) -> list:
        matches = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(f".{extension}"):
                    matches.append(file)

        return matches

    @staticmethod
    def find_directories(pattern: str, root_directory: str):
        directories = []

        for root, dirs, files in os.walk(root_directory):
            for dir_name in fnmatch.filter(dirs, pattern):
                directories.append(os.path.join(root, dir_name))

        return directories

    @staticmethod
    def move_all_files_except_extension(src_dir: str, dst_dir: str, extension: str, log_signal: SignalInstance):
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if not file.endswith(extension):
                    # Construct full file path
                    file_path = os.path.join(root, file)

                    # Determine the relative path from the source directory
                    relative_path = os.path.relpath(root, src_dir)

                    # Create the corresponding directory in the destination if it doesn't exist
                    destination_dir = os.path.join(dst_dir, relative_path)
                    os.makedirs(destination_dir, exist_ok=True)

                    # Move the file
                    if file.endswith(".pyc"):
                        shutil.move(file_path, os.path.join(destination_dir, file))
                        log_signal.emit(f"Moved: {file_path} -> {os.path.join(destination_dir, file)}")
                    else:
                        shutil.copy(file_path, os.path.join(destination_dir, file))
                        log_signal.emit(f"Copied: {file_path} -> {os.path.join(destination_dir, file)}")

    @staticmethod
    def get_os_root_dir():
        return os.path.abspath(os.sep)

    @staticmethod
    def join_with_os_root_dir(path: str) -> str:
        return os.path.join(FileManager.get_os_root_dir(), path)

    @staticmethod
    def erase_dir_files(path: str):
        files = os.listdir(path)
        for file in files:
            if os.path.isdir(file):
                FileManager.erase_dir(os.path.join(path, file))
            else:
                os.remove(os.path.join(path, file))
