import os
from configparser import ConfigParser
from tempfile import TemporaryDirectory

from exceptions.ConfigNotFoundError import ConfigNotFoundError
from wsl.wsl_api import WslApi


class ConfigManager:
    def __init__(self, wsl_api: WslApi, instance_name: str, config_path: str):
        self._wsl_api = wsl_api
        self._instance_name = instance_name
        self._config_path = config_path
        self._config = ConfigParser()

    def read_config(self) -> None:
        self._config = ConfigParser()
        with TemporaryDirectory() as temp_dir:
            temp_config_file_path = os.path.join(temp_dir, "config.conf")
            if not self._wsl_api.file_exists_in_instance(self._instance_name, self._config_path):
                raise ConfigNotFoundError()
            self._wsl_api.run_command_in_instance(
                self._instance_name,
                f"cp {self._config_path} {WslApi.linuxify(temp_config_file_path)}"
            )
            self._config.read(temp_config_file_path)

    def write_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_config_file_path = os.path.join(temp_dir, "config.conf")
            with open(temp_config_file_path, "x", encoding="utf-8") as file:
                self._config.write(file, space_around_delimiters=False)
            self._wsl_api.run_command_in_instance(
                self._instance_name,
                f"cp {WslApi.linuxify(temp_config_file_path)} {self._config_path}"
            )
            self._wsl_api.run_command_in_instance(
                self._instance_name,
                f"chmod 644 {self._config_path} && dos2unix {self._config_path}"
            )
