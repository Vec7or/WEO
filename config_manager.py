from wsl_api import WslApi
from configparser import ConfigParser


class ConfigManager:
    def __init__(self, wsl_api: WslApi, config_instance_name: str, config_path: str) -> None:
        self._wsl_api = wsl_api
        self._config_path = config_path
        self._config_instance_name = config_instance_name

    def read_config(self) -> ConfigParser:
        config = self._wsl_api.run_command_in_instance(self._config_instance_name, 'cat ' + self._config_path)
        parser = ConfigParser()
        parser.read_string(config)
        return parser
