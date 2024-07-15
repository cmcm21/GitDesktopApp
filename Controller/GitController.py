from PySide6.QtCore import QObject, Signal, Slot, QThread
from pathlib import Path
import subprocess
import requests
import os


class GitController(QObject):
    """Signals"""
    setup_started = Signal()
    setup_completed = Signal(bool)
    push_completed = Signal()
    get_latest_completed = Signal()
    log_message = Signal(str)
    error_message = Signal(str)
    send_main_branch = Signal(str)
    send_all_branches = Signal(list)
    send_merge_requests = Signal(list)
    send_merge_request_commits = Signal(list)
    send_merge_requests_changes = Signal(list)
    send_merge_requests_comments = Signal(list)

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
        self.project_id = config["git"]["project_id"]
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
            if stdout or "push" in command or "pull" in command:
                self.log_message.emit(stdout)
                return_value = True
            elif stderr:
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
        self.setup_started.emit()
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
        self.get_latest_completed.emit()

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
        self.push_completed.emit()

    @Slot()
    def load_merge_requests(self):
        url = self._get_merge_request_url()
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            merge_requests = response.json()
            if len(merge_requests) == 0:
                self.error_message.emit("No merge requests founded!!")
                self.send_merge_requests(merge_requests)

            self.send_merge_requests.emit(merge_requests)
        else:
            self.error_message.emit(f"Error trying to get merge requests url: {url}")

    @Slot()
    def get_main_branch(self):
        try:
            # Run the git symbolic-ref command to get the main branch name
            result = subprocess.run(
                ['git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Extract the branch name from the result
                main_branch = result.stdout.strip().replace('origin/', '')
                self.send_main_branch.emit(main_branch)
            else:
                self.error_message.emit(f"Error: {result.stderr}")
        except subprocess.CalledProcessError as e:
            self.error_message.emit("An error occurred while getting the main branch name: ", e)

    @Slot()
    def get_all_branches(self):
        try:
            # Run the git branch command to get all branches
            result = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True)
            if result.returncode == 0:
                # Extract the branches from the result
                branches = result.stdout.strip().split('\n')
                # Clean up branch names
                branches = [branch.replace('* ', '').strip() for branch in branches]
                self.send_all_branches.emit(branches)
            else:
                self.error_message.emit("Error: ", result.stderr)
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred while getting all branches: {e.stderr}")

    @Slot(int)
    def get_merge_request_commits(self, merge_request_id: int):
        url = f"{self._get_merge_request_url()}/{merge_request_id}/commits"
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            self.send_merge_request_commits.emit(commits)
        else:
            self.error_message.emit(f"Failed to load commits from : {url}")

    @Slot()
    def get_merge_requests_comments(self, merge_request_id: int):
        url = f"{self._get_merge_request_url()}/{merge_request_id}/notes"
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            comments = response.json()
            self.send_merge_requests_comments.emit(comments)
        else:
            self.error_message.emit(f"Error handling request to get comments from : {url}")
        return

    @Slot(int)
    def get_merge_request_changes(self, merge_request_id: int):
        url = f'{self._get_merge_request_url()}/{merge_request_id}/changes'
        headers = {
            'Private-Token': self.personal_access_token
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            changes = response.json().get('changes', [])
            self.send_merge_requests_changes.emit(changes)
        else:
            self.error_message.emit(f"Failed to get merge request changes, response: {response.json()}")

    @Slot(str, int)
    def merge_request_add_comment(self, comment: str, merge_request_id: int):
        url = f"{self._get_merge_request_url()}/{merge_request_id}/notes"
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        data = {"body": comment}
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 201:
            self.get_merge_requests_comments(merge_request_id)
            self.log_message.emit("Comment upload correctly")
        else:
            self.error_message.emit(f"Failed to add comment to : {url}")

    @Slot()
    def merge_request_accept_and_merge(self, merge_request_id: int, commit_message: str):
        url = f"{self._get_merge_request_url()}/{merge_request_id}/merge"
        payload = {
            "merge_commit_message": commit_message,
            'should_remove_source_branch': True
        }

        # Make the request to accept and merge the merge request
        response = requests.put(
            url,
            headers={'PRIVATE-TOKEN': self.personal_access_token},
            json=payload
        )

        if response.status_code == 200:
            self.log_message.emit("Merge request accepted and merged successfully")
            self.load_merge_requests()
        else:
            self.error_message.emit(f"Failed to accept and merge merge request: {response.status_code}")

    def _get_merge_request_url(self):
        return f"{self.git_api_url}/projects/{self.project_id}/merge_requests"

