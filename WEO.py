import argparse
import shutil
import subprocess
import sys
import requests
import os
import zipfile

from colorama import Fore, Back, Style
from enum import Enum
from logger import Logger
from orchestrator import Orchestrator

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


def _initialize_orchestrator(parser: argparse.ArgumentParser) -> Orchestrator:
    orchestrator_factory = OrchestratorFactory()

    if not orchestrator_factory.is_initialized():
        Logger.info("WEO not initialized yet. Getting arguments to initialize...")
        parser.add_argument(
            "-iu",
            "--instance-user",
            required=True,
            type=str,
            metavar="INSTANCE_USER",
            help="Default user for new WEO created wsl instances",
        )
        parser.add_argument(
            "-ip",
            "--instance-password",
            required=True,
            type=str,
            metavar="INSTANCE_PASSWORD",
            help="Default password for new WEO created wsl instances",
        )
        init_args, init_unknown = parser.parse_known_args()
        try:
            orchestrator_factory.initialize_orchestrator(
                init_args.instance_user, init_args.instance_password
            )
            sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(ExitCodes.INIT_FAILURE.value)
    else:
        Logger.info("WEO already initialized")
        try:
            orchestrator = orchestrator_factory.create_orchestrator()
            return orchestrator
        except Exception as e:
            print(e)
            sys.exit(ExitCodes.INIT_FAILURE.value)


def _main():
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

    orchestrator = _initialize_orchestrator(argument_parser)

    argument_parser.add_argument('-a', '--action', required=True, type=WEOEnvironmentAction, metavar='ACTION', choices=list(WEOEnvironmentAction),
                                 help='The action that should be performed using the environment provided.'
                                      + possible_action_values_str)
    args, unknown = argument_parser.parse_known_args()

    orchestrator.instance_action(args.action, argument_parser)

    if len(sys.argv) == 1:
        argument_parser.print_help(sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    _main()
