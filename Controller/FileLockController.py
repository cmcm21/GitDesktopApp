from PySide6.QtCore import QObject, Signal


class FileLockController(QObject):
    message_log = Signal(str)
    error_log = Signal(str)

    def __init__(self, config_file: dict, rep_url: str):
        return

    def setup(self) -> bool:
        return True

    def create_lock_repo(self):
        return

    def create_remote_repo(self):
        return

    def get_latest(self):
        return

    def lock_rep_exists(self) -> bool:
        return True

    def read_file(self):
        return

    def lock_file(self):
        return

    def unlock_file(self):
        return


