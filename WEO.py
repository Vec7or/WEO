import argparse
import shutil
import subprocess
import sys
import requests
import os
import zipfile

from colorama import Fore, Back, Style
from enum import Enum

from orchestrator_factory import OrchestratorFactory
from weo_environment_action import WEOEnvironmentAction
from wsl_registry import WSLRegistry


class ExitCodes(Enum):
    INIT_FAILURE = 16


class MyArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


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
        prog='weo.exe',
        description='WEO - WSL Environment Orchestrator\nCreate wsl development ansible with ease',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='Happy coding')

    possible_action_values_str = '\nPossible values:\n'
    for action in WEOEnvironmentAction:
        possible_action_values_str += '\t - "' + action.value + '"\n'
    argument_parser.add_argument('-a', '--action', required=True, type=WEOEnvironmentAction, metavar='ACTION', choices=list(WEOEnvironmentAction),
                                 help='The action that should be performed using the environment provided.'
                                      + possible_action_values_str)
    args, unknown = argument_parser.parse_known_args()

    orchestrator_factory = OrchestratorFactory()
    try:
        orchestrator = orchestrator_factory.create_orchestrator()
    except Exception as e:
        print(e)
        sys.exit(ExitCodes.INIT_FAILURE.value)

    orchestrator.instance_action(args.action, argument_parser)

    if len(sys.argv) == 1:
        argument_parser.print_help(sys.stderr)
        sys.exit(1)
