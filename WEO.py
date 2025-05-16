import configparser
import sys
from enum import Enum

import click
from rich.console import Console

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


def _get_orchestrator(verbose: bool) -> Orchestrator:
    click.secho(f"Checking WEO status", fg="blue")
    orchestrator_factory = OrchestratorFactory(verbose)
    match orchestrator_factory.status:
        case OrchestratorFactoryStatus.OK:
            click.secho(f"WEO already initialized. Continuing...", fg="blue")
        case OrchestratorFactoryStatus.NO_ORCHESTRATOR:
            click.secho(f"WEO not initialized yet. Initializing...", fg="blue")
        case OrchestratorFactoryStatus.INCOMPATIBLE_ORCHESTRATOR:
            click.secho("Orchestrator instance incompatible with WEO version. Adjusting "
                       "orchestrator instance...", fg="blue")

    try:
        orchestrator_factory.initialize(overwrite=True)
        return orchestrator_factory.create_orchestrator()
    except OrchestratorError as e:
        click.secho(f"{e}", fg="red")
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
@click.option("-v", "--verbose",
              is_flag=True,
              required=False,
              help="Print verbose log outputs.")
def create(docker_image, environment_name, local, environment_password, user, verbose):
    orchestrator = _get_orchestrator(verbose)
    try:
        click.secho(f"Creating environment {environment_name}", fg="blue")
        if not verbose:
            console = Console()
            with console.status("[bold dodger_blue1]Working on creation...") as status:
                log_func = lambda str : status.update(f"[bold dodger_blue1] {str}")
                orchestrator.create(log_func, docker_image, environment_name, local, environment_password, user)
        else:
            log_func = lambda str : click.secho(f"[PROGRESS:] {str}", fg="blue")
            orchestrator.create(log_func, docker_image, environment_name, local, environment_password, user)

        click.secho(f"Successfully created environment {environment_name}", fg="blue")
    except (OrchestratorError, configparser.Error, EnvironmentExistsError) as e:
        click.secho(f"{e}", fg="red")
        sys.exit(ExitCodes.CREATION_FAILURE.value)


@cli.command(help="Removes an existing wsl environment")
@click.option("-e", "--environment-name", required=True,
              help="The name of the new environment that will be removed")
@click.option("-v", "--verbose",
              is_flag=True,
              required=False,
              help="Print verbose log outputs.")
def remove(environment_name, verbose):
    orchestrator = _get_orchestrator(verbose)
    try:
        click.secho(f"Removing environment {environment_name}", fg="blue")
        orchestrator.remove(environment_name)
        click.secho(f"Successfully removed environment {environment_name}", fg="blue")
    except EnvironmentNotFoundError:
        click.secho(f"Environment {environment_name} does not exist. Skipping...", fg="yellow")
    except ConfigNotFoundError:
        click.secho(f"The environment {environment_name} was not created by WEO. Aborting...", fg="red")
    except configparser.Error:
        click.secho(f"The environment {environment_name} does not have a valid WEO configuration file. Aborting...", fg="red")
    except OrchestratorError as e:
        click.secho(f"{e}", fg="red")
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
    click.secho("██     ██     ███████              ██████             ", fg="green")
    click.secho("██     ██     ██                  ██    ██            ", fg="green")
    click.secho("██  █  ██     █████               ██    ██            ", fg="green")
    click.secho("██ ███ ██     ██                  ██    ██            ", fg="green")
    click.secho(" ███ ███  SL  ███████ NVIRONMENT   ██████  RCHESTRATOR", fg="green")
    click.secho("                                                      ", fg="green")
    click.secho(f"VERSION: {WEO_VERSION}                               ", fg="green")
    cli()
