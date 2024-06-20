from PySide6.QtCore import QObject, Signal, Slot, QThread
import os
from pathlib import Path
import subprocess


class GitController(QObject):
    """Signals"""
    setup_completed = Signal(bool)
    log_message = Signal(str)
    error_message = Signal(str)

    def __init__(self, config: dict):
        super(GitController, self).__init__()
        self.repository_name = config["git"]["repository_name"]
        self.username = config["git"]["username"]
        self.raw_working_path = config["general"]["working_path"]
        self.working_path = Path(config["general"]["working_path"])
        self.personal_access_token = config["git"]["personal_access_token"]
        self.repository_url = config["git"]["repository_url"]

    def repo_exist(self) -> bool:
        git_directory = self.working_path.joinpath(".git/")
        return os.path.isdir(self.working_path) and os.path.isdir(git_directory)

    def _run_git_command(self, command):
        command_str = " ".join(command)
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                check=True
            )
            if result.stdout:
                self.log_message.emit(result.stdout)
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred executing command: {command_str}, error: {e.stderr}")

    @Slot()
    def setup(self):
        try:
            # Check if the directory exists
            if self.repo_exist():
                self.log_message.emit(f"The directory '{self.working_path}' already exists.")
                return
            else:
                self.log_message.emit(f"The directory '{self.working_path}' does not exist. Creating it now.")
                if not self.working_path.exists():
                    self.working_path.mkdir(parents=True)

            # Clone the repository
            clone_command = f'git clone {self.repository_url} {self.working_path}'
            self._run_git_command(clone_command)

            # Change directory to the cloned repository
            os.chdir(self.working_path)

            # Set or update the remote URL (if needed)
            set_remote_command = f'git remote set-url origin {self.repository_url}'
            self._run_git_command(set_remote_command)

            # Fetch updates from the remote repository
            fetch_command = 'git fetch origin'
            self._run_git_command(fetch_command)

            # Send setup signal
            self.setup_completed.emit(self.repo_exist())
        except subprocess.CalledProcessError as e:
            self.log_message.emit(f"An error occurred while running the command: {e}")

            # Send setup signal
            self.setup_completed.emit(self.repo_exist())

    def _get_branch_name(self) -> str:
        command = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            self.error_message.emit(result.stderr)
            return "main"

        return result.stdout.strip()

    @Slot()
    def get_latest(self):
        self.log_message.emit("getting latest...")
        # Change to the repository directory
        os.chdir(self.raw_working_path)

        # Fetch changes from the remote repository
        self._run_git_command(['git', 'fetch', 'origin'])

        # Pull the changes directly
        self._run_git_command(['git', 'pull', 'origin', self._get_branch_name()])

        # Check the status of the repository
        self._run_git_command(['git', 'status'])

    @Slot(str)
    def push_changes(self, message: str):
        self.log_message.emit("pushing changes...")
        # Change to the repository directory
        os.chdir(self.raw_working_path)

        # Add all changes to the staging area
        self._run_git_command(['git', 'add', '--all'])

        # Commit changes with a specified message
        self._run_git_command(['git', 'commit', '-m', message])

        # Ensure that the remote origin is correct
        self._run_git_command(['git', 'remote', 'set-url', 'origin', self.repository_url])

        # Push changes to the remote repository
        self._run_git_command(['git', 'push', '--force', 'origin', self._get_branch_name()])

        # Check the status of the repository
        self._run_git_command(['git', 'status'])
