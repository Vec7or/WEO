import subprocess


class WSLRegistry:
    @staticmethod
    def instance_exists(instance_name: str) -> bool:
        return instance_name in WSLRegistry._get_wsl_list()

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
