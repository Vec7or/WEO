import base64
import os
from argparse import ArgumentParser, Namespace
from shutil import copyfile

from argument_aggregator import ArgumentAggregator
from config_manager import ConfigManager
from weo_environment_action import WEOEnvironmentAction
from wsl_api import WslApi, WslApiError


class Orchestrator:
    _repo_root = '/opt/weo'
    _ansible_root = '/opt/weo/ansible'
    _config_file = '/etc/weo.conf'

    def __init__(self, orchestrator_instance_name: str, wsl_api: WslApi, orchestrator_template_path: str,
                 config_manager: ConfigManager):
        self._instance_name = orchestrator_instance_name
        self._wsl_api = wsl_api
        self._template_path = orchestrator_template_path
        self._argument_aggregator = ArgumentAggregator()
        self._temp_ssh_port = 54836
        self._config_manager = config_manager

    def instance_action(self, action: WEOEnvironmentAction, parser: ArgumentParser):
        args = self._argument_aggregator.handle_arguments(action, parser)
        if action == WEOEnvironmentAction.CREATE:
            self._create(args)

    def _create(self, args: Namespace):
        # if self._wsl_api.instance_exists(args.instance_name):
        #    raise RuntimeError("Instance already exists")
        self._wsl_api.create_instance(args.instance_name, self._template_path)
        try:
            ip = self._wsl_api.get_instance_ip(args.instance_name)
            old_port = self._wsl_api.set_instance_ssh_port(args.instance_name, self._temp_ssh_port)
            self._checkout_weo('feature/initial-version')
            # Ansible shissel
            self._adjust_inventory_file(ip)
            print(self._wsl_api.run_command_in_instance(
                self._instance_name,
                'ansible-playbook -i ' + self._ansible_root + '/inventory.yml -e weo_environment=basic -e instance_user_name=developer -e instance_user_password=test1234 ' + self._ansible_root + '/playbook.yml'))
            self._wsl_api.set_instance_ssh_port(args.instance_name, old_port)
        except Exception as e:
            print(e)
            self._wsl_api.remove_instance(args.instance_name)

    def _adjust_inventory_file(self, ip):
        inventory_path = self._ansible_root + '/inventory.yml'
        inventory_content = self._wsl_api.run_command_in_instance(self._instance_name,
                                                                  "cat " + self._ansible_root + '/inventory.in.yml')
        inventory_content = inventory_content.replace('{{ weo_host }}', ip)
        inventory_content = inventory_content.replace('{{ weo_port }}', str(self._temp_ssh_port))
        inventory_content = inventory_content.replace('{{ weo_user }}',
                                                      self._config_manager.read_config().get('user',
                                                                                             'username'))  # ToDo: Adjust
        inventory_content = inventory_content.replace('{{ weo_password }}',
                                                      self._config_manager.read_config().get('user',
                                                                                             'password'))  # ToDo: Adjust
        inventory_content_base64 = base64.b64encode(inventory_content.encode('utf-8'))

        self._wsl_api.run_command_in_instance(self._instance_name,
                                              "rm -f " + inventory_path)
        self._wsl_api.run_command_in_instance(self._instance_name,
                                              "echo " + inventory_content_base64.decode(
                                                  'utf-8') + " | base64 --decode >> " + inventory_path)

    def _checkout_weo(self, git_hash: str):
        try:
            git_checkout = self._wsl_api.run_command_in_instance(self._instance_name,
                                                                 'cd ' + self._repo_root + ' && git checkout ' + git_hash + ' && git pull',
                                                                 self._config_manager.read_config().get('user',
                                                                                                        'username'))  # ToDo: Read user from file
            print(git_checkout)
        except WslApiError:
            print("What?")
            raise RuntimeError("Could not checkout git hash")
