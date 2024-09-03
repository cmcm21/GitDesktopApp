from Controller.GitController import GitController
from Utils.UserSession import UserSession
from Utils.Environment import CreateDir
import abc
import subprocess
import requests
import json
import os
import paramiko
import base64
import hashlib
import stat


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
        return_code = self.git_controller.run_command(
            ['git', 'clone', self.repository_url, self.git_controller.raw_working_path])

        if not return_code:
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

        ssh_dir = os.path.join(os.path.expanduser("~"), ".ssh")
        user_session = UserSession()
        private_key_path = os.path.join(ssh_dir, f'id_rsa_puppet_launcher_{user_session.username}')
        public_key_path = os.path.join(ssh_dir, f'id_rsa_puppet_launcher_{user_session.username}.pub')
        known_hosts = os.path.join(ssh_dir, "known_hosts")

        if not os.path.exists(public_key_path):
            self.generate_ssh_keys(ssh_dir, private_key_path, public_key_path)

        public_key = self.get_ssh_public_key(public_key_path)

        if not self.is_key_in_known_hosts(public_key, known_hosts):
            self.add_host_key(known_hosts, public_key)

        if not self.check_ssh_key_exists_remote(public_key):
            self.add_ssh_key_to_gitlab(public_key)

        if self.test_ssh_connection(private_key_path):
            self.set_env_ssh_key_var(private_key_path)
            self.add_private_key_to_agent(private_key_path)
            return True
        else:
            return False

    def check_ssh_installed(self) -> bool:
        try:
            # Attempt to run the ssh command with the version flag
            result = subprocess.run(['ssh', '-V'], capture_output=True, text=True)
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
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
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

    def test_ssh_connection(self, private_key_path):
        try:
            key = paramiko.RSAKey(filename=private_key_path)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname='gitlab.com', username='git', pkey=key)
            # Close the client after successful connection
            client.close()
            self.git_controller.log_message.emit(f"Connection successful using key: {private_key_path}")
            return True
        except Exception as e:
            self.git_controller.error_message.emit(f"Failed to connect using key {private_key_path}: {e}")
            return False

    def add_private_key_to_agent(self, private_key_path: str):
        result = subprocess.run(["ssh-add" , private_key_path])
        self.git_controller.log_message.emit(result.stdout)
        if result.stderr:
            self.git_controller.error_message.emit(result.stderr)

    def start_ssh_agent(self) -> bool:
        # Start ssh-agent and set environment variables
        result = subprocess.run(["ssh-agent", "-s"], capture_output=True, text=True)
        if result.returncode == 0:
            # Extract and set environment variables
            for line in result.stdout.splitlines():
                if line.startswith("SSH_AUTH_SOCK"):
                    # Normally you would set these environment variables here
                    # Example: os.environ["SSH_AUTH_SOCK"] = line.split("=")[1]
                    print(line)
                elif line.startswith("SSH_AGENT_PID"):
                    # Example: os.environ["SSH_AGENT_PID"] = line.split("=")[1]
                    print(line)
            return True
        else:
            self.git_controller.log_message.emit(f"Failed to start ssh-agent: {result.stderr}")
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
        response = requests.post(
            f'{self.git_controller.git_api_url}/user/keys/', headers=headers, data=json.dumps(data) )

        if response.status_code == 201:
            self.git_controller.log_message.emit("SSH key added to GitLab.")
        else:
            self.git_controller.log_message.emit(f"Failed to add SSH key to GitLab: "
                                                 f"{response.status_code} - {response.text}")

    def add_host_key(self, known_hosts_path, public_key):
        host = 'gitlab.com'

        try:
            entry = f"{host} {public_key}\n"
            # Append the host key to known_hosts
            with open(known_hosts_path, 'a') as f:
                f.write(entry)
            self.git_controller.log_message.emit(f"public key for {host} added to known_hosts.")

        except Exception as e:
            self.git_controller.log_message.emit(f"Failed to fetch host key for {host}, error:{e}")

    def is_key_in_known_hosts(self, key_to_check, known_hosts_file):
        # Calculate the fingerprint of the key to check
        fingerprint_to_check = self.calculate_fingerprint(key_to_check)

        # Create file if this doesn't exist
        if not os.path.isfile(known_hosts_file):
            with open(known_hosts_file, 'w') as file:
                pass

            os.chmod(known_hosts_file, stat.S_IRUSR | stat.S_IWUSR |  # Owner permissions: read, write
                     stat.S_IRGRP | stat.S_IWGRP |  # Group permissions: read, write
                     stat.S_IROTH | stat.S_IWOTH)

        with open(known_hosts_file, 'r') as file:
            for line in file:
                # Ignore commented or empty lines
                if line.strip() and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 3:
                        # Extract the key part from the known_hosts file entry
                        known_host_key = parts[2]

                        # Calculate the fingerprint of the key from known_hosts
                        known_host_fingerprint = self.calculate_fingerprint(" ".join(parts[1:3]))
                        # Compare fingerprints
                        if fingerprint_to_check == known_host_fingerprint:
                            self.git_controller.log_message.emit("key is in known_hosts")
                            return True

        self.git_controller.log_message.emit("key wasn't found in known_hosts")
        return False

    def check_with_existing_keys(self) -> bool:
        # Check for existing SSH keys
        existing_keys = self.check_ssh_keys()
        for key in existing_keys:
            if self.test_ssh_connection(key):
                self.set_env_ssh_key_var(key)
                return True
        return False

    @staticmethod
    def calculate_fingerprint(ssh_key):
        # Remove any trailing information like "user@hostname"
        key_body = ssh_key.strip().split()[1]

        # Decode the base64 key to get the raw bytes
        key_bytes = base64.b64decode(key_body)

        # Hash the key using SHA-256 and return the hex digest
        return hashlib.sha256(key_bytes).hexdigest()

    def get_ssh_keys_response(self):
        headers = {
            'PRIVATE-TOKEN': self.git_controller.personal_access_token
        }
        response = requests.get(
            f'{self.git_controller.git_api_url}/users/{self.git_controller.username}/keys', headers=headers)

        response.raise_for_status()
        return response.json()

    def is_key_present(self, json_response, fingerprint_to_check):
        for json_obj in json_response:
            key = json_obj['key'].split()
            if len(key) > 1:
                fingerprint = self.calculate_fingerprint(" ".join(key[0:2]))
                if fingerprint == fingerprint_to_check:
                    self.git_controller.log_message.emit("SSH Key is already added to gitlab remote account")
                    return True

        self.git_controller.log_message.emit("SSH Key is not added to gitlab remote account")
        return False

    def check_ssh_key_exists_remote(self,  ssh_public_key) -> bool:
        try:
            json_response = self.get_ssh_keys_response()
            fingerprint_to_check = self.calculate_fingerprint(ssh_public_key)
            if self.is_key_present(json_response, fingerprint_to_check):
                self.git_controller.log_message.emit("SSH key is already added.")
                return True
            else:
                self.git_controller.log_message.emit("SSH key is not added.")
                return False
        except requests.exceptions.HTTPError as err:
            self.git_controller.log_message.emit(f"HTTP error occurred: {err}")
            return False
        except Exception as err:
            print(f"An error occur while trying to check ssh key: {err}")
            self.git_controller.log_message.emit(f"An error occurred: {err}")
            return False

    @staticmethod
    def set_env_ssh_key_var(private_key_path):
        raw_key_path = fr"{private_key_path}"
        os.environ['GIT_SSH_COMMAND'] = f'ssh -i "{raw_key_path}"'

    # Step 2: Use ssh-keygen to remove the offending host key
    def remove_offending_host_key(self):
        known_hosts_file = os.path.expanduser('~/.ssh/known_hosts')
        host = "gitlab.com"
        try:
            # Run ssh-keygen to remove the offending key
            result = subprocess.run(['ssh-keygen', '-R', host], capture_output=True, text=True)
            if result.returncode == 0:
                self.git_controller.log_message.emit(f"Successfully removed host key for {host} from {known_hosts_file}.")
            else:
                self.git_controller.log_message.emit(f"Failed to remove host key: {result.stderr}")
        except Exception as e:
            self.git_controller.error_message.emit(f"Error: {e}")

    # Step 3: Reconnect to the server to accept the new host key
    def reconnect_to_host(self):
        host = "gitlab.com"
        known_hosts_file = os.path.expanduser('~/.ssh/known_hosts')

        try:
            # Define the SSH command and arguments, we set the options -o StrictHostKeyChecking=no and BatchMode=yes
            # so the command no waits for the user's input
            command = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes', '-v', 'git@gitlab.com']
            self.git_controller.log_message.emit(f"Executing command: {command}")

            # Start the subprocess
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Send input ("yes\n") to the process to accept the host key
            stdout, stderr = process.communicate("yes\n")

            self.git_controller.log_message.emit(f"Command: {command} execution finished")
            # Print the output and errors
            self.git_controller.log_message.emit(stdout)

            if stderr:
                self.git_controller.error_message.emit(stdout)

            # Check the exit status
            exit_code = process.returncode
            self.git_controller.log_message(f"Exit Code: {exit_code}")

            # Check for errors in the stderr
            if exit_code != 0:
                self.git_controller.error_message(f"An error occurred: {stderr}")

            self.git_controller.log_message.emit(f"New host key for gitlab.com added to {known_hosts_file} -> {stdout}")

        except Exception as e:
            self.git_controller.error_message.emit(f"Error: {e}")


class GitProtocolHTTPS(GitProtocolAbstract):
    def __init__(self, git_controller: GitController, url_https: str):
        super().__init__(git_controller)
        self.repository_url = url_https

    def setup(self) -> bool:
        result = self.git_controller.create_repository_dir()
        if result == CreateDir.ALREADY_EXIST:
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
