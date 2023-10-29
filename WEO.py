import configparser
import sys
from enum import Enum

import click
from colorama import Fore, Style

from config.version import WEO_VERSION
from exceptions.ConfigNotFoundError import ConfigNotFoundError
from exceptions.EnvironmentExistsError import EnvironmentExistsError
from exceptions.EnvironmentNotFoundError import EnvironmentNotFoundError
from exceptions.OrchestratorError import OrchestratorError
from orchestrator.orchestrator import Orchestrator
from orchestrator.orchestrator_factory import OrchestratorFactory, OrchestratorFactoryStatus


class ExitCodes(Enum):
    INIT_FAILURE = 16
    CREATION_FAILURE = 26


def _get_orchestrator() -> Orchestrator:
    orchestrator_factory = OrchestratorFactory()
    match orchestrator_factory.status:
        case OrchestratorFactoryStatus.OK:
            click.echo(f"{Fore.LIGHTBLUE_EX}WEO already initialized. Continuing...{Style.RESET_ALL}")
        case OrchestratorFactoryStatus.NO_ORCHESTRATOR:
            click.echo(f"{Fore.LIGHTBLUE_EX}WEO not initialized yet. Initializing...{Style.RESET_ALL}")
        case OrchestratorFactoryStatus.INCOMPATIBLE_ORCHESTRATOR:
            click.echo(f"{Fore.LIGHTYELLOW_EX}Orchestrator instance incompatible with WEO version. Adjusting "
                       f"orchestrator instance...{Style.RESET_ALL}")

    try:
        orchestrator_factory.initialize(overwrite=True)
        return orchestrator_factory.create_orchestrator()
    except OrchestratorError as e:
        click.echo(f"{Fore.RED}{e}{Style.RESET_ALL}")
        sys.exit(ExitCodes.INIT_FAILURE.value)


@click.group()
def cli():
    pass


@cli.command(help="Creates a new wsl environment")
@click.option("-d", "--docker-image", required=True,
              help="The name of the docker image to use as "
                   "environment base")
@click.option("-e", "--environment-name", required=True,
              help="The name of the new environment that will be created")
@click.option("-l", '--local',
              type=click.Choice(['FILE', 'DIR'], case_sensitive=False),
              help ="If this is set the option \"-d\" "
                    "will be interpreted as a local path to a dockerfile or to "
                    "a directory containing a dockerfile and it's build assets "
                    "dependent on the value.")
@click.option("-p", "--environment-password", default="WEO",
              show_default=True, required=True,
              help="The password of the user within the new "
                   "environment")
@click.option("-u", "--user",
              required=False,
              help="The user that should be used within the environment. "
                   "This user needs to exist in the image.")
def create(docker_image, environment_name, local, environment_password, user):
    orchestrator = _get_orchestrator()
    try:
        orchestrator.create(docker_image, environment_name, local, environment_password, user)
    except (OrchestratorError, configparser.Error, EnvironmentExistsError) as e:
        click.echo(f"{Fore.RED}{e}{Style.RESET_ALL}")
        sys.exit(ExitCodes.CREATION_FAILURE.value)


@cli.command(help="Removes an existing wsl environment")
@click.option("-e", "--environment-name", required=True,
              help="The name of the new environment that will be removed")
def remove(environment_name):
    orchestrator = _get_orchestrator()
    try:
        orchestrator.remove(environment_name)
        click.echo(f"{Fore.LIGHTBLUE_EX}Successfully removed environment {environment_name}{Style.RESET_ALL}")
    except EnvironmentNotFoundError:
        click.echo(f"{Fore.LIGHTYELLOW_EX}Environment does not exist. Skipping...{Style.RESET_ALL}")
    except ConfigNotFoundError:
        click.echo(f"{Fore.RED}The environment was not created by WEO. Aborting...{Style.RESET_ALL}")
    except configparser.Error:
        click.echo(
            f"{Fore.RED}The environment does not have a valid WEO configuration file. Aborting...{Style.RESET_ALL}")
    except OrchestratorError as e:
        click.echo(f"{Fore.RED}{e}{Style.RESET_ALL}")
        sys.exit(ExitCodes.CREATION_FAILURE.value)


# ToDo: Implement
# @cli.command()
# def export_env():
#     pass


# ToDo: Implement
# @cli.command()
# def import_env():
#     pass


# ToDo: Implement
# @cli.command()
# def change_pw():
#     pass


if __name__ == '__main__':
    click.echo(Fore.GREEN)
    click.echo("██     ██     ███████              ██████             ")
    click.echo("██     ██     ██                  ██    ██            ")
    click.echo("██  █  ██     █████               ██    ██            ")
    click.echo("██ ███ ██     ██                  ██    ██            ")
    click.echo(" ███ ███  SL  ███████ NVIRONMENT   ██████  RCHESTRATOR")
    click.echo("                                                      ")
    click.echo(f"VERSION: {WEO_VERSION}                               ")
    click.echo(Style.RESET_ALL)
    cli()
