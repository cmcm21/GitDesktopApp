import os
from pathlib import Path


class FileManager:

    @staticmethod
    def get_local_path():
        this_file_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(this_file_path, "../")

    @staticmethod
    def get_img_path() -> str:
        local_path = FileManager.get_local_path()
        icon_path = os.path.join(local_path, "Resources/Img/")
        return icon_path

    @staticmethod
    def file_exist(file: str) -> bool:
        local_path = FileManager.get_local_path()
        file_path = os.path.join(local_path, file)
        print(file_path)
        return Path(file_path).exists()

