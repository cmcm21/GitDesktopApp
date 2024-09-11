import io
import sys
import os
import stat
import fnmatch
from PySide6.QtCore import SignalInstance, QObject, Signal
from pathlib import Path
import shutil
import py_compile
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
            try:
                os.chdir(path)
            except Exception as e:
                print(f"Error trying to execute os.chdir : {e}")

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
    def compile_python_files_from_source(source_path: str, log_signal:SignalInstance):
        FileManager.move_to(source_path)

        log_signal.emit(f"Compiling files in {source_path}")
        for dir_path, dir_names, files in os.walk(source_path):
            for file in files:
                log_signal.emit(f"Listing file {file}")
                file = fr"{file.strip()}"
                file_path = fr"{os.path.join(dir_path, file)}".strip()
                if file.endswith(".py"):
                    FileManager.compile_python_file(file_path, log_signal)

        log_signal.emit(f"Compilation finished")

    @staticmethod
    def compile_python_files(source_path: str, files: list, log_signal: SignalInstance):
        FileManager.move_to(source_path)
        log_signal.emit(f"Compiling files: {files}")

        for file in files:
            file_path = fr"{os.path.join(source_path, file)}".strip()
            if not os.path.exists(file_path):
                continue

            if os.path.isdir(file_path):
                files = os.listdir(file_path)
                log_signal.emit(f"Compiling dir {file}...")
                FileManager.compile_python_files(source_path, files, log_signal)

            elif file_path.endswith(".py"):
                FileManager.compile_python_file(file_path, log_signal)

        log_signal.emit(f"Compiling files finished")

    @staticmethod
    def compile_python_file(file_path: str, log_signal: SignalInstance):
        try:
            if os.path.exists(file_path):
               python_version = FileManager.detect_python_version_by_features(file_path)
               log_signal.emit(f"Compiling file {file_path}...")

               if python_version == 2:
                   FileManager.compile_python2_file(file_path, log_signal)
               else:
                   # Get the directory and file name separately
                   dir_name, file_name = os.path.split(file_path)
                   # Construct the compiled file name (same name but with .pyc extension)
                   compiled_file_name = os.path.splitext(file_name)[0] + ".pyc"
                   # Create the full path for the compiled file
                   compiled_file_path = os.path.join(dir_name, compiled_file_name)
                   py_compile.compile(file_path, cfile=compiled_file_path, doraise=True)

               log_signal.emit(f"Compile file {file_path} successfully")
            else:
               log_signal.emit(f"file: {file_path} doesn't found")
        except py_compile.PyCompileError as e:
            log_signal.emit(f"Error compiling {file_path} : {e}")

        except Exception as e:
            log_signal.emit(f"Unexpected error: {e}")

    @staticmethod
    def compile_python2_file(file_path: str, log_signal: SignalInstance):
        from Utils.ConfigFileManager import ConfigFileManager

        config_manager = ConfigFileManager()
        python2_alias = config_manager.get_config()['general']['python2_alias']

        result = subprocess.run([python2_alias, "-m", "py_compile", file_path], check=True)
        if result.returncode == 0:
            log_signal.emit(f"file: {file_path} compiled successfully")
        else:
            log_signal.emit(f"file: {file_path} compiled error")


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
                if ".git" in root:
                    continue

                if file.endswith(extension):
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
    def move_files(files: list, src_dir: str, ignore: str, dst_dir:str, log_signal: SignalInstance, attends=0):
        # Ensure the extension starts with a dot
        if not ignore.startswith('.'):
            ignore = '.' + ignore

        os.makedirs(dst_dir, exist_ok=True, mode=0o777)

        for file in files:
            file = file.strip()
            if not file.endswith(ignore):

                source_path = os.path.join(src_dir, file)
                destination_dir = os.path.join(dst_dir, file)

                if os.path.isdir(source_path):
                    in_files = os.listdir(source_path)
                    FileManager.move_files(in_files, source_path, ignore, destination_dir, log_signal)
                else:
                    try:
                        if file.endswith(".pyc"):
                            # Check if the file is read-only and change it
                            if not os.access(src_dir, os.W_OK):
                                os.chmod(src_dir, stat.S_IWRITE)

                            shutil.move(fr"{source_path.strip()}", fr"{destination_dir.strip()}")
                            log_signal.emit(f"Moved: {source_path} -> {destination_dir}")
                        else:
                            shutil.copy(fr"{source_path.strip()}", fr"{destination_dir.strip()}")
                            log_signal.emit(f"Copied: {source_path.strip()} -> {destination_dir.strip()}")

                    except Exception as e :
                        log_signal.emit(f"Error Moving file from {source_path} -> to {destination_dir}, exception: {e}")
                        if attends <= 2:
                            attends += 1
                            FileManager.move_files(files, src_dir, ignore, dst_dir, log_signal, attends)

    @staticmethod
    def remove_files(files: list, dest_dir: str, log_signal):
        for file in files:
            if file.endswith(".py"):
                file = file.replace(".py",".pyc")

            file_path = os.path.join(dest_dir, file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    log_signal.emit(f"Error trying to remove file: {file_path}, error: {e}")

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
    def sync_directories(source_path: str, dest_path: str, log_signal: SignalInstance):
        for root, dirs, files in os.walk(dest_path):
            for file in files:
                file_path = fr"{os.path.join(root, file)}".strip()
                #ignore all .git related files
                if ".git" in file_path:
                    continue

                relative_path = os.path.relpath(root, dest_path)
                source_file = os.path.join(source_path, relative_path)
                to_remove_file = os.path.join(source_file,file)

                if to_remove_file.endswith(".pyc"):
                    to_remove_file = to_remove_file.replace(".pyc", ".py")

                if not os.path.exists(to_remove_file):
                    try:
                        log_signal.emit(f"Removing file: {file_path}")
                        os.remove(file_path)
                    except Exception as e:
                        log_signal.emit(f"Exception occur while trying to erase file: {file_path} error({e}),"
                              f" source file: {source_file}")
                        continue

            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)

                if ".git" in dir_path:
                    continue

                relative_path = os.path.relpath(root, dest_path)
                source_dir = os.path.join(source_path, relative_path)
                if not os.path.exists(source_dir):
                    log_signal.emit(f"Removing empty directory {dir_path}")
                    FileManager.erase_dir(dir_path)

                files = os.listdir(dir_path)
                if len(files) <= 0:
                    log_signal.emit(f"Removing empty directory {dir_path}")
                    FileManager.erase_dir(dir_path)

    @staticmethod
    def detect_python_version_by_features(file_path):
        python2_keywords = ["print ", "xrange(", "basestring", "unicode"]
        python3_keywords = ["print(", "range(", "str", "bytes"]

        with open(file_path, "r") as file:
            content = file.read()

            if any(keyword in content for keyword in python2_keywords):
                return 2
            elif any(keyword in content for keyword in python3_keywords):
                return 3

        return None