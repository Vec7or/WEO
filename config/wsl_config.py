from configparser import ConfigParser
from io import StringIO
from tempfile import TemporaryFile
from typing import TextIO

from config.config_manager import ConfigManager
from wsl.wsl_api import WslApi


class WslConfig(ConfigManager):
    CONFIG_PATH: str = "/etc/wsl.conf"

    def __init__(self, wsl_api: WslApi, instance_name: str, config_path: str = CONFIG_PATH):
        super().__init__(wsl_api, instance_name, config_path)
        self._config.add_section("boot")
        self._config.set("boot", "systemd", "false")
        self._config.add_section("user")
        self._config.set("user", "default", "user")

    @property
    def systemd(self) -> str:
        return self._config.get("boot", "systemd")

    @systemd.setter
    def systemd(self, value: str):
        if not value in ["false", "true"]:
            raise ValueError("Invalid value for systemd")
        self._config.set("boot", "systemd", value)

    @property
    def user(self) -> str:
        return self._config.get("user", "default")

    @user.setter
    def user(self, value: str):
        self._config.set("user", "default", value)

    def get(self) -> ConfigParser:
        return self._config

    def load(self, config: ConfigParser) -> None:
        self._config = config

    def write(self, file: TextIO) -> None:
        self._config.write(file)
