from PySide6.QtCore import QObject, Signal, Slot
import git
import os


class FileLockController(QObject):
    message_log = Signal(str)
    error_log = Signal(str)

    def __init__(self, config_file: dict, rep_url: str):
        super(FileLockController).__init__()
        self.config_file = config_file
        self.lock_path = config_file['lock_rep']['path']
        self.private_token = config_file['git']['personal_access_token']
        self.source_project_name = config_file['git']['repository_name']
        self.repository_url = rep_url

    def setup(self) -> bool:
        return True

    def create_lock_repo(self):
        if not os.path.exists(self.lock_path):
            os.makedirs(self.lock_path)

        repo = git.Repo.init(self.lock_path)
        with open(os.path.join(self.lock_path, 'README.md'), 'w') as f:
            f.write('# New Repository\nThis is a new repository.')

        repo.index.add(['README.md'])
        repo.index.commit('Initial commit')
        return repo

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


