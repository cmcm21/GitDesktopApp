from PySide6.QtCore import Signal, Slot
from pyparsing import Empty

from Utils.FileManager import FileManager
from Utils.UserSession import UserSession
from Utils.Environment import RoleID, FILE_CHANGE_DIC
from Controller.GitController import GitController
from Utils.ConfigFileManager import ConfigFileManager
import requests
from pathlib import Path
from typing import Callable
import os
import time

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
        self.ssh_setup = False
        self.user_session = None
        self.fresh_new_rep = False

        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)

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
            return lambda: print("No allowed to Compile files")

        # compile the files of the origin repository
        self.log_message.emit(f"Compiling python files... in {self.source_path}")
        if len(files) > 0:
            FileManager.compile_python_files(self.source_path, files, self.log_message)
            # Timer to wait that all files compiled Finished
            time.sleep(2)

            FileManager.move_files(files, self.source_path,'.py', self.raw_working_path, self.log_message)
        else:
            FileManager.compile_python_files_from_source(self.source_path, self.log_message)
            # Timer to wait that all files compiled Finished
            time.sleep(2)
            FileManager.move_all_files_except_extension(self.source_path, self.raw_working_path, '.py', self.log_message)

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

    def upload_files(self, message: str, changes: list[str]):
        user_session = UserSession()
        if user_session.role_id != RoleID.ADMIN.value:
            self.log_message.emit("Animator user is not allowed to upload files either compile .py -> .pyc")

        self.uploading_anim_files.emit()
        self.compile_files(changes)

        FileManager.delete_empty_sub_dirs_with_name(self.source_path, "__pycache__", self.log_message)
        deleted_files = FileManager.sync_directories(self.source_path, self.raw_working_path, self.log_message)
        changes += deleted_files
        self._commit_and_push(message, changes)

        self.log_message.emit(f"Repository {self.repository_name} created and pushed successfully.")
        self.uploading_anim_files_completed.emit()

    def get_changes_from_default_rep(self) -> tuple:
        temp_url = self.raw_working_path
        self.raw_working_path = self.config_manager.get_config()["general"]["working_path"]
        modifies, changes = self.get_repository_changes()
        self.raw_working_path = temp_url

        return modifies, changes

    def check_working_path(self):
        if self.raw_working_path == "":
            self.raw_working_path = FileManager.get_working_path(
                self.config_manager.get_config()["general"]["repository_prefix"],"animator")
            self.config_manager.add_value("general","animator_path", self.raw_working_path)
            self.working_path = Path(self.raw_working_path)
            self.source_path = self.config_manager.get_config()["general"]["working_path"]

    @staticmethod
    def extract_just_file_paths(modifies, changes) -> tuple:
        file_paths = []
        deleted_files = []

        for file, modification in modifies:
            if modification != "D":
                file_paths.append(file)
            else:
                deleted_files.append(file)

        for file, change in changes:
            if change != "D":
                file_paths.append(file)
            else:
                deleted_files.append(file)

        return file_paths, deleted_files

    @Slot(str)
    def on_setup_working_path(self, path: str):
        real_path = os.path.join(path, self.working_path_prefix, "animator")
        self.raw_working_path = real_path
        self.working_path = Path(real_path)

        self.config_manager.add_value("general", "animator_path", real_path)
        self.setup()

    @Slot()
    def verify_user_branch(self):
        return

    @Slot(str, list)
    def publish_rep(self, message: str, changes: list[str]):
        if self.setup():
            self.upload_files(message, changes)
        else:
            self.error_message.emit("An error occur while trying to publish repository")

    @Slot()
    def setup(self) -> bool:
        self.check_working_path()

        print(f"class: {self.__class__.__name__} working in path: {self.raw_working_path}")
        self.publishing_anim_rep.emit()

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
            return True

        except Exception as e:
            self.error_message.emit(f"Error trying to create animation repository, error: {e}")
            return False

        finally:
            self.publishing_anim_rep_completed.emit()