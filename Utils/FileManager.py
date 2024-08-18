import os
from pathlib import Path
import tomli_w
import tomli
import shutil
import compileall


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
    def add_value_to_config_file(section: str, key: str, value):
        file_path = os.path.join(FileManager.get_local_path(), "configFile.toml")
        with open(file_path, 'rb') as file:
            data = tomli.load(file)

        data[section][key] = value

        with open(file_path, 'wb') as file:
            tomli_w.dump(data, file)

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
    def compile_python_files(source_path: str):
        # WARNING: if you don't move to the working path before continue all the project files will be deleted
        FileManager.move_to(source_path)
        compileall.compile_dir(source_path)

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
