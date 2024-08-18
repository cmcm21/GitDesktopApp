import abc
import subprocess
import requests
import json
import os
import paramiko
from past.builtins import raw_input

from Controller.GitController import GitController
from Utils.UserSession import UserSession
from Utils.Environment import CREATE_DIR
from enum import Enum


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

    @abc.abstractmethod
    def setup(self) -> bool:
        """ Set up the communication between local pc and remote repository """
        raise NotImplementedError


class GitProtocolSSH(GitProtocolAbstract):

    def __init__(self, git_controller: GitController, ssh_url):
        super().__init__(git_controller)
        self.repository_url = ssh_url

    def setup(self) -> bool:
        if not self.setup_ssh():
            return False

        return_code = self.git_controller.create_repository_dir()
        if return_code == return_code.ALREADY_EXIST:
            return True

        self.git_controller.log_message.emit(f"Running git clone command...")
        process = subprocess.Popen(
            ['git', 'clone', self.repository_url, self.git_controller.raw_working_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input="yes\n")
        if stdout:
            self.git_controller.log_message.emit(stdout)
        if stderr:
            self.git_controller.error_message.emit(stderr)
            return self.git_controller.repo_exist()

        return True

    def setup_ssh(self) -> bool:
        ssh_in_os = False
        if not self.check_ssh_installed():
            ssh_in_os = self.install_openssh()
        else:
            ssh_in_os = True

        if not ssh_in_os:
            self.git_controller.error_message.emit("SSH couldn't be installed in the system")
            return False

        if not self.check_with_existing_keys():
            user_session = UserSession()
            ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
            private_key_path = os.path.join(ssh_dir, f'id_rsa_puppet_launcher_{user_session.username}')
            public_key_path = os.path.join(ssh_dir, f'id_rsa_puppet_launcher_{user_session.username}.pub')

            self.generate_ssh_keys(ssh_dir, private_key_path, public_key_path)
            ssh_public_key = self.get_ssh_public_key(public_key_path)
            self.add_ssh_key_to_gitlab(ssh_public_key)
            self.add_host_key(ssh_dir)
            self.set_env_ssh_key_var(ssh_public_key)
            return self.test_ssh_connection(private_key_path, self.repository_url)
        else:
            return True

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
                 "PuppetLauncher ssh key", '-f', private_key_path, '-N', ''],
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
    def check_ssh_keys():
        ssh_dir = os.path.expanduser('~/.ssh')
        existing_keys = []
        if os.path.exists(ssh_dir):
            for file in os.listdir(ssh_dir):
                if file.endswith('.pub'):
                    existing_keys.append(os.path.join(ssh_dir, file[:-4]))  # strip the .pub extension
        return existing_keys

    @staticmethod
    def get_ssh_public_key(public_key_path: str):
        public_key = ""
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()

        return public_key

    def test_ssh_connection(self, key_path, git_url):
        try:
            key = paramiko.RSAKey(filename=key_path)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname='gitlab.com', username='git', pkey=key)
            # Close the client after successful connection
            client.close()
            self.git_controller.log_message.emit(f"Connection successful using new key: {key_path}")
            return True
        except Exception as e:
            self.git_controller.error_message.emit(f"Failed to connect using key {key_path}: {e}")
            return False

    def add_ssh_key_to_gitlab(self, ssh_key: str):
        user_session = UserSession()
        headers = {
            'PRIVATE-TOKEN': self.git_controller.personal_access_token,
            'Content-Type': 'application/json'
        }
        data = {
            'title': f'Puppet Launcher SSH Key {user_session.username}',
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

    def add_host_key(self, ssh_dir):
        host = 'gitlab.com'
        known_hosts_path = os.path.join(ssh_dir, 'known_hosts')

        # Use ssh-keyscan to fetch the host key
        result = subprocess.run(['ssh-keyscan', host], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            # Ensure the .ssh directory exists
            if not os.path.exists(ssh_dir):
                os.makedirs(ssh_dir)
            # Append the host key to known_hosts
            with open(known_hosts_path, 'a') as f:
                f.write(result.stdout)
            self.git_controller.log_message.emit(f"Host key for {host} added to known_hosts.")
        else:
            self.git_controller.log_message.emit(f"Failed to fetch host key for {host}: {result.stderr}")

    def check_with_existing_keys(self) -> bool:
        # Check for existing SSH keys
        existing_keys = self.check_ssh_keys()
        for key in existing_keys:
            print(key)
            if self.test_ssh_connection(key, self.repository_url):
                self.git_controller.log_message.emit(f"Connection successful using existing key: {key}")
                self.set_env_ssh_key_var(key)
                return True
            else:
                print(f"Connection with git repository: {self.repository_url} failed using key: {key}")
        return False

    @staticmethod
    def set_env_ssh_key_var(key_path):
        raw_key_path = fr"{key_path}"
        os.environ['GIT_SSH_COMMAND'] = f'ssh -i "{raw_key_path}"'


class GitProtocolHTTPS(GitProtocolAbstract):
    def __init__(self, git_controller: GitController, url_https: str):
        super().__init__(git_controller)
        self.repository_url = url_https

    def setup(self) -> bool:
        result = self.git_controller.create_repository_dir()
        if result == CREATE_DIR.ALREADY_EXIST:
            return True

        process = subprocess.Popen(
            ['git', 'clone', self.repository_url, self.git_controller.raw_working_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate()
        if stdout:
            self.git_controller.log_message.emit(stdout)
        if stderr:
            return self.git_controller.repo_exist()

        return True
