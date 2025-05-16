import os.path
from tempfile import TemporaryDirectory

import click

import requests
from semver import Version
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
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

    def __init__(self, verbose: bool):
        self._status = OrchestratorFactoryStatus.UNKNOWN
        wsl_storage_dir = os.path.expanduser('~') + "\\wsl"
        self._wsl_api = WslApi(wsl_storage_dir, verbose)
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
        click.secho(f"Downloading alpine {alpine_version} for orchestrator...", fg="blue")

        with TemporaryDirectory() as temp_dir:
            alpine_image_file_path = os.path.join(temp_dir, alpine_image_file_name)
            try:
                with requests.get(alpine_download_url, stream=True, timeout=10) as response:
                    self._file_download(alpine_image_file_name, alpine_image_file_path, response)
            except requests.exceptions.Timeout as e:
                click.secho(f"Alpine could not be downloaded. Timeout", fg="red")
                raise e

            click.secho(f"Creating orchestrator instance...", fg="blue")
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

    def _file_download(self, file_name, ms_download_file_path_temp, response):
        progress = Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )
        with progress:
            task_id: TaskID = progress.add_task(
                "[cyan]Downloading...",
                filename=file_name,
                start=False
            )
            # This will break if the response doesn't contain content length
            progress.update(task_id, total=int(response.headers.get('content-length', 0)))
            with open(ms_download_file_path_temp, "wb") as dest_file:
                progress.start_task(task_id)
                for data in response.iter_content(chunk_size=4096):
                    dest_file.write(data)
                    progress.update(task_id, advance=len(data))

            progress.update(task_id, advance=0)

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
