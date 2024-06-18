from PySide6.QtCore import QObject, Signal, Slot
from threading import Thread
import os
from pathlib import Path
import subprocess


class GitController(QObject):
    """Signals"""
    setup_completed = Signal(bool)

    def __init__(self, config: dict, logger):
        super().__init__()
        self.repository_name = config["git"]["repository_name"]
        self.username = config["git"]["username"]
        self.working_path = Path(config["general"]["working_path"])
        self.personal_access_token = config["git"]["personal_access_token"]
        self.repository_url = config["git"]["repository_url"]
        self.logger = logger

    def repo_exist(self) -> bool:
        git_directory = self.working_path.joinpath(".git/")
        return os.path.isdir(self.working_path) and os.path.isdir(git_directory)

    def _run_git_command(self, command):
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            check=True,
            capture_output=True,
        )

        self.logger.debug(result.stdout)
        if result.stderr and result.stderr:
            self.logger.error(result.stderr)

    def setup(self):
        setup_thread = Thread(target=self._setup_thread)
        setup_thread.run()
        return

    def _setup_thread(self):
        try:
            # Check if the directory exists
            if self.repo_exist():
                self.logger.debug(f"The directory '{self.working_path}' already exists.")
                return
            else:
                self.logger.debug(f"The directory '{self.working_path}' does not exist. Creating it now.")
                if not self.working_path.exists():
                    self.working_path.mkdir(parents=True)

            # Clone the repository
            clone_command = f'git clone {self.repository_url} {self.working_path}'
            self.logger.debug(f"Cloning the repository: {clone_command}")
            self._run_git_command(clone_command)

            # Change directory to the cloned repository
            os.chdir(self.working_path)

            # Set or update the remote URL (if needed)
            set_remote_command = f'git remote set-url origin {self.repository_url}'
            self.logger.debug(f"Setting the remote URL: {set_remote_command}")
            self._run_git_command(set_remote_command)

            # Fetch updates from the remote repository
            fetch_command = 'git fetch origin'
            self.logger.debug(f"Fetching updates: {fetch_command}")
            self._run_git_command(fetch_command)

            # Send setup signal
            self.setup_completed.emit(self.repo_exist())
        except subprocess.CalledProcessError as e:
            self.logger.error(f"An error occurred while running the command: {e}")

            # Send setup signal
            self.setup_completed.emit(self.repo_exist())

    def _get_branch_name(self) -> str:
        # Change to the repository directory
        subprocess.run(['cd', self.working_path], shell=True)

        command = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            self.logger.debug(result.stderr)
            return "main"

        return result.stdout.strip()

    @Slot()
    def get_latest(self):
        print("Get latest button clicked")

    @Slot(str)
    def upload_repository(self, message):
        print("From GitController: " + message)

    @Slot(str)
    def push_changes(self, commit_message: str):
        # Change to the repository directory
        subprocess.run(['cd', self.working_path], shell=True)

        # Add all changes to the staging area
        self._run_git_command(['git', 'add', '--all'])

        # Commit changes with a specified message
        self._run_git_command(['git', 'commit', '-m', commit_message])

        # Push changes to the remote repository
        self._run_git_command(['git', 'push', '-force', 'origin', self._get_branch_name()])

        # Check the status of the repository
        self._run_git_command(['git', 'status'])
