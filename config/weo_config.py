from typing import TextIO

from semver import Version

from config.config_manager import ConfigManager
from wsl.wsl_api import WslApi


class WeoConfig(ConfigManager):
    CONFIG_PATH: str = "/etc/weo.conf"

    def __init__(self, wsl_api: WslApi, instance_name: str, config_path: str = CONFIG_PATH):
        super().__init__(wsl_api, instance_name, config_path)
        self._config.add_section("general")
        self._config.set("general", "version", "0.0.0")
        self._config.set("general", "base_image", "none")
        self._config.set("general", "base_image_local", "true")

    @property
    def version(self) -> str:
        return self._config.get("general", "version")

    @version.setter
    def version(self, value: str):
        if not Version.is_valid(value):
            raise ValueError("Invalid value for version")
        self._config.set("general", "version", value)

    @property
    def base_image(self) -> str:
        return self._config.get("general", "base_image")

    @base_image.setter
    def base_image(self, value: str):
        self._config.set("general", "base_image", value)

    @property
    def base_image_local(self) -> str:
        return self._config.get("general", "base_image_local")

    @base_image_local.setter
    def base_image_local(self, value: str):
        if not value in ["true", "false"]:
            raise ValueError("Invalid value for base_image_local")
        self._config.set("general", "base_image_local", value)
