from PySide6.QtCore import Signal, Slot
from Utils import FileManager
from Utils.UserSession import UserSession
from Utils.Environment import RoleID, FILE_CHANGE_DIC
from Controller.GitController import GitController
from Utils.ConfigFileManager import ConfigFileManager
import requests
from pathlib import Path
import os

class AnimatorGitController(GitController):
    config_rep_ssh_key = "repository_url_ssh"
    config_rep_http_key = "repository_url"
    config_rep_id_key = "project_id"
    config_section = "git_anim"

    publishing_anim_rep = Signal()
    publishing_anim_rep_completed = Signal()
    uploading_anim_files = Signal()
    uploading_anim_files_completed = Signal()

    def __init__(self):
        super().__init__()
        self.config()
        self.ssh_setup = False
        self.user_session = None
        self.fresh_new_rep = False

        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)

    def config(self):
        self.config_manager = ConfigFileManager()
        config = self.config_manager.get_config()

        self.source_path = config["general"]["working_path"]
        self.repository_name = config["git_anim"]["repository_name"]
        self.username = config["git_anim"]["username"]
        self.raw_working_path = config["general"]["animator_path"]
        self.working_path = Path(config["general"]["animator_path"])
        self.personal_access_token = config["git"]["personal_access_token"]
        self.repository_url_https = config["git_anim"]["repository_url"]
        self.repository_url_ssh = config["git_anim"]["repository_url_ssh"]
        self.git_api_url = config["git_anim"]["gitlab_api_url"]
        self.git_hosts = config["git_anim"]["git_hosts"]
        self.project_id = config["git_anim"]["project_id"]

    def run_command(self, command: list) -> bool:
        return super().run_command(command)

    def looking_for_project_remote(self) -> dir:
        headers = {"Private-Token": self.personal_access_token}
        response = requests.get(f"{self.git_api_url}/projects?search={self.repository_name}", headers=headers)
        if response.status_code != 200:
            self.error_message.emit(f"Failed to search for project: {response.text}")
            raise Exception(f"Failed to search for project: {response.text}")

        projects = response.json()
        anim_project = None
        for project in projects:
            if project['name'] == self.repository_name:
                anim_project = project

        return anim_project

    def create_remote_repository(self) -> bool:
        headers = {"Private-Token": self.personal_access_token}
        data = {"name": self.repository_name}
        response = requests.post(f"{self.git_api_url}/projects", headers=headers, data=data)
        if response.status_code != 201:
            self.error_message.emit(f"Failed to create project: {response.text}")
            return False

        project_info = response.json()
        self.write_anim_config(project_info)
        return True

    def write_anim_config(self, project_info: dict):
        self.repository_url_ssh = project_info['ssh_url_to_repo']
        self.repository_url_https = project_info['http_url_to_repo']
        self.project_id = project_info['id']

        self.config_manager.add_value(self.config_section, self.config_rep_id_key, str(self.project_id))
        self.config_manager.add_value(self.config_section, self.config_rep_ssh_key, self.repository_url_ssh)
        self.config_manager.add_value(self.config_section, self.config_rep_http_key, self.repository_url_https)

    def compile_files(self, files:list[str]):
        user_session = UserSession()
        if user_session.role_id != RoleID.ADMIN.value:
            self.log_message.emit(f"Not allowed to compile files")

        # compile the files of the origin repository
        self.log_message.emit(f"Compiling python files... in {self.source_path}")
        if len(files) > 0:
            FileManager.copy_files(files, self.source_path, self.raw_working_path, self.log_message)
            FileManager.compile_python_files(self.raw_working_path, files, self.log_message)
        else:
            FileManager.copy_all_files(self.source_path, self.raw_working_path, self.log_message)
            FileManager.compile_all_python_files(self.raw_working_path, self.log_message)

    def get_commit_count(self):
        headers = {"Private-Token": self.personal_access_token}
        commits_url = f"{self.git_api_url}/projects/{self.project_id}/repository/commits"
        # To handle pagination, we need to loop through all pages
        commit_count = 0
        page = 1

        while True:
            response = requests.get(commits_url, headers=headers, params={'per_page': 100, 'page': page})

            if response.status_code != 200:
                raise Exception(f"Failed to retrieve commits: {response.text}")

            commits = response.json()
            # Count the number of commits in the current page
            commit_count += len(commits)
            # Check if we have fetched all commits
            if len(commits) < 100:
                break
            page += 1

        return commit_count

    def _commit_and_push(self, comment: str, changes: list[str] ,branch =""):
        self.add_all(changes)
        self.commit(comment)
        # When the animator repo is pushed we don't want to get latest
        # self.get_latest()
        self.push(branch)
        # Check the status of the repository
        self.run_command(['git', 'status'])

    def upload_files(self, message: str, changes: list[tuple[str, str]]):
        user_session = UserSession()
        if user_session.role_id != RoleID.ADMIN.value:
            self.log_message.emit("Animator user is not allowed to upload files either compile .py -> .pyc")

        self.uploading_anim_files.emit()
        to_delete_files, to_compile_files = self.get_separate_changes(changes)
        changes_files = []

        self.compile_files(to_compile_files)

        FileManager.remove_files_in_path(self.raw_working_path, ".py", self.log_message)
        FileManager.delete_empty_sub_dirs(self.source_path, self.log_message)
        FileManager.delete_empty_sub_dirs(self.raw_working_path, self.log_message)

        if len(changes) > 0:
            FileManager.remove_files(to_delete_files, self.raw_working_path, self.log_message)
            changes_files = [change_file for change_file, change in changes]
        else:
            to_delete_files = FileManager.sync_directories(self.source_path, self.raw_working_path, self.log_message)
            changes += to_delete_files

        self._commit_and_push(message, changes_files)

        self.log_message.emit(f"Repository {self.repository_name} created and pushed successfully.")
        self.uploading_anim_files_completed.emit()

    def check_working_path(self):
        if not os.path.exists(self.raw_working_path):
            self.raw_working_path = FileManager.get_working_path(
                self.config_manager.get_config()["general"]["repository_prefix"],"animator")
            self.config_manager.add_value("general","animator_path", self.raw_working_path)
            self.working_path = Path(self.raw_working_path)
            self.source_path = self.config_manager.get_config()["general"]["working_path"]

    @Slot()
    def get_latest(self, send_process_signal=True):
        if send_process_signal:
            self.get_latest_started.emit()

        # restore all the modified files before get latest
        self.restore_git_repository()

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
    def verify_user_branch(self):
        return

    @Slot(str, list)
    def publish_rep(self, message: str, changes: list[tuple[str,str]]):
        self.publishing_anim_rep.emit()
        if self.setup():
            self.upload_files(message, changes)
        else:
            self.error_message.emit("An error occur while trying to publish repository")
        self.publishing_anim_rep_completed.emit()

    @staticmethod
    def get_separate_changes(changes: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
        deleted_files = [change_file for change_file, change in changes if change == "D"]
        others = [change_file for change_file, change in changes if change != "D"]

        return deleted_files, others

    @Slot()
    def setup(self) -> bool:
        self.check_working_path()
        self.setup_started.emit()
        print(f"class: {self.__class__.__name__} working in path: {self.raw_working_path}")
        setup_success = False

        try:
            anim_project = self.looking_for_project_remote()
            if anim_project is not None:
                self.log_message.emit(f"Remote repository '{self.repository_name}' already exists on GitLab.")
                self.write_anim_config(anim_project)
                self.fresh_new_rep = False
            else:
                self.create_remote_repository()
                self.fresh_new_rep = True

            super().setup()
            setup_success = True
        except Exception as e:
            self.error_message.emit(f"Error trying to create animation repository, error: {e}")
            setup_success = False
        finally:
            self.setup_completed.emit(setup_success, self.raw_working_path)
            return setup_success