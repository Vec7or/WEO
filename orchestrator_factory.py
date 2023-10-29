import os.path
import shutil
import time
import zipfile
from os import close

import requests
from tqdm import tqdm

from logger import Logger
from orchestrator import Orchestrator
from wsl_api import WslApi


class OrchestratorConfig:
    pass;


class OrchestratorFactory:
    _staging_dir = os.path.dirname(os.path.realpath(__file__)) + "\\staging"
    _script_dir = os.path.dirname(os.path.realpath(__file__)) + "\\scripts"
    _ms_download_file = "ubuntu_22-04.zip"
    _ubuntu_template_file = "ubuntu_22-04.tar.gz"
    _orchestrator_template_file = "weo.tar.gz"
    _weo_template_file = "weo_ubuntu.tar"

    def __init__(self):
        wsl_storage_dir = os.path.expanduser('~') + "\\wsl"
        self._wsl_api = WslApi(wsl_storage_dir)

    @staticmethod
    def _staging_path(file: str) -> str:
        return OrchestratorFactory._staging_dir + "\\" + file

    @staticmethod
    def _weo_template_file_exists() -> bool:
        return os.path.exists(OrchestratorFactory._staging_path(OrchestratorFactory._weo_template_file))

    @staticmethod
    def _download_file_exists() -> bool:
        return os.path.exists(OrchestratorFactory._staging_path(OrchestratorFactory._ms_download_file))

    @staticmethod
    def _ubuntu_template_file_exists() -> bool:
        return os.path.exists(OrchestratorFactory._staging_path(OrchestratorFactory._ubuntu_template_file))

    @staticmethod
    def _orchestrator_template_file_exists() -> bool:
        return os.path.exists(OrchestratorFactory._staging_path(OrchestratorFactory._orchestrator_template_file))

    @staticmethod
    def _download_ubuntu() -> None:
        if not OrchestratorFactory._download_file_exists():
            Logger.info("Downloading ubuntu template from microsoft...")
            ms_download_url = "https://aka.ms/wslubuntu2204"
            ms_download_file_path = OrchestratorFactory._staging_path(OrchestratorFactory._ms_download_file)
            ms_download_file_path_temp = ms_download_file_path + ".tmp"
            if not os.path.exists(OrchestratorFactory._staging_dir):
                os.mkdir(OrchestratorFactory._staging_dir)
            if os.path.exists(ms_download_file_path_temp):
                os.remove(ms_download_file_path_temp)
            try:
                with requests.get(ms_download_url, stream=True, timeout=10) as response:
                    OrchestratorFactory._tqdm_download(ms_download_file_path_temp, response)
            except requests.exceptions.Timeout as e:
                Logger.err("Image could not be downloaded. Timeout")
                raise e

            os.rename(ms_download_file_path_temp, ms_download_file_path)

    @staticmethod
    def _tqdm_download(ms_download_file_path_temp, response):
        with tqdm.wrapattr(open(ms_download_file_path_temp, "wb"), "write",
                           colour="green",
                           miniters=1,
                           desc=OrchestratorFactory._ms_download_file,
                           total=int(response.headers.get('content-length', 0))) as file_out:
            for chunk in response.iter_content(chunk_size=4096):
                file_out.write(chunk)

    @staticmethod
    def _extract_ubuntu() -> None:
        if not OrchestratorFactory._ubuntu_template_file_exists():
            Logger.info("Extracting ubuntu template...")
            ms_download_extracted_folder = "ubuntu_22-04"
            ms_download_extracted_folder_inner = "ubuntu_22-04-install"
            ms_download_install_source_file = "Ubuntu_2204.1.7.0_x64.appx"
            ms_download_install_file = "install.tar.gz"
            if os.path.exists(OrchestratorFactory._staging_path(ms_download_extracted_folder)):
                os.remove(OrchestratorFactory._staging_path(ms_download_extracted_folder))
            if os.path.exists(OrchestratorFactory._staging_path(ms_download_extracted_folder_inner)):
                os.remove(OrchestratorFactory._staging_path(ms_download_extracted_folder_inner))

            with zipfile.ZipFile(OrchestratorFactory._staging_path(OrchestratorFactory._ms_download_file),
                                 'r') as ms_zip:
                ms_zip.extractall(OrchestratorFactory._staging_path(ms_download_extracted_folder))

            with zipfile.ZipFile(
                    OrchestratorFactory._staging_path(
                        ms_download_extracted_folder + "\\" + ms_download_install_source_file),
                    'r') as ms_zip:
                ms_zip.extractall(OrchestratorFactory._staging_path(ms_download_extracted_folder_inner))

            os.rename(
                OrchestratorFactory._staging_path(ms_download_extracted_folder_inner + "\\" + ms_download_install_file),
                OrchestratorFactory._staging_path(OrchestratorFactory._ubuntu_template_file)
            )

            shutil.rmtree(OrchestratorFactory._staging_path(ms_download_extracted_folder))
            shutil.rmtree(OrchestratorFactory._staging_path(ms_download_extracted_folder_inner))

    def _create_orchestrator_template(self) -> None:
        weo_template_temp_instance_name = "weo_temp_instance"
        if self._wsl_api.instance_exists(weo_template_temp_instance_name):
            self._wsl_api.remove_instance(weo_template_temp_instance_name)

        if not OrchestratorFactory._orchestrator_template_file_exists():
            Logger.info("Creating temporary instance...")
            self._wsl_api.create_instance(
                weo_template_temp_instance_name,
                OrchestratorFactory._staging_path(OrchestratorFactory._ubuntu_template_file))

            self._wsl_api.run_script_as_root_in_instance(
                weo_template_temp_instance_name,
                OrchestratorFactory._script_dir + "\\template_init.sh")

            Logger.info("Exporting WEO template...")
            self._wsl_api.export_instance(
                weo_template_temp_instance_name,
                OrchestratorFactory._staging_path(OrchestratorFactory._weo_template_file))

            self._wsl_api.remove_instance(weo_template_temp_instance_name)

    def create_orchestrator(self) -> Orchestrator:
        if OrchestratorFactory._weo_template_file_exists():
            raise EOFError()
        else:
            Logger.info("WEO not initialized yet. Initializing....")
            OrchestratorFactory._download_ubuntu()
            OrchestratorFactory._extract_ubuntu()
            self._create_orchestrator_template()


if __name__ == '__main__':
    # print(OrchestratorFactory.linuxify("C:\\User\\kica"))
    factory = OrchestratorFactory()
    factory.create_orchestrator()
