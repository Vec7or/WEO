import subprocess
from argparse import ArgumentParser

from argument_aggregator import ArgumentAggregator
from weo_environment_action import WEOEnvironmentAction
from wsl_api import WslApi, WslApiError


class Orchestrator:
    def __init__(self, orchestrator_instance_name: str, wsl_api: WslApi, orchestrator_template_path: str):
        self._instance_name = orchestrator_instance_name
        self._wsl_api = wsl_api
        self._template_path = orchestrator_template_path
        self._argument_aggregator = ArgumentAggregator()
        self._temp_ssh_port = 54836

    def instance_action(self, action: WEOEnvironmentAction, parser: ArgumentParser):
        args = self._argument_aggregator.handle_arguments(action, parser)
        if action == WEOEnvironmentAction.CREATE:
            # if self._wsl_api.instance_exists(args.instance_name):
            #    raise RuntimeError("Instance already exists")
            self._wsl_api.create_instance(args.instance_name, self._template_path)
            try:
                ip = self._wsl_api.get_instance_ip(args.instance_name)
                old_port = self._wsl_api.set_instance_ssh_port(args.instance_name, self._temp_ssh_port)
                self._checkout_weo('main')
                # Ansible shissel
            finally:
                self._wsl_api.remove_instance(args.instance_name)
            self._wsl_api.remove_instance(args.instance_name)

    def _checkout_weo(self, git_hash: str):
        try:
            git_checkout = self._wsl_api.run_command_in_instance(self._instance_name,
                                                                 'cd /opt/weo && git checkout ' + git_hash)
            print(git_checkout)
        except WslApiError:
            print("What?")
            raise RuntimeError("Could not checkout git hash")
