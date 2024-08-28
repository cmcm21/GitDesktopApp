from PySide6.QtCore import QObject, Signal, Slot
from pathlib import Path
from Utils.UserSession import UserSession
from Utils.Environment import RoleID, FILE_CHANGE_DIC, CreateDir
from Utils.FileManager import FileManager
from Utils.ConfigFileManager import ConfigFileManager
from Exceptions.AppExceptions import GitProtocolException, GitProtocolErrorCode
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
    send_repository_history = Signal(list)
    send_current_changes = Signal(list, list)

    def __init__(self):
        super(GitController, self).__init__()
        self.config_manager = ConfigFileManager()
        config = self.config_manager.get_config()
        self.repository_name = config["git"]["repository_name"]
        self.username = config["git"]["username"]
        self.raw_working_path = config["general"]["working_path"]
        self.working_path = Path(config["general"]["working_path"])
        self.working_path_prefix = config['general']['repository_prefix']
        self.personal_access_token = config["git"]["personal_access_token"]
        self.repository_url_https = config["git"]["repository_url"]
        self.repository_url_ssh = config["git"]["repository_url_ssh"]
        self.git_api_url = config["git"]["gitlab_api_url"]
        self.git_hosts = config["git"]["git_hosts"]
        self.project_id = config["git"]["project_id"]
        self.user_session = None
        self.attends = 0
        self.reset_ssh = False

        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)

    def repo_exist(self) -> bool:
        git_directory = self.working_path.joinpath(".git/")
        return os.path.isdir(self.working_path) and os.path.isdir(git_directory)

    def create_repository_dir(self) -> CreateDir:
        # Check if the repository directory exists check for the directory and the .git file
        if self.repo_exist():
            self.log_message.emit(f"The directory '{self.working_path}' already exists.")
            return CreateDir.ALREADY_EXIST
        else:
            self.log_message.emit(f"Creating directory : {self.working_path} "
                                                 f"using protocol: {self.__str__()}")
            if not self.working_path.exists():
                self.working_path.mkdir(parents=True)
                return CreateDir.DIR_CREATED
            else:
                return CreateDir.JUST_DIR

    def _run_git_command(self, command: list) -> bool:
        FileManager.move_to(self.raw_working_path)
        command_str = " ".join(command)

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()
            if stdout or "push" in command or "pull" in command:
                self.log_message.emit(stdout)
                return True
            elif stderr:
                if "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!" in stderr:
                    self.reset_ssh = True
                if "fatal" in stderr:
                    self.error_message.emit(f"An error occurred executing command: {command_str}, {stderr}")
                    return False
                else:
                    self.log_message.emit(f"{stderr}")
                    return True

        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred executing command: {command_str}, error: {e.stderr}")
            raise subprocess.CalledProcessError(e.returncode, e.stderr)

    def _run_git_command_get_output(self, command) -> str:
        FileManager.move_to(self.raw_working_path)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"Git command failed: {e}")
            return ""

    def arrange_dev_push(self, comment: str):
        branch_name = self.get_dev_branch_name()
        if not self.branch_exists(branch_name):
            self.create_branch(branch_name, self._get_main_branch_name())

        self._commit_and_push_everything(comment, branch_name)
        if not self.merge_request_exists(branch_name):
            merge_request_id = self.create_merge_request(branch_name)
            if merge_request_id == -1:
                self.error_message.emit(f"Failed to create merge request for branch : {branch_name}")
            else:
                self.log_message.emit(f"merge request for branch : {branch_name} created successfully!!")
                self.add_commits_to_merge_request(merge_request_id, branch_name)

        self.load_merge_requests()

    def check_branch_exists(self, branch_name) -> bool:
        FileManager.move_to(self.raw_working_path)
        try:
            # Execute the git branch command and capture the output
            result = subprocess.run(['git', 'branch', '--list', branch_name], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            # If the branch exists, it will appear in the stdout
            return branch_name in result.stdout
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred: {e}")
            return False

    def create_local_branch(self, branch_name, source_branch):
        # Fetch latest changes from remote
        if not self._run_git_command(['git', 'fetch', 'origin']):
            print("git fetch error")
        # Checkout to source branch and pull latest changes
        if not self._run_git_command(['git', 'checkout', source_branch]):
            print("git checkout error")
        if not self._run_git_command(['git', 'pull', 'origin', source_branch]):
            print("git pull origin error")
        # Create and checkout to the new branch
        if not self.check_branch_exists(branch_name):
            self._run_git_command(['git', 'checkout', '-b', branch_name])
        else:
            self._run_git_command(['git', 'checkout', branch_name])

        return True

    def _get_main_branch_name(self) -> str:
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        # send the GET requests to fetch project details
        url = f"{self.git_api_url}/projects/{self.project_id}/repository/branches"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            branches = response.json()
            # find the main branch
            for branch in branches:
                if branch.get("default"):
                    main_branch = branch['name']
                    return main_branch

            return "main"

    def _get_main_branch_name_local(self) -> str:
        FileManager.move_to(self.raw_working_path)
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

    def branch_exists(self, branch_name):
        url = f"{self.git_api_url}/projects/{self.project_id}/repository/branches/{branch_name}"
        headers = {'PRIVATE-TOKEN': self.personal_access_token}
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    def merge_request_exists(self, branch_name):
        url = f"{self.git_api_url}/projects/{self.project_id}/merge_requests"
        headers = {'PRIVATE-TOKEN': self.personal_access_token}
        params = {'source_branch': branch_name, 'state': 'opened'}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            merge_requests = response.json()
            return len(merge_requests) > 0
        else:
            self.error_message.emit(f"error trying to check if merge request exists url: {url}, "
                                    f"code: {response.status_code}")
        return False

    def create_branch(self, branch_name, source_branch):
        url = f"{self.git_api_url}/projects/{self.project_id}/repository/branches"
        headers = {'PRIVATE-TOKEN': self.personal_access_token}
        data = {'branch': branch_name, 'ref': source_branch}
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 201:
            return True
        else:
            self.error_message.emit(f"error trying to create branch in remote url: {url}, code: {response.status_code}")
            return False

    def create_merge_request(self, branch_name) -> int:
        url = f"{self.git_api_url}/projects/{self.project_id}/merge_requests"
        headers = {'PRIVATE-TOKEN': self.personal_access_token}
        data = {
            'source_branch': branch_name,
            'target_branch': 'main',  # The branch into which the changes are merged
            'title': f'Merge request for {branch_name}',
            'remove_source_branch': True,
            'target_project_id': self.project_id
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 201:
            merge_request_id = response.json()['iid']
            print(response.json())
            if merge_request_id is not None:
                return merge_request_id
        else:
            self.error_message.emit(f"error trying to create merge request url: {url}, code: {response.status_code}")
            return -1

    def get_dev_branch_name(self):
        self.user_session = UserSession()
        return f"branch_{self.user_session.username}"

    def _commit_and_push_everything(self, comment: str, branch = ""):
        # Add all changes to the staging area
        self._run_git_command(['git', 'add', '.', '-f'])

        # Commit changes with a specified message
        self._run_git_command(['git', 'commit', '-m', comment])

        # Ensure that the remote origin is correct
        self._run_git_command(['git', 'remote', 'set-url', 'origin', self.git_protocol.repository_url])

        # Push changes to the remote repository
        if branch == "":
            self._run_git_command(['git', 'push', '--force'])
        else:
            self._run_git_command(['git', 'push', '-u', 'origin', branch])

        # Check the status of the repository
        self._run_git_command(['git', 'status'])

    def add_commits_to_merge_request(self, merge_request_id: int, branch_name: str):
        url = f"{self.git_api_url}/api/v4/projects/{self.project_id}/merge_requests/{merge_request_id}/commits"
        headers = {'PRIVATE-TOKEN': self.personal_access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            for commit in commits:
                self.log_message.emit(f"Commit {commit['id']} added to merge request.")
            return True
        return False

    def check_user_session(self):
        if self.user_session is None:
            self.user_session = UserSession()

    def get_current_branch(self):
        FileManager.move_to(self.raw_working_path)
        result = subprocess.run('git branch --show-current', capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            self.error_message.emit(f"Error getting current branch: {result.stderr}")
            return None

    def restore_git_repository(self):
        # Reset the working directory to the last commit
        self._run_git_command(['git', 'reset', '--hard'])

        # Remove all untracked files and directories
        self._run_git_command(['git', 'clean', '-fd'])

    def _get_merge_request_url(self):
        return f"{self.git_api_url}/projects/{self.project_id}/merge_requests"

    def clone_repository(self):
        clone_command = f'git clone {self.git_protocol.repository_url} {self.working_path}'
        self.log_message.emit(clone_command)
        self._run_git_command(['git', 'clone', self.git_protocol.repository_url, self.raw_working_path])

    def check_and_add_origin(self, url):
        result = self._run_git_command_get_output(['git', 'remote'])
        remotes = result.splitlines()
        if "origin" in remotes:
            self.log_message.emit(f"Remote 'origin' is already added")
        else:
            self._run_git_command(['git', 'remote', 'add', 'origin', url])

    def check_working_path(self):
        if self.raw_working_path == "":
            self.raw_working_path = FileManager.get_working_path(
                self.config_manager.get_config()["general"]["repository_prefix"],"default")
            print(self.raw_working_path)
            self.config_manager.add_value("general","working_path", self.raw_working_path)
            self.working_path = Path(self.raw_working_path)

    def catch_ssh_connection_error(self):
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        if isinstance(self.git_protocol, GitProtocolSSH) and self.attends < 2:
            self.attends += 1
            self.git_protocol.remove_offending_host_key()
            self.git_protocol.reconnect_to_host()
            self.setup()

    @Slot()
    def setup(self):
        self.check_working_path()

        self.setup_started.emit()
        no_errors = True
        try:
            if not self.git_protocol.setup():
                print("initial setup with ssh failed")
                # Import here to avoid circular import error
                from Controller.GitProtocol.GitProtocols import GitProtocolHTTPS
                self.git_protocol = GitProtocolHTTPS(self, self.repository_url_https)
                if not self.git_protocol.setup():
                    raise GitProtocolException("None SSH Nether HTTP Protocols could setup correctly",
                                               GitProtocolErrorCode.SETUP_FAILED)

            """ TODO: Check the first state set up, if it not finished with success code then change protocol"""
            # Change directory to the cloned repository
            os.chdir(self.working_path)
            self.check_and_add_origin(self.git_protocol.repository_url)
            # Set or update the remote URL (if needed)
            set_remote_command = f'git remote set-url origin {self.git_protocol.repository_url}'
            self.log_message.emit(f"Running command: {set_remote_command}")
            self._run_git_command(['git', 'remote', 'set-url', 'origin', self.git_protocol.repository_url])
            # Verify remote repository
            self._run_git_command(['git', 'ls-remote', '--get-url', 'origin'])
            # Fetch updates from the remote repository
            fetch_command = 'git fetch origin'
            self.log_message.emit(f"Running command: {fetch_command}")
            self._run_git_command(['git', 'fetch', 'origin'])
            # Send setup signal
            self.log_message.emit(f" Setup Completed ")
            self.setup_completed.emit(self.repo_exist())

            if self.reset_ssh:
                self.reset_ssh = False
                return self.catch_ssh_connection_error()

        except Exception as e:
            self.log_message.emit(f"An error occurred : {e}")

    @Slot(str)
    def push_changes(self, message: str):
        self.check_user_session()
        self.log_message.emit("pushing changes...")
        if self.user_session.role_id == RoleID.DEV.value:
            self.arrange_dev_push(message)
        else:
            self._commit_and_push_everything(message)
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
            self.error_message.emit(f"Failed to accept and merge MR: {response.status_code}, url: {url}")

    @Slot()
    def verify_user_branch(self):
        self.check_user_session()
        current_branch = self.get_current_branch()
        if self.user_session.role_id == RoleID.DEV.value:
            if current_branch != self.get_dev_branch_name():
                self.create_local_branch(self.get_dev_branch_name(), self._get_main_branch_name())
        else:
            if current_branch != self._get_main_branch_name():
                self._run_git_command(['git', 'checkout', self._get_main_branch_name()])

    @Slot()
    def get_repository_history(self):
        output = self._run_git_command_get_output(["git", "log", "--pretty=format:%h - %s (%ci)"])
        if output:
            commits = output.splitlines()
            self.send_repository_history.emit(commits)

    @Slot()
    def get_repository_changes(self):
        changes_modified = []
        other_changes = []
        changed_files_out = self._run_git_command_get_output(['git', 'status', '--porcelain'])
        if changed_files_out:
            changed_files = [(line[:3].replace(" ", ""), line[3:]) for line in changed_files_out.splitlines() if line]
            for change, changed_file in changed_files:
                if change == "M":
                    diff = self._run_git_command_get_output(['git', 'diff', changed_file])
                    if diff:
                        changes_modified.append((changed_file, diff))
                else:
                    if not change in FILE_CHANGE_DIC:
                        other_changes.append((changed_file,"Unknown change"))
                    else:
                        other_changes.append((changed_file, FILE_CHANGE_DIC[change]))

        self.send_current_changes.emit(changes_modified, other_changes)

    @Slot()
    def get_latest(self):
        # restore all the modified files before get latest
        self.restore_git_repository()

        self.log_message.emit("getting latest...")
        # Change to the repository directory
        os.chdir(self.raw_working_path)

        # Fetch changes from the remote repository
        self._run_git_command(['git', 'fetch', 'origin'])

        # Pull the changes directly
        self._run_git_command(['git', 'pull', 'origin', self._get_main_branch_name()])

        # Check the status of the repository
        self._run_git_command(['git', 'status'])
        self.get_latest_completed.emit()

    @Slot(str)
    def on_setup_working_path(self, path: str):
        real_path = os.path.join(path, self.working_path_prefix, "default")
        animator_path = os.path.join(path, self.working_path_prefix, "animator")
        self.raw_working_path = real_path
        self.working_path = Path(real_path)

        self.config_manager.add_value("general", "working_path", real_path)
        self.config_manager.add_value("general", "animator_path", animator_path)
        self.setup()

    @Slot()
    def on_log_out(self):
        self.attends = 0