import io
import os
import sys
import stat
import fnmatch
from PySide6.QtCore import SignalInstance, QObject, Signal
from pathlib import Path
import shutil
import compileall
import ast
import subprocess
from Utils.Environment import FILE_CHANGE_DIC


class FileManager:

    @staticmethod
    def get_working_path(default_path: str, user: str) -> str:
        current_script = Path(__file__).resolve()
        project_path = current_script.parents[2]
        work_path = os.path.join(project_path, default_path, user)
        return work_path

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
    def compile_python_files_from_source(source_path: str, log_signal: SignalInstance):
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
    def compile_python_files(source_path: str, files: list, log_signal: SignalInstance):
        FileManager.move_to(source_path)
        print(f"files to compile: {files}")
        output = io.StringIO()
        # Redirect sys.stdout to the StringIO object
        old_stdout = sys.stdout
        sys.stdout = output
        try:
            for file in files:
                file_path = os.path.join(source_path, file)
                if os.path.isdir(file):
                    compileall.compile_dir(file, maxlevels=5, force=True)
                    print(f"Compiling dir {file}...")
                else:
                    compileall.compile_file(file_path, force=True)
                    print(f"Compiling file {file}...")
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
                    full_path = os.path.join(root, fr"{file}")
                    matches.append(full_path)

        return matches

    @staticmethod
    def get_files_extension(extension, directory) -> list:
        # Ensure the extension starts with a dot
        if not extension.startswith('.'):
            extension = '.' + extension

        matches = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    full_path = os.path.join(root, fr"{file}")
                    matches.append(full_path)

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

                    #ignore all git related files
                    if ".git" in file_path:
                        continue

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
    def move_files(files: list, src_dir: str, extension: str, dst_dir:str, log_signal: SignalInstance):
        # Ensure the extension starts with a dot
        if not extension.startswith('.'):
            extension = '.' + extension

        os.makedirs(dst_dir, exist_ok=True, mode=0o777)

        for file in files:
            file = file.strip('""')
            if not file.endswith(extension):

                source_path = os.path.join(src_dir, file)
                destination_dir = os.path.join(dst_dir, file)

                if os.path.isdir(source_path):
                    in_files = os.listdir(source_path)
                    FileManager.move_files(in_files, source_path, extension, destination_dir, log_signal)
                else:
                    try:
                        if file.endswith(".pyc"):
                            # Check if the file is read-only and change it
                            if not os.access(src_dir, os.W_OK):
                                os.chmod(src_dir, stat.S_IWRITE)

                            shutil.move(source_path, destination_dir)
                            log_signal.emit(f"Moved: {source_path} -> {destination_dir}")
                        else:
                            shutil.copy(source_path, destination_dir)
                            log_signal.emit(f"Copied: {source_path} -> {destination_dir}")
                    except Exception as e :
                        log_signal.emit(f"Error Moving file from {source_path} -> to {destination_dir}, exception: {e}")

    @staticmethod
    def remove_files(files: list, dest_dir: str, log_signal):
        for file in files:
            file_path = os.path.join(dest_dir, file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    log_signal.emit(f"Error trying to move file: {file_path}, error: {e}")

    @staticmethod
    def delete_empty_sub_dirs_with_name(root_dir, target_name, log_signal: SignalInstance):
        for dir_path, dir_names, filenames in os.walk(root_dir, topdown=False):
            # Look for directories with the target name
            for dir_name in dir_names:
                if dir_name == target_name:
                    full_dir_path = os.path.join(dir_path, dir_name)
                    list_of_files = os.listdir(str(full_dir_path))
                    # Check if the directory is empty
                    if len(list_of_files) <= 0:
                        try:
                            os.rmdir(full_dir_path)
                            log_signal.emit(f"Deleted empty directory: {full_dir_path}")
                        except Exception as e:
                            log_signal.emit(f"Failed to delete directory {full_dir_path}: {e}")

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
            full_path = os.path.join(path, file)
            if os.path.isdir(file):
                FileManager.erase_dir(full_path)
            else:
                try:
                    os.remove(full_path)
                except PermissionError as e:
                    print(f"Permission error: {e}")

    @staticmethod
    def sync_directories_erase(source_path: str, dest_path: str):
        for root, dirs, files in os.walk(dest_path):
            for dir_name in dirs:
                # Construct full file path
                dir_path = os.path.join(root, dir_name)

                #ignore all git related files
                if ".git" in dir_path:
                    continue

                # Determine the relative path from the source directory
                relative_path = os.path.relpath(root, dest_path)

                source_dir = os.path.join(source_path, relative_path)
                if not os.path.exists(source_dir):
                    erase_dir = os.path.join(dest_path, relative_path)
                    FileManager.erase_dir(erase_dir)

                #erase empty directories
                files = os.listdir(dir_path)
                if len(files) <= 0:
                    FileManager.erase_dir(dir_path)

    @staticmethod
    def detect_python_version(file_path: str, log_signal:SignalInstance):
        with open(file_path, "r") as file:
            try:
                # Parse the file using Python 3's syntax
                ast.parse(file.read(), filename=file_path)
                log_signal.emit(f"{file_path} is compatible with Python 3")
                return 3
            except SyntaxError as e:
                log_signal.emit(f"{file_path} raised a SyntaxError: {e}")

                try:
                    # Try parsing again using Python 2's syntax by executing a Python 2 subprocess
                    subprocess.run(["python2", "-m", "py_compile", file_path], check=True)
                    log_signal.emit(f"{file_path} is compatible with Python 2")
                    return 2
                except subprocess.CalledProcessError:
                    log_signal.emit(f"{file_path} is not compatible with Python 2 or Python 3.")
                    return None