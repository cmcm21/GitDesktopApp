import abc
import subprocess
import requests
import json
import os
from Controller.GitController import GitController
from enum import Enum


class CreateRepDir(Enum):
    ALREADY_EXIST = 1
    DIR_CREATED = 2


class GitProtocolAbstract(metaclass=abc.ABCMeta):
    repository_url = ""
    @classmethod
    def __subclasshook__(cls, subclass):
        """class method used to verify that and inherited class has the abstract class methods implemented"""
        return (
                hasattr(subclass, 'setup') and
                callable(subclass.setup) or
                NotImplemented
        )

    def __init__(self, git_controller: GitController):
        self.git_controller = git_controller

    def create_repository_dir(self) -> CreateRepDir:
        # Check if the repository directory exists check for the directory and the .git file
        if self.git_controller.repo_exist():
            self.git_controller.log_message.emit(f"The directory '{self.git_controller.working_path}' already exists.")
            return CreateRepDir.ALREADY_EXIST
        else:
            self.git_controller.log_message.emit(f"Creating directory : {self.git_controller.working_path} ")
            if not self.git_controller.working_path.exists():
                self.git_controller.working_path.mkdir(parents=True)
                return CreateRepDir.DIR_CREATED

    @abc.abstractmethod
    def setup(self) -> bool:
        """ Set up the communication between local pc and remote repository """
        raise NotImplementedError


class GitProtocolSSH(GitProtocolAbstract):

    def __init__(self, git_controller: GitController):
        super().__init__(git_controller)
        self.repository_url = git_controller.repository_url_ssh

    def setup(self) -> bool:
        if not self.setup_ssh():
            return False

        return_code = self.create_repository_dir()
        if return_code == return_code.ALREADY_EXIST:
            return True

        process = subprocess.Popen(
            ['git', 'clone', self.git_controller.repository_url_ssh, self.git_controller.working_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        stdout, stderr = process.communicate(input="yes\n")
        if stdout:
            self.git_controller.log_message.emit(stdout)
        if stderr:
            return self.git_controller.repo_exist()

        return True

    def setup_ssh(self) -> bool:
        ssh_in_os = False
        if not self.check_ssh_installed():
            ssh_in_os = self.install_openssh()
        else:
            ssh_in_os = True

        if ssh_in_os:
            ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
            private_key_path = os.path.join(ssh_dir, 'id_rsa')
            public_key_path = os.path.join(ssh_dir, 'id_rsa.pub')

            self.generate_ssh_keys(ssh_dir, private_key_path, public_key_path)
            self.add_ssh_key_to_gitlab(self.get_ssh_public_key(public_key_path))
            return True
        else:
            return False

    def check_ssh_installed(self) -> bool:
        try:
            # Attempt to run the ssh command with the version flag
            result = subprocess.run(['ssh', '-V'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.git_controller.log_message.emit("SSH is installed.")
                self.git_controller.log_message.emit(result.stdout or result.stderr)  # ssh -V outputs to stderr
                return True
            else:
                self.git_controller.log_message("SSH is not installed.")
                return False
        except FileNotFoundError:
            self.git_controller.log_message.emit("SSH is not installed.")
            return False
        except Exception as e:
            self.git_controller.log_message.emit(f"An error occurred while checking for SSH: {e}")
            return False

    def install_openssh(self) -> bool:
        try:
            # Install OpenSSH Client
            self.git_controller.log_message.emit("Installing OpenSSH Client...")
            subprocess.run(['powershell', 'Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0'],
                           check=True)
            self.git_controller.log_message.emit("OpenSSH Client installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self.git_controller.log_message.emit(f"Failed to install OpenSSH Client: {e}")
            return False
        except Exception as e:
            self.git_controller.log_message.emit(f"An error occurred: {e}")
            return False

    def generate_ssh_keys(self, ssh_dir, private_key_path, public_key_path):
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
        if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
            self.git_controller.log_message.emit("Generating SSH keys...")
            process = subprocess.Popen(
                ['ssh-keygen', '-t', 'rsa', '-b', '4096', '-C',
                 "RiggingLauncher ssh key", '-f', private_key_path, '-N', ''],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input="n\n")
            self.git_controller.log_message.emit("SSH keys generated.")
        else:
            self.git_controller.log_message.emit("SSH keys already exist.")

    @staticmethod
    def get_ssh_public_key(public_key_path: str):
        with open(public_key_path, 'r') as f:
            return f.read().strip()

    def add_ssh_key_to_gitlab(self, ssh_key: str):
        headers = {
            'PRIVATE-TOKEN': self.git_controller.personal_access_token,
            'Content-Type': 'application/json'
        }
        data = {
            'title': 'Auto-generated SSH Key',
            'key': ssh_key
        }
        response = requests.post(f'{self.git_controller.git_api_url}/user/keys/',
                                 headers=headers,
                                 data=json.dumps(data)
                                 )
        if response.status_code == 201:
            self.git_controller.log_message.emit("SSH key added to GitLab.")
        else:
            self.git_controller.log_message.emit(f"Failed to add SSH key to GitLab: "
                                                 f"{response.status_code} - {response.text}")


class GitProtocolHTTPS(GitProtocolAbstract):
    def __init__(self, git_controller: GitController):
        super().__init__(git_controller)
        self.repository_url = self.git_controller.repository_url_https

    def setup(self) -> bool:
        self.create_repository_dir()
        process = subprocess.Popen(
            ['git', 'clone', self.git_controller.repository_url_ssh, self.git_controller.raw_working_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        stdout, stderr = process.communicate()
        if stdout:
            self.git_controller.log_message.emit(stdout)
        if stderr:
            return self.git_controller.repo_exist()

        return True

