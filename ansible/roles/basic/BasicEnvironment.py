from argparse import ArgumentParser

from weo_environment import WEOEnvironment
from weo_environment_action import WEOEnvironmentAction


class BasicEnvironment(WEOEnvironment):
    @staticmethod
    def get_name() -> str:
        return 'basic'

    def environment_arguments(self, action: WEOEnvironmentAction, argument_parser: ArgumentParser) -> None:
        if action == WEOEnvironmentAction.CREATE:
            argument_parser.add_argument('-e', '--environment', required=True, type=str, metavar='ENVIRONMENT',
                                         help='The environment affected by the action.')
        argument_parser.add_argument('-in', '--instance-name', required=True, type=str, metavar='INSTANCE_NAME',
                                     help='The name of the instance to be affected')
        pass

    def __init__(self):
        pass
