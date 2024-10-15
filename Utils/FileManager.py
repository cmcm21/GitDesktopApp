from PySide6.QtCore import SignalInstance, QObject, Signal
import os
import fnmatch
from pathlib import Path
import shutil
import py_compile
import subprocess


def get_working_path(default_path: str, user_role: str) -> str:
    """
    :param default_path: the default workspace name (dev/admin)
    :param user_role: the role of the user
    :return: the complete workspace path
    """
    current_script = Path(__file__).resolve()
    project_path = current_script.parents[2]
    work_path = os.path.join(project_path, default_path, user_role)
    return work_path

def path_exists(path: str) -> bool:
    return os.path.isdir(path)


def get_local_path() -> str:
    """
    :return: the absolute path of the application
    """
    this_file_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_file_path, "../")


def get_img_path(img_path: str) -> str:
    """
    :param img_path: image (.jpg/.png) file name
    :return: the absolute path of the image
    """
    local_path = get_local_path()
    icon_path = os.path.join(local_path, "Resources/Img/", img_path)
    return icon_path


def file_exist(file: str) -> bool:
    """
    :param file: the file to check if exist or not
    :return: true if the file exist false otherwise
    """
    local_path = get_local_path()
    file_path = os.path.join(local_path, file)
    return Path(file_path).exists()


def in_path(path: str) -> bool:
    return os.curdir == path


def join_with_local_path(path: str) -> str:
    return os.path.join(get_local_path(), "Data/")


def create_dir(path:str) -> None:
    os.mkdir(path)


def dir_exist(path: str) -> bool:
    return os.path.exists(path)


def move_to(path: str) -> None:
    """
    move the current system cursor path to the path passed
    :param path: absolute path to move the os cursor
    :return: None
    """
    if not in_path(path):
        try:
            os.chdir(path)
        except Exception as e:
            print(f"Error trying to execute os.chdir : {e}")


def move_to_local_dir() -> None:
    """
    move the os cursor to the application absolute path
    :return:
    """
    if not in_path(get_local_path()):
        move_to(get_local_path())


def move_dir(source_path: str, dist_path: str):
    """
    :param source_path: absolute path of the dir to move
    :param dist_path: absolute path of the destination dir
    :return:
    """
    if not os.path.exists(dist_path):
        os.mkdir(dist_path)
    if os.path.exists(source_path) and os.path.isdir(source_path):
        try:
            shutil.move(source_path, dist_path)
        except Exception as e:
            print(f"Error moving directory from {source_path} to {dist_path}: {e}")


def erase_dir(source_path: str):
    """
    :param source_path:  absolute path to erase
    :return:
    """
    try:
        if os.path.exists(source_path) and os.path.isdir(source_path):
            shutil.rmtree(source_path)
    except PermissionError as pr:
        print("Error trying to remove path")



def ensure_all_files_extension(directory, extension) -> bool:
    """
    :param directory: the absolute path where we are going to look in
    :param extension: the type of file to look for in directory
    :return: true if all files are the same type false otherwise
    """
    files = os.listdir(directory)
    return all(file.endswith(extension) for file in files)


def dir_empty(path: str):
    return not os.listdir(path)


def get_dir_files_count(path: str):
    return len(os.listdir(path))


def compile_all_python_files(source_path: str, log_signal:SignalInstance) -> None:
    """
    :param source_path: the source file where the python file are located
    :param log_signal: signal to show messages in the UI
    """
    move_to(source_path)

    log_signal.emit(f"Compiling files in {source_path}")
    for dir_path, dir_names, files in os.walk(source_path):
        for file in files:
            log_signal.emit(f"Listing file {file}")
            file = fr"{file.strip()}"
            file_path = fr"{os.path.join(dir_path, file)}".strip()
            if file.endswith(".py"):
                compile_python_file(file_path, log_signal)

    log_signal.emit(f"Compilation finished")


def compile_python_files(source_path: str, files: list[str], log_signal: SignalInstance) -> None:
    """
    :param source_path: The default workspace path (admin/dev working path)
    :param files: The files that are going to be compiled (you can pass not .py files as well)
                    the compiled files are added in the files list if the .py was compiled successfully
    :param log_signal: signal that show log messages in the ui
    """
    move_to(source_path)
    log_signal.emit(f"Compiling files: {files}")

    for file in files:
        file_path = fr"{os.path.join(source_path, file)}".strip()
        if not os.path.exists(file_path):
            log_signal.emit(f"file: {file_path} doesn't exist")
            continue

        if os.path.isdir(file_path):
            files = os.listdir(file_path)
            log_signal.emit(f"Compiling dir {file}...")
            compile_python_files(file_path, files, log_signal)

        elif file_path.endswith(".py"):
            if compile_python_file(file_path, log_signal):
                # we add the compiled file to the files list
                file = file.replace(".py",".pyc")
                files.append(file)

    log_signal.emit(f"Compiling files finished")


