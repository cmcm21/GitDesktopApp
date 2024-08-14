from PySide6.QtCore import Signal, Slot
from Utils.FileManager import FileManager
from Utils.UserSession import UserSession
from Utils.Environment import ROLE_ID
from Controller.GitController import GitController
from Controller.GitProtocol.GitProtocols import GitProtocolSSH
from Controller.GitProtocol.GitProtocols import GitProtocolHTTPS
from Controller.SystemController import SystemController
import requests
from pathlib import Path
import os
import shutil
import subprocess


class AnimatorGitController(GitController):
    config_rep_ssh_key = "repository_url_ssh"
    config_rep_http_key = "repository_url"
    config_rep_id_key = "project_id"
    config_section = "git_anim"
    creating_anim_rep = Signal()
    anim_rep_creation_completed = Signal()

    def __init__(self, config: dict):
        super().__init__(config)
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
        self.user_session = None

        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)

    def _run_git_command(self, command: list) -> bool:
        print(self.working_path)
        return super()._run_git_command(command)

    def create_anim_repository(self) -> bool:
        # TODO: Refactor this method
        self.creating_anim_rep.emit()
        remote_rep_created = False

        try:
            anim_project = self.looking_for_project_remote()
            if anim_project is not None:
                self.log_message.emit(f"Remote repository '{self.repository_name}' already exists on GitLab.")
                self.write_anim_config(anim_project)
            else:
                remote_rep_created = self.create_remote_repository()

            if FileManager.path_exists(self.raw_working_path):
                self.log_message.emit(f"Local repository '{self.repository_name}' already exists.")

                if FileManager.get_dir_files_count(self.raw_working_path) <= 1:
                    self.compile_origin_files()
            else:
                self.create_local_repository()

            if remote_rep_created:
                self.push_local_repository()
            else:
                self._run_git_command(["git", "remote", "set-url", "origin", self.git_protocol.repository_url])

            user_session = UserSession()

            if self.get_commit_count() <= 1 and user_session.role_id != ROLE_ID.ANIMATOR.value:
                self.upload_files("Upload .pyc files for first time")

            return True
        except Exception as e:
            self.error_message.emit(f"Error trying to create animation repository, error: {e}")
            return False
        finally:
            self.anim_rep_creation_completed.emit()

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

    def create_local_repository(self):
        self.create_repository_dir()
        self._run_git_command(["git", "init", "."])

        self.compile_origin_files()

    def push_local_repository(self):
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)
        if not self.git_protocol.check_with_existing_keys():
            self.git_protocol = GitProtocolHTTPS(self, self.repository_url_https)

        self._run_git_command(["git", "remote", "add", "origin", self.git_protocol.repository_url])
        self._run_git_command(["git", "add", "."])
        self._run_git_command(["git", "commit", "-m", "Initial commit"])
        self._run_git_command(["git", "push", "-u", "origin", "master"])

        self.log_message.emit(f"Repository {self.repository_name} created and pushed successfully.")

    def write_anim_config(self, project_info: dict):
        self.repository_url_ssh = project_info['ssh_url_to_repo']
        self.repository_url_https = project_info['http_url_to_repo']
        self.project_id = project_info['id']

        FileManager.add_value_to_config_file(self.config_section, self.config_rep_id_key, str(self.project_id))
        FileManager.add_value_to_config_file(self.config_section, self.config_rep_ssh_key, self.repository_url_ssh)
        FileManager.add_value_to_config_file(self.config_section, self.config_rep_http_key, self.repository_url_https)

    def get_cache_path(self):
        return os.path.join(self.raw_working_path, "__pycache__")

    def compile_origin_files(self):
        # compile the files of the origin repository
        self.log_message.emit(f"Compiling python files... in {self.source_path}")
        SystemController.compile_python_files(self.source_path)
        # move files to the anim working path
        source_dir = os.path.join(self.source_path, "__pycache__")
        self.log_message.emit(f"Moving .pyc files from {source_dir} to {self.get_cache_path()}")
        FileManager.move_dir(source_dir, self.raw_working_path)

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

    @Slot()
    def setup(self):
        print(f"class: {self.__class__.__name__} working in path: {self.raw_working_path}")
        self.create_anim_repository()
        super().setup()

    @Slot()
    def verify_user_branch(self):
        super().verify_user_branch()

    @Slot()
    def on_git_setup_completed(self):
        self.create_anim_repository()

    @Slot()
    def get_anim_rep_latest(self):
        self.get_latest()

    @Slot(str)
    def upload_files(self, message: str):
        user_session = UserSession()
        if user_session.role_id == ROLE_ID.ANIMATOR.value:
            self.log_message.emit("Animator user is not allowed to upload files either compile .py -> .pyc")
            return

        self.compile_origin_files()

        if FileManager.ensure_all_files_extension(self.get_cache_path(), ".pyc"):
            self._commit_and_push_everything(message, self._get_main_branch_name())
        else:
            self.error_message.emit("There was an error trying to compile all the files")


