import git
from PySide6.QtCore import QObject, Signal, Slot
from pathlib import Path
from Utils.UserSession import UserSession
from Utils.Environment import RoleID, FILE_CHANGE_DIC, CreateDir
from Utils import FileManager
from Utils.ConfigFileManager import ConfigFileManager
from Exceptions.AppExceptions import GitProtocolException, GitProtocolErrorCode
import subprocess
import requests
import os


class GitController(QObject):
    """Signals"""
    setup_started = Signal()
    setup_completed = Signal(bool, str)
    push_and_commit_started = Signal()
    push_and_commit_completed = Signal(str, list)
    auto_publish_started = Signal()
    auto_publish_completed = Signal()
    get_latest_started = Signal()
    get_latest_completed = Signal()
    accept_merge_started = Signal()
    accept_merge_completed = Signal()
    reset_started = Signal()
    reset_completed = Signal()
    branching_started = Signal()
    branching_completed = Signal()
    load_mr_started = Signal()
    load_mr_completed = Signal()
    add_comment_started = Signal()
    add_comment_completed = Signal()
    get_mr_changes_started = Signal()
    get_mr_changes_completed = Signal()
    get_mr_comments_started = Signal()
    get_mr_comments_completed = Signal()
    get_mr_commits_started = Signal()
    get_mr_commits_completed = Signal()

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
    refreshing = Signal()
    refreshing_completed = Signal()

    def __init__(self):
        super(GitController, self).__init__()
        self.user_session = None
        self.attends = 0
        self.reset_ssh = False
        self.config()
        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)

    def config(self):
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

    def repo_exist(self) -> bool:
        git_directory = self.working_path.joinpath(".git/")
        return os.path.isdir(self.working_path) and os.path.isdir(git_directory)

    def create_repository_dir(self) -> CreateDir:
        # Check if the repository directory exists check for the directory and the .git file
        if self.repo_exist():
            self.log_message.emit(f"The directory '{self.working_path}' already exists.")
            return CreateDir.ALREADY_EXIST
        else:
            self.log_message.emit(f"Creating directory : {self.working_path} " f"using protocol: {self.__str__()}")
            if not self.working_path.exists():
                self.working_path.mkdir(parents=True)
                return CreateDir.DIR_CREATED
            else:
                return CreateDir.JUST_DIR

    def run_command(self, command: list) -> bool:
        FileManager.move_to(self.raw_working_path)
        command_str = " ".join(command)

        self.log_message.emit(f"Running command: {command_str}...")
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            stdout, stderr = process.communicate()
            if stdout or "push" in command or "pull" in command:
                self.log_message.emit(stdout)
                return True

            elif stderr:
                if "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!" in stderr:
                    self.reset_ssh = True
                if "dubious ownership"  in stderr:
                    self.run_command(["git", "config", "--global", "--add", "safe.directory", self.raw_working_path])
                    self.log_message.emit(f"an error occur running the command: {stderr}")
                    return False
                elif "fatal" in stderr:
                    self.error_message.emit(f"An error occurred executing command: {command_str}, {stderr}")
                    return False
                else:
                    self.log_message.emit(f"error occurred executing command {command_str}: error{stderr}")
                    return True

        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred executing command: {command_str}, error: {e.stderr}")
            raise subprocess.CalledProcessError(e.returncode, e.stderr)

    def _run_git_command_get_output(self, command: list) -> str:
        FileManager.move_to(self.raw_working_path)
        self.log_message.emit(f"Running command: {" ".join(command)}...")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"Git command ({command}) failed: {e}")
            return ""

    def arrange_dev_push(self, comment: str, changes: list[str]):
        branch_name = self.get_dev_branch_name()
        if not self.branch_exists(branch_name):
            self.create_branch(branch_name, self._get_main_branch_name())

        self._commit_and_push(comment, changes, branch_name)
        if not self.merge_request_exists(branch_name):
            merge_request_id = self.create_merge_request(branch_name)
            if merge_request_id == -1:
                self.error_message.emit(f"Failed to create merge request for branch : {branch_name}")
            else:
                self.log_message.emit(f"merge request for branch : {branch_name} created successfully!!")
                self.add_commits_to_merge_request(merge_request_id, branch_name)

        self.load_merge_requests(False)

    def check_branch_exists(self, branch_name: str) -> bool:
        FileManager.move_to(self.raw_working_path)
        try:
            # Execute the git branch command and capture the output
            result = subprocess.run(['git', 'branch', '--list', branch_name], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True,creationflags = subprocess.CREATE_NO_WINDOW)
            # If the branch exists, it will appear in the stdout
            return branch_name in result.stdout
        except subprocess.CalledProcessError as e:
            self.error_message.emit(f"An error occurred: {e}")
            return False

    def create_local_branch(self, branch_name: str, source_branch: str):
        # Fetch latest changes from remote
        if not self.run_command(['git', 'fetch', 'origin']):
            self.log_message.emit("git fetch error")

        # Checkout to source branch and pull latest changes
        if not self.run_command(['git', 'checkout', source_branch]):
            self.log_message.emit("git checkout error")

        if not self.run_command(['git', 'pull', 'origin', source_branch]):
            self.log_message.emit("git pull origin error")

        # Create and checkout to the new branch
        if not self.check_branch_exists(branch_name):
            self.run_command(['git', 'checkout', '-b', branch_name])
        else:
            self.run_command(['git', 'checkout', branch_name])

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
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode != 0:
            self.error_message.emit(result.stderr)
            return "main"
        return result.stdout.strip()

    def branch_exists(self, branch_name: str):
        url = f"{self.git_api_url}/projects/{self.project_id}/repository/branches/{branch_name}"
        headers = {'PRIVATE-TOKEN': self.personal_access_token}
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    def merge_request_exists(self, branch_name: str):
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

    def create_branch(self, branch_name: str, source_branch: str):
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
        self.log_message.emit(f"Creating Merge request...")
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
            self.log_message.emit(f"Merge request created successfully!!")
        else:
            self.error_message.emit(f"error trying to create merge request url: {url}, code: {response.status_code}")
            return -1

    def get_dev_branch_name(self):
        self.user_session = UserSession()
        return f"branch_{self.user_session.username}"

    def add_all(self, changes: list[str]):
        if len(changes) > 0:
            for change in changes:
                change = change.strip()
                try:
                    self.run_command(['git', 'add', f'{change}', '-f'])
                    self.log_message.emit(f"{change} file added successfully")
                except Exception as e:
                    self.log_message.emit(f"An exception occur trying to add {change} file: {e}")
        else:
            self.log_message.emit(f"Adding all changes to git...")
            try:
                self.run_command(['git', 'add', '.', '-f'])
                self.log_message.emit(f"added all changes successfully")
            except Exception as e:
                self.log_message.emit(f"An exception occur trying to add all changes: {e}")

    def commit(self, comment:str):
        self.log_message.emit(f"Commit all changes...")
        try:
            self.run_command(['git', 'commit', '-m', comment])
            self.log_message.emit(f"All changes Commited successfully")
        except Exception as e:
            self.log_message.emit(f"An exception occur running commit command: {e}")

    def push(self, branch=""):
        self.log_message.emit(f"Setting remote url : {self.git_protocol.repository_url}")
        self.run_command(['git', 'remote', 'set-url', 'origin', self.git_protocol.repository_url])

        if branch == "":
            self.log_message.emit(f"Pushing changes to main branch")
            try:
                self.run_command(['git', 'push', '--force'])
                self.log_message.emit(f"Pushing changes successfully!!!")
            except Exception as e:
                self.log_message.emit(f"Pushing command failed error: {e}")
        else:
            self.log_message.emit(f"Pushing changes to branch: {branch}")
            try:
                self.run_command(['git', 'push', '-u', 'origin', branch])
                self.log_message.emit(f"Pushing from origin to branch Successfully!!")
            except Exception as e:
                self.log_message.emit(f"Pushing changes to branch ({branch} failed, error: {e})")

    def _commit_and_push(self, comment: str, changes: list[str] ,branch =""):
        self.add_all(changes)
        self.commit(comment)
        self.get_latest(False)
        self.push(branch)
        # Check the status of the repository
        self.run_command(['git', 'status'])

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
        result = subprocess.run('git branch --show-current',
                                capture_output=True, text=True,
                                creationflags = subprocess.CREATE_NO_WINDOW )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            self.error_message.emit(f"Error getting current branch: {result.stderr}")
            return None

    def restore_git_repository(self):
        # Reset the working directory to the last commit
        self.run_command(['git', 'reset', '--hard'])

        # Remove all untracked files and directories
        self.run_command(['git', 'clean', '-fd'])

    def _get_merge_request_url(self):
        return f"{self.git_api_url}/projects/{self.project_id}/merge_requests"

    def check_and_add_origin(self, url):
        result = self._run_git_command_get_output(['git', 'remote'])
        remotes = result.splitlines()
        if "origin" in remotes:
            self.log_message.emit(f"Remote 'origin' is already added")
        else:
            self.run_command(['git', 'remote', 'add', 'origin', url])

    def check_working_path(self):
        if not os.path.exists(self.raw_working_path):
            self.raw_working_path = FileManager.get_working_path(
                self.config_manager.get_config()["general"]["repository_prefix"],"default")
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
    def setup(self, send_process_signal=True):
        if send_process_signal:
            self.setup_started.emit()
        self.check_working_path()

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

            """ TODO: Check the first state set up, if it not finished with success code then change protocol """
            # Change directory to the cloned repository
            os.chdir(self.working_path)
            self.check_and_add_origin(self.git_protocol.repository_url)
            # Set or update the remote URL (if needed)
            self.run_command(['git', 'remote', 'set-url', 'origin', self.git_protocol.repository_url])
            # Verify remote repository
            self.run_command(['git', 'ls-remote', '--get-url', 'origin'])
            # Fetch updates from the remote repository
            self.run_command(['git', 'fetch',  'origin'])
            # Send setup signal
            self.log_message.emit(f" Setup Completed ")

            if self.reset_ssh:
                self.reset_ssh = False
                return self.catch_ssh_connection_error()

            changes, modifications = self.get_repository_changes()
            if len(changes) <= 0 and len(modifications) <= 0:
                self.get_latest(False)

            if send_process_signal:
                self.setup_completed.emit(self.repo_exist(), self.raw_working_path)
        except Exception as e:
            self.log_message.emit(f"An error occurred : {e}")

    @Slot(str, list)
    def commit_and_push_changes(self, message: str, changes: list[tuple[str,str]]):
        self.push_and_commit_started.emit()
        self.check_user_session()
        self.log_message.emit("pushing changes...")
        changes_files = [change[0] for change in changes]
        if self.user_session.role_id == RoleID.DEV.value:
            self.arrange_dev_push(message, changes_files)
        else:
            self._commit_and_push(message, changes_files)

        self.get_latest(False)
        self.get_repository_changes()
        self.push_and_commit_completed.emit(message, changes)

    @Slot()
    def load_merge_requests(self, send_end_process_signal=True):
        self.load_mr_started.emit()

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

        if send_end_process_signal:
            self.load_mr_completed.emit()

    @Slot()
    def get_main_branch(self):
        try:
            # Run the git symbolic-ref command to get the main branch name
            result = subprocess.run(
                ['git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'],
                capture_output=True,
                text=True,
                creationflags = subprocess.CREATE_NO_WINDOW
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
            result = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True,
                                    creationflags = subprocess.CREATE_NO_WINDOW)
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
        self.get_mr_commits_started.emit()

        url = f"{self._get_merge_request_url()}/{merge_request_id}/commits"
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            self.send_merge_request_commits.emit(commits)
        else:
            self.error_message.emit(f"Failed to load commits from : {url}")

        self.get_mr_commits_completed.emit()

    @Slot()
    def get_merge_requests_comments(self, merge_request_id: int):
        self.get_mr_comments_started.emit()

        url = f"{self._get_merge_request_url()}/{merge_request_id}/notes"
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            comments = response.json()
            self.send_merge_requests_comments.emit(comments)
        else:
            self.error_message.emit(f"Error handling request to get comments from : {url}")

        self.get_mr_comments_completed.emit()

    @Slot(int)
    def get_merge_request_changes(self, merge_request_id: int):
        self.get_mr_changes_started.emit()

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

        self.get_mr_changes_completed.emit()

    @Slot(str, int)
    def merge_request_add_comment(self, comment: str, merge_request_id: int):
        self.add_comment_started.emit()

        url = f"{self._get_merge_request_url()}/{merge_request_id}/notes"
        headers = {"PRIVATE-TOKEN": self.personal_access_token}
        data = {"body": comment}
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 201:
            self.get_merge_requests_comments(merge_request_id)
            self.log_message.emit("Comment upload correctly")
        else:
            self.error_message.emit(f"Failed to add comment to : {url}")

        self.add_comment_completed.emit()

    @Slot()
    def merge_request_accept_and_merge(self, merge_request_id: int, commit_message: str):
        self.accept_merge_started.emit()
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
            self.load_merge_requests(False)
            self.get_latest(False)
        else:
            self.error_message.emit(f"Failed to accept and merge MR: {response.status_code}, url: {url}")

        self.accept_merge_completed.emit()

    @Slot()
    def verify_user_branch(self):
        self.branching_started.emit()
        self.check_user_session()
        current_branch = self.get_current_branch()
        if self.user_session.role_id == RoleID.DEV.value:
            if current_branch != self.get_dev_branch_name():
                self.create_local_branch(self.get_dev_branch_name(), self._get_main_branch_name())
        else:
            if current_branch != self._get_main_branch_name():
                self.run_command(['git', 'checkout', self._get_main_branch_name()])
        self.branching_completed.emit()

    @Slot()
    def get_repository_history(self):
        output = self._run_git_command_get_output(["git", "log", "--pretty=format:%h - %s (%ci)"])
        if output:
            commits = output.splitlines()
            self.send_repository_history.emit(commits)

    @Slot()
    def get_repository_changes(self) -> tuple[list, list]:
        """
        :return: (modifications, changes)
        a tuple of list where the first element is a list of the
        files with modification and the second list is a list of files with others changes
        each element of the first list is a tuple where the first element is the file path and the second element is
        the differences between the old and the new file
        each element of the second list is a tuple where the first element is the file path and the second element
        is the type of change
        """
        changes_modified = []
        other_changes = []
        self.log_message.emit("Getting Changes in repository...")
        changed_files_out = self._run_git_command_get_output(['git', 'status', '--porcelain'])
        if changed_files_out:
            changed_files = [
                (line[:3].replace(" ", ""), line[3:]) for line in changed_files_out.splitlines() if line]
            for change, changed_file in changed_files:
                changed_file = changed_file.strip('""')
                if change == "M":
                    self.log_message.emit(f"Getting differences in file: {changed_file}")
                    diff = self._run_git_command_get_output(['git', 'diff', changed_file])
                    if diff:
                        changes_modified.append((fr"{changed_file}", diff))
                else:
                    if not change in FILE_CHANGE_DIC:
                        other_changes.append((fr"{changed_file}","Unknown change"))
                    else:
                        other_changes.append((fr"{changed_file}", change))

        self.send_current_changes.emit(changes_modified, other_changes)
        self.log_message.emit("Getting changes in repository finished")
        return changes_modified, other_changes

    @Slot()
    def get_latest(self, send_process_signal=True):
        if send_process_signal:
            self.get_latest_started.emit()

        # restore all the modified files before get latest
        # self.restore_git_repository()

        self.log_message.emit("getting latest...")
        # Change to the repository directory
        os.chdir(self.raw_working_path)

        # Set or update the remote URL (if needed)
        self.run_command(['git', 'remote', 'set-url', 'origin', self.git_protocol.repository_url])

        # Verify remote repository
        self.run_command(['git', 'ls-remote', '--get-url', 'origin'])

        # Fetch changes from the remote repository
        self.run_command(['git', 'fetch', 'origin'])

        # Pull the changes directly
        self.run_command(['git', 'pull' ,'origin', self._get_main_branch_name()])

        # Check the status of the repository
        self.run_command(['git', 'status'])

        if send_process_signal:
            self.get_latest_completed.emit()

    @Slot()
    def on_log_out(self):
        self.attends = 0

    @Slot()
    def reset(self):
        self.reset_started.emit()
        self.restore_git_repository()
        self.reset_completed.emit()

    @Slot()
    def on_refresh(self):
        self.refreshing.emit()
        self.log_message.emit("Refreshing windows")
        modifications, changes = self.get_repository_changes()

        if len(modifications) > 0 or len(changes) > 0:
            GitController.setup(self, False)
        else:
            GitController.setup(self, False)
            self.get_latest(False)

        self.refreshing_completed.emit()
        self.log_message.emit("Refreshing windows completed")