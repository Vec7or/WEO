import subprocess
import os


class WslApiError(Exception):
    pass


class WslApi:
    def __init__(self, storage_path: str):
        if not storage_path.endswith("\\"):
            storage_path = storage_path + "\\"
        self._storage_path = storage_path

    def create_instance(self, name: str, template_path: str) -> None:
        wsl_create = subprocess.run(
            ['wsl.exe', '--import', name, self._storage_path + name, template_path],
            shell=True,
            capture_output=True,
            text=True)

        if wsl_create.returncode != 0:
            raise WslApiError("Instance could not be removed")

    def remove_instance(self, name: str) -> None:
        wsl_delete = subprocess.run(
            ['wsl.exe', '--unregister', name],
            shell=True,
            capture_output=True,
            text=True)
        if wsl_delete.returncode == 0:
            os.rmdir(self._storage_path + name)
        else:
            raise WslApiError("Instance could not be removed")

    def run_script_as_root_in_instance(self, name: str, script_path: str) -> None:
        linux_script_path = WslApi._linuxify(script_path)
        print(linux_script_path)
        wsl_script = subprocess.run(
            ['wsl.exe', '-u', 'root', '-d', name, '-e', linux_script_path],
            shell=True,
            # capture_output=True,
            text=True)

        if wsl_script.returncode != 0:
            raise WslApiError("Script could not be run")

    def export_instance(self, name, export_file_path):
        wsl_script = subprocess.run(
            ['wsl.exe', '--export', name, export_file_path],
            shell=True,
            capture_output=True,
            text=True)

        if wsl_script.returncode != 0:
            raise WslApiError("Instance could not be exported")

    @staticmethod
    def instance_exists(instance_name: str) -> bool:
        return instance_name in WslApi._get_wsl_list()

    @staticmethod
    def _get_wsl_list() -> str:
        wsl_list = subprocess.run(['wsl.exe', '--list'], shell=True, capture_output=True, text=True)
        if wsl_list.returncode != 0:
            # Either list could not be fetched or no distributions yet
            return ""

        wsl_list_string = wsl_list.stdout
        wsl_list_string = wsl_list_string.replace('\x00', '')
        wsl_list_string = wsl_list_string.split()
        wsl_list_string = " ".join(wsl_list_string)
        return wsl_list_string

    @staticmethod
    def _linuxify(path: str) -> str:
        volume = path[:1]
        volume = volume.lower()
        new_path = path.replace(os.sep, '/')
        new_path = new_path[2:]
        new_path = "/mnt/" + volume + new_path

        return new_path