def compile_python_file(file_path: str, log_signal: SignalInstance) -> bool:
    """
    :param file_path: full path of the file to compile
    :param log_signal: signal to show messages in the UI
    :return: true if compile was successfully and false otherwise
    """
    return_value = True
    try:
        if os.path.exists(file_path):
           python_version = detect_python_version_by_features(file_path)
           log_signal.emit(f"Compiling file {file_path}... using python {python_version}")

           if python_version == 2:
               if not compile_python2_file(file_path, log_signal):
                   py_compile.compile(file_path, cfile=file_path+"c", doraise=True)
           else:
               py_compile.compile(file_path, cfile=file_path+"c", doraise=True)

           log_signal.emit(f"Compile file {file_path} successfully")
           return_value = True
        else:
            return_value = False
            log_signal.emit(f"file: {file_path} doesn't found")

    except py_compile.PyCompileError as e:
        log_signal.emit(f"Error compiling {file_path} : {e}")
        return_value = False
    except Exception as e:
        log_signal.emit(f"Unexpected error: {e}")
        return_value = False
    finally:
        return return_value


def compile_python2_file(file_path: str, log_signal: SignalInstance) -> bool:
    """
    This function compiles a file using python 2 version
    :param file_path:  the full path (absolute path) of the file
    :param log_signal: log signal to show messages in the UI
    :return: None
    """
    from Utils.ConfigFileManager import ConfigFileManager

    config_manager = ConfigFileManager()
    python2_alias = config_manager.get_config()['general']['python2_alias']
    try:
        result = subprocess.run([python2_alias, "-m", "py_compile", file_path], check=True)
        log_signal.emit(f"file: {file_path} compiled successfully")
        return True
    except subprocess.CalledProcessError:
        log_signal.emit(f"file: {file_path} compiled error")
        return False


def find_files(pattern, extension, directory) -> list:
    """
    Look up for a pattern in a specific type of file inside the directory
    :param pattern: the pattern that we are looking for inside the directory
    :param extension: the type of file where we are searching the pattern
    :param directory: the directory where we are going to look for the pattern
    :return: a list that contains all the files .extension that contains the pattern
    """
    matches = []
    # Traverse the directory tree
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(f".{extension}") and pattern in file:
                full_path = os.path.join(root, fr"{file}")
                matches.append(full_path)

    return matches


def get_files_extension(extension, directory) -> list:
    """
    :param extension: the extension we're looking for
    :param directory: the directory path where we are looking for
    :return: a list with all the matches
    """
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


def find_directories(pattern: str, root_directory: str):
    """
    :param pattern: the pattern that we are looking for
    :param root_directory: the directory where we will be looking for
    :return:
    """
    directories = []

    for root, dirs, files in os.walk(root_directory):
        for dir_name in fnmatch.filter(dirs, pattern):
            directories.append(os.path.join(root, dir_name))

    return directories


def copy_all_files(src_dir: str, dst_dir: str, log_signal: SignalInstance):
    """
    move all the files from src_dir to dst_dir except for those of type extension
    :param src_dir: the absolute path of the where the files are located originally
    :param dst_dir: the absolute path where the files are going to be moved to
    :param log_signal: a signal to show messages in the UI
    :return: None
    """
    for root, dirs, files in os.walk(src_dir):
        for file in files:
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

            try:
                shutil.copy(file_path, os.path.join(destination_dir, file))
                log_signal.emit(f"Copied: {file_path} -> {os.path.join(destination_dir, file)}")

            except Exception as e:
                log_signal.emit(f"Exception trying to copy file: {file_path} -> error: {e}")


def copy_files(files: list[str], src_dir: str, dst_dir:str, log_signal: SignalInstance, attends=0):
    """
    :param files: a list of all the files that are going to be moved
    :param src_dir: the source absolute path where all the files are located
    :param dst_dir: the destination path where all the files are going to be moved
    :param log_signal: a signal to show messages to the UI
    :param attends: the number of attend that you have try to move the files
    """

    # Ensure the extension starts with a dot
    log_signal.emit(f"Moving files : {files}")
    os.makedirs(dst_dir, exist_ok=True, mode=0o777)

    for file in files:
        file = file.strip()

        source_path = os.path.join(src_dir, file)
        destination_dir = os.path.join(dst_dir, file)

        if os.path.isdir(source_path):
            in_files = os.listdir(source_path)
            copy_files(in_files, source_path, destination_dir, log_signal)
        else:
            try:
                shutil.copy(fr"{source_path.strip()}", fr"{destination_dir.strip()}")
                log_signal.emit(f"Copied: {source_path.strip()} -> {destination_dir.strip()}")

            except Exception as e:
                log_signal.emit(f"Error Moving file from {source_path} -> to {destination_dir}, exception: {e}")
                if attends <= 2:
                    attends += 1
                    copy_files(files, src_dir, dst_dir, log_signal, attends)


