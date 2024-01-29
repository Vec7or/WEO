from abc import ABC, abstractmethod
from argparse import ArgumentParser

from weo_environment_action import WEOEnvironmentAction


class WEOEnvironment(ABC):

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        raise NotImplementedError

    @abstractmethod
    def environment_arguments(self, action: WEOEnvironmentAction, argument_parser: ArgumentParser) -> None:
        raise NotImplementedError