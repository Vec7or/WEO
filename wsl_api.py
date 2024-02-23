import re
import subprocess
import os
from typing import Optional


class WslApiError(Exception):
    pass


class WslApi:
    def __init__(self, storage_path: str):
        if not storage_path.endswith("\\"):
            storage_path = storage_path + "\\"
        self._storage_path = storage_path
        os.makedirs(self._storage_path, exist_ok=True)

    def create_instance(self, name: str, template_path: str) -> None:
        wsl_create = subprocess.run(
            ['wsl.exe', '--import', name, self._storage_path + name, template_path],
            shell=True,
            capture_output=True,
            text=True)

        if wsl_create.returncode != 0:
            raise WslApiError("Instance could not be created")

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

    @staticmethod
    def run_script_as_root_in_instance(name: str, script_path: str) -> None:
        linux_script_path = WslApi._linuxify(script_path)
        print(linux_script_path)
        wsl_script = subprocess.run(
            ['wsl.exe', '-u', 'root', '-d', name, '-e', linux_script_path],
            shell=True,
            # capture_output=True,
            text=True)

        if wsl_script.returncode != 0:
            raise WslApiError("Script could not be run")

    @staticmethod
    def run_script_in_instance(name: str, script_path: str) -> None:
        linux_script_path = WslApi._linuxify(script_path)
        print(linux_script_path)
        wsl_script = subprocess.run(
            ['wsl.exe', '-d', name, '-e', linux_script_path],
            shell=True,
            # capture_output=True,
            text=True)

        if wsl_script.returncode != 0:
            raise WslApiError("Script could not be run")

    @staticmethod
    def run_command_in_instance(name: str, command: str) -> str:
        wsl_command = subprocess.run(
            ['wsl.exe', '-u', 'root', '-d', name, 'bash', '-c',
             command],
            shell=True,
            capture_output=True,
            text=True)
        print("Command: " + command)
        print(wsl_command.stdout)

        if wsl_command.returncode != 0:
            raise WslApiError("Command could not be run")

        return wsl_command.stdout

    @staticmethod
    def export_instance(name, export_file_path) -> None:
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

    def get_instance_ip(self, name) -> str:
        try:
            wsl_ip = self.run_command_in_instance(name, "ip -4 addr show eth0 | grep -oP \'(?<=inet\\s)\\d+(\\.\\d+){3}\'")
        except WslApiError:
            raise WslApiError("Instance ip could not be fetched")

        return wsl_ip

    def set_instance_ssh_port(self, name: str, new_port: Optional[int]) -> Optional[int]:
        ssh_port_pattern = r"^\s*Port\s*(?P<port>[1-9]{1,4}).*\n"
        old_port = None
        ssh_config = None
        try:
            wsl_old_ssh = self.run_command_in_instance(name, 'cat /etc/ssh/ssh_config')
        except WslApiError:
            raise WslApiError("SSH config of instance could not be read")

        ssh_config = wsl_old_ssh

        port_search = re.search(ssh_port_pattern, ssh_config, flags=re.MULTILINE)
        if port_search is not None:
            old_port = int(port_search.groups()[0])

        if not old_port and not new_port:
            # Nothing to remove or add
            pass
        elif not new_port:
            # Remove port
            ssh_config = re.sub(ssh_port_pattern, '', ssh_config, flags=re.MULTILINE)
            pass
        elif not old_port:
            # Add port
            ssh_config = ssh_config + "    Port " + str(new_port) + "\n"
        else:
            # Switch port
            ssh_config = re.sub(ssh_port_pattern, "    Port " + str(new_port) + "\n", ssh_config, flags=re.MULTILINE)
            pass

        if ssh_config:
            temp_ssh_config_path = self._storage_path + "/temp_ssh_config"
            with open(temp_ssh_config_path, "w") as f:
                f.write(ssh_config)
            try:
                wsl_write_ssh = self.run_command_in_instance(name, 'cat ' + self._linuxify(
                    temp_ssh_config_path) + ' > /etc/ssh/ssh_config')
                os.remove(temp_ssh_config_path)
            except WslApiError:
                os.remove(temp_ssh_config_path)
                raise WslApiError("SSH config of instance could not be written")

        # Restart ssh service
        try:
            wsl_restart_ssh = self.run_command_in_instance(name, '/etc/init.d/ssh restart')
        except WslApiError:
            raise WslApiError("SSH service could not be restarted")

        return old_port

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
