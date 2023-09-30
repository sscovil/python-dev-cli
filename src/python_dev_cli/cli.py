import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger, Logger
from typing import List

from .scripts import Scripts

logger: Logger = getLogger(__name__)


def build_arg_parser(scripts: Scripts) -> ArgumentParser:
    """Returns the dev CLI argument parser. See also: https://docs.python.org/3/library/argparse.html

    :param scripts: A Scripts object containing the scripts defined in the pyproject.toml file.
    :return: An ArgumentParser object.
    """
    arg_parser: ArgumentParser = ArgumentParser(
        prog="dev", description="Python developer CLI for running custom scripts defined in pyproject.toml"
    )
    arg_parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging")

    # Add a subparser for each script defined in pyproject.toml, excluding scripts that start with an underscore.
    subparsers = arg_parser.add_subparsers(dest="script", title="available scripts")
    script_keys: List[str] = sorted([key for key in scripts if not key.startswith("_")])
    [subparsers.add_parser(key, help=str(scripts.get_script_help(key))) for key in script_keys]

    return arg_parser


def dev_cli() -> None:
    """The main entry point for the dev CLI. This is the function called by the `dev` command line script."""
    try:
        scripts: Scripts = Scripts.from_config()
        cli: ArgumentParser = build_arg_parser(scripts)
        args: Namespace = cli.parse_args()
        key: str = args.script
        scripts.run_script(key) if key else cli.print_help()
    except Exception as e:
        if "-d" in sys.argv or "--debug" in sys.argv:
            raise e
        else:
            logger.error(e)


if __name__ == "__main__":
    dev_cli()
