from PySide6.QtCore import Signal, Slot
from Utils.FileManager import FileManager
from Utils.UserSession import UserSession
from Utils.Environment import ROLE_ID
from Controller.GitController import GitController
from Controller.GitProtocol.GitProtocols import GitProtocolSSH
from Controller.GitProtocol.GitProtocols import GitProtocolHTTPS
from Exceptions.AppExceptions import GitProtocolException, GitProtocolErrorCode
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
    uploading_anim_files = Signal()
    uploading_anim_files_completed = Signal()

    def __init__(self, config: dict):
        super().__init__(config)
        self.source_path = config["general"]["working_path"]
        self.repository_name = config["git_anim"]["repository_name"]
        self.username = config["git_anim"]["username"]
        self.raw_working_path = FileManager.join_with_os_root_dir(os.path.join(f"{self.repository_name}"
                                                                               ,config["general"]["animator_path"]))
        self.working_path = Path(FileManager.join_with_os_root_dir(os.path.join(f"{self.username}",
                                                                                config["general"]["animator_path"])))
        self.personal_access_token = config["git"]["personal_access_token"]
        self.repository_url_https = config["git_anim"]["repository_url"]
        self.repository_url_ssh = config["git_anim"]["repository_url_ssh"]
        self.git_api_url = config["git_anim"]["gitlab_api_url"]
        self.git_hosts = config["git_anim"]["git_hosts"]
        self.project_id = config["git_anim"]["project_id"]
        self.ssh_setup = False
        self.user_session = None

        # avoid circular import
        from Controller.GitProtocol.GitProtocols import GitProtocolSSH
        self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)

    def _run_git_command(self, command: list) -> bool:
        print(self.working_path)
        return super()._run_git_command(command)

    def check_anim_repository(self, from_setup=False) -> bool:
        # TODO: Refactor this method
        self.creating_anim_rep.emit()

        try:

            anim_project = self.looking_for_project_remote()
            if anim_project is not None:
                self.log_message.emit(f"Remote repository '{self.repository_name}' already exists on GitLab.")
                self.write_anim_config(anim_project)
            else:
                self.create_remote_repository()

            if not from_setup:
                self.git_protocol = GitProtocolSSH(self, self.repository_url_ssh)
                self.git_protocol.setup()
                if not self.git_protocol.check_with_existing_keys():
                    self.git_protocol = GitProtocolHTTPS(self, self.repository_url_https)
                    if not self.git_protocol.setup():
                        raise GitProtocolException("None SSH Nether HTTP Protocols could setup correctly",
                                                   GitProtocolErrorCode.SETUP_FAILED)

            if FileManager.path_exists(self.raw_working_path):
                self.log_message.emit(f"Local repository '{self.repository_name}' already exists.")
            else:
                self.create_local_repository()

            self._run_git_command(["git", "remote", "set-url", "origin", self.git_protocol.repository_url])
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


    def push_local_repository(self):
        self._run_git_command(["git", "remote", "set-url", "origin", self.git_protocol.repository_url])
        self._run_git_command(["git", "add", "."])
        self._run_git_command(["git", "commit", "-m", "Initial commit"])
        self._run_git_command(["git", "push" ])

        self.log_message.emit(f"Repository {self.repository_name} created and pushed successfully.")

    def write_anim_config(self, project_info: dict):
        self.repository_url_ssh = project_info['ssh_url_to_repo']
        self.repository_url_https = project_info['http_url_to_repo']
        self.project_id = project_info['id']

        FileManager.add_value_to_config_file(self.config_section, self.config_rep_id_key, str(self.project_id))
        FileManager.add_value_to_config_file(self.config_section, self.config_rep_ssh_key, self.repository_url_ssh)
        FileManager.add_value_to_config_file(self.config_section, self.config_rep_http_key, self.repository_url_https)

    def compile_origin_files(self):
        user_session = UserSession()
        if user_session.role_id == ROLE_ID.ANIMATOR.value or user_session.role == ROLE_ID.ADMIN_ANIM.value:
            return

        # compile the files of the origin repository
        self.log_message.emit(f"Compiling python files... in {self.source_path}")
        FileManager.compile_python_files(self.source_path, self.log_message)
        # move files to the anim working path
        FileManager.move_all_files_except_extension(
            self.source_path, self.raw_working_path, '.py', self.log_message)

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
        self.check_anim_repository(from_setup=True)
        super().setup()

    @Slot()
    def get_anim_rep_latest(self):
        self.get_latest()

    @Slot(str)
    def publish_rep(self, message: str):
        if self.check_anim_repository():
            self.upload_files(message)
        else:
            self.error_message.emit("An error occur while trying to publish repository")

    @Slot(str)
    def upload_files(self, message: str):
        self.uploading_anim_files.emit()

        user_session = UserSession()
        if user_session.role_id == ROLE_ID.ANIMATOR.value:
            self.log_message.emit("Animator user is not allowed to upload files either compile .py -> .pyc")

        self.compile_origin_files()
        self.push_local_repository()

        self.uploading_anim_files_completed.emit()

    @Slot()
    def verify_user_branch(self):
        return

    @Slot(str)
    def on_setup_working_path(self, path: str):
        real_path = os.path.join(path, self.working_path_prefix, "animator")
        self.raw_working_path = real_path
        self.working_path = Path(real_path)

        FileManager.add_value_to_config_file("general", "animator_path", path)
        self.setup()