def remove_files_in_path(path: str, file_extension: str, log_signal:SignalInstance):
    """
    :param path: the absolute path where we have to erase the files
    :param file_extension: the type of file to erase
    :param log_signal: a help signal so show log messages in the UI
    :return:
    """
    if not file_extension.startswith("."):
        file_extension = "." + file_extension

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(file_extension):
                # Construct full file path
                file_path = os.path.join(root, file)

                #ignore all git related files
                if ".git" in file_path:
                    continue

                try:
                    os.remove(file_path)
                    log_signal.emit(f"file deleted: {file_path} -> {file_path}")

                except Exception as e:
                    log_signal.emit(f"Exception trying to delete file: {file_path} -> error: {e}")



def remove_files(files: list[str], dest_dir: str, log_signal):
    """
    :param files: list of files to remove
    :param dest_dir: the destination directory where we are looking for files list
    :param log_signal: a signal to show messages to the UI
    """
    for file in files:
        if file.endswith(".py"):
            file = file.replace(".py", ".pyc")

        file_path = os.path.join(dest_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                log_signal.emit(f"remove file: {file_path} successfully!!")
            except Exception as e:
                log_signal.emit(f"Error trying to remove file: {file_path}, error: {e}")


def delete_empty_sub_dirs(root_dir, log_signal: SignalInstance):
    """
    :param root_dir: the root directory where we are going to
    :param log_signal: a signal to show messages in the UI
    """
    for dir_path, dir_names, filenames in os.walk(root_dir, topdown=False):
        # Look for directories with the target name
        for dir_name in dir_names:
            full_dir_path = os.path.join(dir_path, dir_name)
            list_of_files = os.listdir(str(full_dir_path))
            # Check if the directory is empty
            if len(list_of_files) <= 0:
                try:
                    os.rmdir(full_dir_path)
                    log_signal.emit(f"Deleted empty directory: {full_dir_path}")
                except Exception as e:
                    log_signal.emit(f"Failed to delete directory {full_dir_path}: {e}")


def get_os_root_dir():
    return os.path.abspath(os.sep)


def join_with_os_root_dir(path: str) -> str:
    return os.path.join(get_os_root_dir(), path)


def erase_dir_files(path: str):
    """
    :param path: the path were we are going to erase the files
    """
    files = os.listdir(path)
    for file in files:
        full_path = os.path.join(path, file)
        if os.path.isdir(file):
            erase_dir(full_path)
        else:
            try:
                os.remove(full_path)
            except PermissionError as e:
                print(f"Permission error: {e}")


def sync_directories(source_path: str, dest_path: str, log_signal: SignalInstance) -> list:
    """
    erase all the files that exist in the dest_path and don't in the source_path
    :param source_path: the source absolute path where we are going to sync the directories
    :param dest_path: the destination absolute path to sync with
    :param log_signal: signal to show messages in the UI
    :return: a list with all absolute path of the files deleted
    """
    deleted_files = []
    for root, dirs, files in os.walk(dest_path):
        for file in files:
            file_path = fr"{os.path.join(root, file)}".strip()
            #ignore all .git related files
            if ".git" in file_path:
                continue

            relative_path = os.path.relpath(root, dest_path)
            source_file = os.path.join(source_path, relative_path)
            to_remove_file = os.path.join(source_file,file)

            if not os.path.exists(to_remove_file):
                # if it is a .pyc file we check if the .py file or the .pyc file exist in the default repo
                # if it exists, then we don't remove this file
                if file_path.endswith(".pyc"):
                    py_file = to_remove_file.replace(".pyc", ".py")
                    if os.path.exists(py_file):
                        continue
                try:
                    log_signal.emit(f"Removing file: {file_path}")
                    os.remove(file_path)
                    deleted_files.append(file_path)
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
                erase_dir(dir_path)
                deleted_files.append(dir_path)
            else:
                dir_files = os.listdir(dir_path)
                if len(dir_files) <= 0:
                    log_signal.emit(f"Removing empty directory {dir_path}")
                    erase_dir(dir_path)
                    deleted_files.append(dir_path)

                src_path = dir_path.replace("animator", "default")
                if os.path.exists(src_path):
                    src_files = os.listdir(src_path)
                    if len(src_files) <= 0:
                        erase_dir(src_path)

    return deleted_files

def detect_python_version_by_features(file_path):
    """
    :param file_path: the absolute path of the python file
    :return: the python version of the file_path python file
    """
    python2_keywords = ["print ", "xrange(", "basestring", "unicode"]
    python3_keywords = ["print(", "range(", "str", "bytes"]

    with open(file_path, "r") as file:
        content = file.read()

        if any(keyword in content for keyword in python2_keywords):
            return 2
        elif any(keyword in content for keyword in python3_keywords):
            return 3

    return 3