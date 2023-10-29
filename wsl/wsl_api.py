import subprocess
import os


class WslApiError(Exception):
    pass


class WslApi:
    def __init__(self, storage_path: str):
        if not storage_path.endswith("\\"):
            storage_path = storage_path + "\\"
        self._storage_path = storage_path
        os.makedirs(self._storage_path, exist_ok=True)

    def create_instance(self, name: str, template_path: str) -> None:
        print(f"Creating instance {name}")
        wsl_create = subprocess.run(
            ['wsl.exe', '--import', name, self._storage_path + name, template_path],
            shell=True,
            check=False,
            capture_output=True,
            text=True)

        if wsl_create.returncode != 0:
            stdout = "" if not wsl_create.stdout else " Stdout: " + wsl_create.stdout
            stderr = "" if not wsl_create.stderr else " Stderr: " + wsl_create.stderr
            raise WslApiError(
                "Instance could not be created." + stdout + stderr)

    def remove_instance(self, name: str) -> None:
        wsl_delete = subprocess.run(
            ['wsl.exe', '--unregister', name],
            shell=True,
            check=False,
            capture_output=True,
            text=True)
        if wsl_delete.returncode == 0:
            os.rmdir(self._storage_path + name)
        else:
            stdout = "" if not wsl_delete.stdout else " Stdout: " + wsl_delete.stdout
            stderr = "" if not wsl_delete.stderr else " Stderr: " + wsl_delete.stderr
            raise WslApiError("Instance could not be removed." + stdout + stderr)

    @staticmethod
    def run_command_in_instance(name: str, command: str, user: str = 'root') -> str:
        print(command)
        wsl_command = subprocess.run(
            ['wsl.exe', '-u', user, '-d', name, 'sh', '-c',
             command],
            shell=True,
            capture_output=True,
            text=True)

        if wsl_command.returncode != 0:
            stdout = "" if not wsl_command.stdout else " Stdout: " + wsl_command.stdout
            stderr = "" if not wsl_command.stderr else " Stderr: " + wsl_command.stderr
            raise WslApiError(
                "Command could not be run." + stdout + stderr)

        return wsl_command.stdout

    @staticmethod
    def file_exists_in_instance(name: str, path: str) -> bool:
        res = WslApi.run_command_in_instance(
            name,
            f"test -f {path} && echo \"EXISTS\" || echo \"NOT EXISTENT\""
        )
        if res.strip() != "EXISTS":
            return False
        return True

    @staticmethod
    def export_instance(name, export_file_path) -> None:
        wsl_script = subprocess.run(
            ['wsl.exe', '--export', name, export_file_path],
            shell=True,
            check=True,
            capture_output=True,
            text=True)

        if wsl_script.returncode != 0:
            stdout = "" if not wsl_script.stdout else " Stdout: " + wsl_script.stdout
            stderr = "" if not wsl_script.stderr else " Stderr: " + wsl_script.stderr
            raise WslApiError(
                "Instance could not be exported." + stdout + stderr)

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
    def linuxify(path: str) -> str:
        volume = path[:1]
        volume = volume.lower()
        new_path = path.replace(os.sep, '/')
        new_path = new_path[2:]
        new_path = "/mnt/" + volume + new_path

        return new_path
