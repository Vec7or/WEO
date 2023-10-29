import os.path
from tempfile import TemporaryDirectory

import click
from colorama import Fore, Style

import requests
from semver import Version
from tqdm import tqdm
from enum import Enum

from config.version import WEO_VERSION
from config.weo_config import WeoConfig
from config.wsl_config import WslConfig
from exceptions.OrchestratorIncompatibleError import OrchestratorIncompatibleError
from exceptions.OrchestratorNotInitialzedError import OrchestratorNotInitializedError
from orchestrator.orchestrator import Orchestrator
from wsl.wsl_api import WslApi


class OrchestratorFactoryStatus(Enum):
    UNKNOWN = 0
    OK = 1
    NO_ORCHESTRATOR = 2
    INCOMPATIBLE_ORCHESTRATOR = 3


class OrchestratorFactory:
    _orchestrator_instance_name = "weo_orchestrator"

    def __init__(self):
        self._status = OrchestratorFactoryStatus.UNKNOWN
        wsl_storage_dir = os.path.expanduser('~') + "\\wsl"
        self._wsl_api = WslApi(wsl_storage_dir)
        self._orchestrator_wsl_config = WslConfig(self._wsl_api, self._orchestrator_instance_name)
        self._orchestrator_weo_config = WeoConfig(self._wsl_api, self._orchestrator_instance_name)
        self._orchestrator = Orchestrator(self._orchestrator_instance_name, self._wsl_api)
        if not self._orchestrator_instance_exists():
            self._status = OrchestratorFactoryStatus.NO_ORCHESTRATOR
        elif not self._orchestrator_instance_compatible():
            self._status = OrchestratorFactoryStatus.INCOMPATIBLE_ORCHESTRATOR
        else:
            self._status = OrchestratorFactoryStatus.OK

    def _orchestrator_instance_exists(self) -> bool:
        return self._wsl_api.instance_exists(self._orchestrator_instance_name)

    def _orchestrator_instance_compatible(self) -> bool:
        self._orchestrator_weo_config.read_config()
        return Version.is_compatible(
            Version.parse(WEO_VERSION), Version.parse(self._orchestrator_weo_config.version))

    def _create_orchestrator_instance(self) -> None:
        alpine_version = "3.20.3"
        alpine_download_url = \
            "https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.3-x86_64.tar.gz"
        alpine_image_file_name = "alpine-minirootfs.tar.gz"
        click.echo(f"{Fore.LIGHTBLUE_EX}Downloading alpine {alpine_version} for orchestrator...{Style.RESET_ALL}")

        with TemporaryDirectory() as temp_dir:
            alpine_image_file_path = os.path.join(temp_dir, alpine_image_file_name)
            try:
                with requests.get(alpine_download_url, stream=True, timeout=10) as response:
                    self._tqdm_download(alpine_image_file_name, alpine_image_file_path, response)
            except requests.exceptions.Timeout as e:
                click.echo(
                    f"{Fore.RED}Alpine could not be downloaded. Timeout{Style.RESET_ALL}")
                raise e

            click.echo(f"{Fore.LIGHTBLUE_EX}Creating orchestrator instance...{Style.RESET_ALL}")
            self._wsl_api.create_instance(
                self._orchestrator_instance_name,
                alpine_image_file_path)

    def _config_orchestrator_instance(self) -> None:
        self._orchestrator_wsl_config.user = "root"
        self._orchestrator_wsl_config.systemd = "false"
        self._orchestrator_weo_config.base_image_local = "false"
        self._orchestrator_weo_config.base_image = "None"
        self._orchestrator_weo_config.version = WEO_VERSION

        self._orchestrator_wsl_config.write_config()
        self._orchestrator_weo_config.write_config()

        self._wsl_api.run_command_in_instance(
            self._orchestrator_instance_name,
            "apk add docker")

    def _tqdm_download(self, file_name, ms_download_file_path_temp, response):
        with tqdm.wrapattr(open(ms_download_file_path_temp, "wb"), "write",
                           colour="green",
                           miniters=1,
                           desc=file_name,
                           total=int(response.headers.get('content-length', 0))) as file_out:
            for chunk in response.iter_content(chunk_size=4096):
                file_out.write(chunk)

    @property
    def status(self) -> OrchestratorFactoryStatus:
        return self._status

    def initialize(self, overwrite: bool = False) -> None:
        if self._status == OrchestratorFactoryStatus.OK:
            return

        if self._status == OrchestratorFactoryStatus.INCOMPATIBLE_ORCHESTRATOR:
            if not overwrite:
                raise OrchestratorIncompatibleError()
            self._wsl_api.remove_instance(self._orchestrator_instance_name)

        try:
            self._create_orchestrator_instance()
            self._config_orchestrator_instance()
            self._status = OrchestratorFactoryStatus.OK
        except Exception as e:
            if self._orchestrator_instance_exists():
                self._wsl_api.remove_instance(self._orchestrator_instance_name)
            raise e

    def create_orchestrator(self) -> Orchestrator:
        if self._status == OrchestratorFactoryStatus.OK:
            return self._orchestrator
        elif self._status == OrchestratorFactoryStatus.NO_ORCHESTRATOR:
            raise OrchestratorNotInitializedError()
        elif self._status == OrchestratorFactoryStatus.INCOMPATIBLE_ORCHESTRATOR:
            raise OrchestratorIncompatibleError()
        else:
            raise RuntimeError("Unknown orchestrator factory error")


if __name__ == '__main__':
    factory = OrchestratorFactory("../")
    factory.create_orchestrator()
