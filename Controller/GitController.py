from PySide6.QtCore import QObject, Signal, Slot, QThread
from pathlib import Path
import subprocess
import os


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
        self.repository_url_https = config["git"]["repository_url"]
        self.repository_url_ssh = config["git"]["repository_url_ssh"]
        self.git_api_url = config["git"]["gitlab_api_url"]
        self.git_hosts = config["git"]["git_hosts"]
        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self)

    def repo_exist(self) -> bool:
        git_directory = self.working_path.joinpath(".git/")
        return os.path.isdir(self.working_path) and os.path.isdir(git_directory)

    def _run_git_command(self, command) -> bool:
        command_str = " ".join(command)
        return_value = False
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True,
            )
            stdout, stderr = process.communicate()
            if stdout:
                self.log_message.emit(stdout)
                return_value = True
            if stderr:
                self.error_message.emit(f"An error occurred executing command: {command_str}, error: {stderr}")
                return_value = False
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred executing command: {command_str}, error: {e.stderr}")
            return_value = False
            raise subprocess.CalledProcessError(e.returncode, e.stderr)
        finally:
            return return_value

    @Slot()
    def setup(self):
        no_errors = True
        try:
            if not self.git_protocol.setup():
                # Import here to avoid circular import error
                from Controller.GitProtocol.GitProtocols import GitProtocolHTTPS
                self.git_protocol = GitProtocolHTTPS(self)
                if not self.git_protocol.setup():
                    self.error_message.emit(f"Communication with remote repository failed, canceling setup...")
                return False

            """ TODO: Check the first state set up, if it not finished with success code then change protocol"""
            # Change directory to the cloned repository
            os.chdir(self.working_path)
            # Set or update the remote URL (if needed)
            set_remote_command = f'git remote set-url origin {self.git_protocol.repository_url}'
            self.log_message.emit(f"Running command: {set_remote_command}")
            self._run_git_command(set_remote_command)
            # Fetch updates from the remote repository
            fetch_command = 'git fetch origin'
            self.log_message.emit(f"Running command: {fetch_command}")
            self._run_git_command(fetch_command)

            # Send setup signal
            self.log_message.emit(f" Setup Completed ")
            self.setup_completed.emit(self.repo_exist())
        except subprocess.CalledProcessError as e:
            self.log_message.emit(f"An error occurred : {e.stderr}")

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
        self._run_git_command(['git', 'remote', 'set-url', 'origin', self.git_protocol.repository_url])

        # Push changes to the remote repository
        self._run_git_command(['git', 'push', '--force', 'origin', self._get_branch_name()])

        # Check the status of the repository
        self._run_git_command(['git', 'status'])

