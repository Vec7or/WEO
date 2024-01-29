from argparse import ArgumentParser, Namespace

from ansible.roles.basic.BasicEnvironment import BasicEnvironment
from weo_environment import WEOEnvironment
from weo_environment_action import WEOEnvironmentAction


class ArgumentAggregator:

    def __init__(self):
        self._environments = dict[str, WEOEnvironment]()
        self._environments[BasicEnvironment.get_name()] = BasicEnvironment()

    def handle_arguments(self, environment_action: WEOEnvironmentAction,
                         argument_parser: ArgumentParser) -> Namespace:
        self._environments[BasicEnvironment.get_name()].environment_arguments(environment_action, argument_parser)
        args, unknown = argument_parser.parse_known_args()
        if not args.environment == BasicEnvironment.get_name():
            self._environments[args.environment].environment_arguments(environment_action, argument_parser)

        return argument_parser.parse_args()
