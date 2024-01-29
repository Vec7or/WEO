import argparse
import shutil
import subprocess
import sys
import requests
import os
import zipfile

from colorama import Fore, Back, Style
from enum import Enum

from wsl_registry import WSLRegistry


class ExitCodes(Enum):
    INIT_FAILURE = 16


class MyArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class Orchestrator:
    _staging_dir = os.path.dirname(os.path.realpath(__file__)) + "\\_staging"
    _script_dir = os.path.dirname(os.path.realpath(__file__)) + "\\scripts"

    def __int__(self):
        if not WSLRegistry.instance_exists('weo_orchestrator'):
            print(Fore.RED, end="")
            print("Orchestrator not initialized. Aborting")
            print(Style.RESET_ALL)
            exit(ExitCodes.INIT_FAILURE)

    @staticmethod
    def create_instance(instance_name: str):


    @staticmethod
    def setup_orchestrator() -> None:
        # Download template to _staging folder
        print(Fore.LIGHTBLUE_EX, end="")
        print("### Initializing WEO ###")
        print(Style.RESET_ALL)
        ms_download_file = "ubuntu_22-04.zip"
        ms_template_file = "ubuntu_22-04.tar.gz"
        weo_template_file = "weo_ubuntu.tar"
        if (not os.path.exists(Orchestrator._staging_dir + "\\" + ms_template_file)
                and not os.path.exists(Orchestrator._staging_dir + "\\" + ms_download_file)
                and not os.path.exists(Orchestrator._staging_dir + "\\" + weo_template_file)):
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Downloading template from Microsoft...")
            print(Style.RESET_ALL)
            ms_download_url = "https://aka.ms/wslubuntu2204"
            if not os.path.exists(Orchestrator._staging_dir):
                os.mkdir(Orchestrator._staging_dir)
            response = requests.get(ms_download_url, stream=True)
            total_length = response.headers.get('content-length')
            with open(Orchestrator._staging_dir + "/" + ms_download_file, "wb") as f:
                if total_length is None:  # no content length header
                    print(Fore.YELLOW, end="")
                    print("  Could not determine file size. No progress bas will be visible.")
                    print("  This might take a long time (1-2h)...")
                    print(Fore.LIGHTBLUE_EX, end="")
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        sys.stdout.write("\r  [%s%s]" % ('=' * done, ' ' * (50 - done)))
                        sys.stdout.flush()
            print("")
        else:
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Template file from microsoft already downloaded. Skipping...")
            print(Style.RESET_ALL)

        ms_download_extracted_folder = "ubuntu_22-04"
        ms_download_extracted_folder_inner = "ubuntu_22-04-install"
        if (not os.path.exists(Orchestrator._staging_dir + "\\" + ms_template_file)
                and not os.path.exists(Orchestrator._staging_dir + "\\" + weo_template_file)):
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Extracting template from Microsoft...")
            print(Style.RESET_ALL)
            ms_download_install_source_file = "Ubuntu_2204.1.7.0_x64.appx"
            ms_download_install_file = "install.tar.gz"
            if os.path.exists(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder):
                os.remove(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder)

            with zipfile.ZipFile(Orchestrator._staging_dir + "\\" + ms_download_file, 'r') as ms_zip:
                ms_zip.extractall(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder)

            with zipfile.ZipFile(
                    Orchestrator._staging_dir + "\\" + ms_download_extracted_folder + "\\" + ms_download_install_source_file,
                    'r') as ms_zip:
                ms_zip.extractall(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder_inner)

            os.rename(
                Orchestrator._staging_dir + "\\" + ms_download_extracted_folder_inner + "\\" + ms_download_install_file,
                Orchestrator._staging_dir + "\\" + ms_template_file
            )

        else:
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Extraction not needed. Skipping...")
            print(Style.RESET_ALL)

        template_prep_instance_name = 'weo_template_temp'
        orchestrator_instance_name = 'orchestrator.py'
        if not os.path.exists(Orchestrator._staging_dir + "\\" + weo_template_file):
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Creating WEO template instance...")
            print(Style.RESET_ALL)

            if WSLRegistry.instance_exists(template_prep_instance_name):
                delete_old_instance = subprocess.run([
                    "wsl.exe",
                    "--unregister",
                    template_prep_instance_name
                ], shell=True)
                if delete_old_instance.returncode != 0:
                    print(Fore.RED, end="")
                    print("  WEO template instance could not be cleaned. Aborting...")
                    print(Style.RESET_ALL)
                    exit(ExitCodes.INIT_FAILURE)

            print(Fore.LIGHTGREEN_EX, end="")
            print("ToDo: Better output of wsl commands")
            if not os.path.exists(os.path.expanduser('~') + "\\wsl\\"):
                os.makedirs(os.path.expanduser('~') + "\\wsl\\")
            import_instance = subprocess.run([
                "wsl.exe",
                "--import",
                template_prep_instance_name,
                os.path.expanduser('~') + "\\wsl\\" + template_prep_instance_name,
                Orchestrator._staging_dir + "\\" + ms_template_file
            ], shell=True)
            print(Style.RESET_ALL)
            if import_instance.returncode != 0:
                print(Fore.RED, end="")
                print("  WEO template instance could not be created. Aborting...")
                print(Style.RESET_ALL)
                exit(ExitCodes.INIT_FAILURE)
        else:
            print(Fore.LIGHTBLUE_EX, end="")
            print("  WEO template instance already created. Skipping creation...")
            print(Style.RESET_ALL)

        if not os.path.exists(Orchestrator._staging_dir + "\\" + weo_template_file):
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Initializing WEO template instance...")
            print(Style.RESET_ALL)

            print(Fore.LIGHTGREEN_EX, end="")
            print("ToDo: Better output of wsl commands")
            print(Orchestrator._script_dir)
            init_script_path_get = subprocess.run([
                "wsl.exe",
                "-d",
                template_prep_instance_name,
                "-u",
                "root",
                "wslpath",
                "'" + Orchestrator._script_dir + "\\template_init.sh'"
                ],
                shell=True,
                capture_output=True,
                text=True)
            print("Hello: " + init_script_path_get.stdout)
            init_script_path = init_script_path_get.stdout
            prepare_instance = subprocess.run([
                "wsl.exe",
                "-d",
                template_prep_instance_name,
                "-u",
                "root",
                "bash",
                "-ic",
                init_script_path
            ], shell=True)
            print(Style.RESET_ALL)
            if prepare_instance.returncode != 0:
                print(Fore.RED, end="")
                print("  WEO template instance could not be initialized. Aborting...")
                print(Style.RESET_ALL)
                exit(ExitCodes.INIT_FAILURE)

            print(Fore.LIGHTBLUE_EX, end="")
            print("  Exporting WEO template instance...")
            print(Style.RESET_ALL)

            print(Fore.LIGHTGREEN_EX, end="")
            print("ToDo: Better output of wsl commands")
            export_template = subprocess.run([
                "wsl.exe",
                "--export",
                template_prep_instance_name,
                Orchestrator._staging_dir + "\\" + weo_template_file,
            ], shell=True)
            print(Style.RESET_ALL)
            if export_template.returncode != 0:
                print(Fore.RED, end="")
                print("  WEO template instance could not be exported. Aborting...")
                print(Style.RESET_ALL)
                exit(ExitCodes.INIT_FAILURE)

            print(Fore.LIGHTBLUE_EX, end="")
            print("  Removing WEO template instance...")
            print(Style.RESET_ALL)

            print(Fore.LIGHTGREEN_EX, end="")
            print("ToDo: Better output of wsl commands")
            export_template = subprocess.run([
                "wsl.exe",
                "--unregister",
                template_prep_instance_name,
            ], shell=True)
            print(Style.RESET_ALL)
            if export_template.returncode != 0:
                print(Fore.RED, end="")
                print("  WEO template instance could not be removed. Aborting...")
                print(Style.RESET_ALL)
                exit(ExitCodes.INIT_FAILURE)
        else:
            print(Fore.LIGHTBLUE_EX, end="")
            print("  WEO template instance already created. Skipping initialization...")
            print(Style.RESET_ALL)

        if not WSLRegistry.instance_exists(orchestrator_instance_name):
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Creating Orchestrator instance...")
            print(Style.RESET_ALL)

            print(Fore.LIGHTGREEN_EX, end="")
            print("ToDo: Better output of wsl commands")
            if not os.path.exists(os.path.expanduser('~') + "\\wsl\\"):
                os.makedirs(os.path.expanduser('~') + "\\wsl\\")
            import_instance = subprocess.run([
                "wsl.exe",
                "--import",
                orchestrator_instance_name,
                os.path.expanduser('~') + "\\wsl\\" + orchestrator_instance_name,
                Orchestrator._staging_dir + "\\" + weo_template_file
            ], shell=True)
            print(Style.RESET_ALL)
            if import_instance.returncode != 0:
                print(Fore.RED, end="")
                print("  WEO orchestrator instance could not be created. Aborting...")
                print(Style.RESET_ALL)
                exit(ExitCodes.INIT_FAILURE)

        else:
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Orchestrator already created. Skipping creation...")
            print(Style.RESET_ALL)

        if os.path.exists(Orchestrator._staging_dir + "\\" + ms_template_file):
            print(Fore.LIGHTBLUE_EX, end="")
            print("  Cleanup temporary files...")
            print(Style.RESET_ALL)
            if os.path.exists(Orchestrator._staging_dir + "\\" + ms_download_file):
                os.remove(Orchestrator._staging_dir + "\\" + ms_download_file)
            if os.path.exists(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder):
                shutil.rmtree(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder, ignore_errors=True)
            if os.path.exists(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder_inner):
                shutil.rmtree(Orchestrator._staging_dir + "\\" + ms_download_extracted_folder_inner, ignore_errors=True)
        else:
            print(Fore.RED, end="")
            print("  Template fetching failed. Aborting...")
            print(Style.RESET_ALL)
            exit(ExitCodes.INIT_FAILURE)


if __name__ == '__main__':
    print(Fore.GREEN, end="")
    print("██     ██     ███████              ██████             ")
    print("██     ██     ██                  ██    ██            ")
    print("██  █  ██     █████               ██    ██            ")
    print("██ ███ ██     ██                  ██    ██            ")
    print(" ███ ███  SL  ███████ NVIRONMENT   ██████  RCHESTRATOR")
    print("                                                      ")
    print(Style.RESET_ALL)
    argument_parser = MyArgParser(
        prog='WEO - WSL Environment Orchestrator',
        description='Create wsl development ansible with ease',
        epilog='Text at the bottom of help')
    argument_parser.add_argument('-i', '--init', dest='init', action='store_true',
                                 help='Initializes the WEO. Has to be done before first use')
    args = argument_parser.parse_args()
    if len(sys.argv) == 1:
        argument_parser.print_help(sys.stderr)
        sys.exit(1)

    if args.init:
        Orchestrator.setup_orchestrator()
