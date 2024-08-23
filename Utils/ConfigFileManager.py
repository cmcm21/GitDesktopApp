from Utils.SingletonMeta import SingletonMeta
from Utils.FileManager import FileManager
import os
import tomli
import tomli_w


class ConfigFileManager(metaclass=SingletonMeta):
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigFileManager, cls).__new__(cls)
            cls._instance.user = None
        return cls._instance

    def get_config(self) -> dict:
        if self._config is None:
            self.load_config()
        return self._config

    def get_value(self, section: str, key: str):
        if section in self._config and key in self._config[section]:
            return self._config[section][key]

    def load_config(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(script_dir, "..\\configFile.toml")
        with open(config_file_path, "rb") as config_file:
            self._config = tomli.load(config_file)

    def add_value(self, section: str, key: str, value: object):
        if self._config is None:
            self.load_config()

        file_path = os.path.join(FileManager.get_local_path(), "configFile.toml")

        self._config[section][key] = value

        with open(file_path, 'wb') as file:
            tomli_w.dump(self._config, file)


