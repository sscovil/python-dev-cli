import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger, Logger
from typing import List

from .scripts import Scripts

logger: Logger = getLogger(__name__)


def build_arg_parser(scripts: Scripts) -> ArgumentParser:
    """Returns the dev CLI argument parser.

    :param scripts: A Scripts object containing the scripts defined in the pyproject.toml file.
    :return: An ArgumentParser object.
    """
    arg_parser: ArgumentParser = ArgumentParser(
        prog="dev", description="Python developer CLI for running custom scripts defined in pyproject.toml"
    )
    arg_parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging")
    subparsers = arg_parser.add_subparsers(dest="script", title="available scripts")
    script_keys: List[str] = sorted([key for key in scripts if not key.startswith("_")])
    [subparsers.add_parser(key, help=str(scripts.get_script_command(key))) for key in script_keys]

    return arg_parser


def dev_cli() -> None:
    """The main entry point for the dev CLI. This is the function called by the `dev` command line script."""
    scripts: Scripts = Scripts.from_config()
    cli: ArgumentParser = build_arg_parser(scripts)
    args: Namespace = cli.parse_args()
    key: str = args.script
    scripts.run_script(key) if key else cli.print_help()


if __name__ == "__main__":
    try:
        dev_cli()
    except Exception as e:
        # If the debug flag is set, raise the exception.
        for arg in sys.argv:
            if arg in ["-d", "--debug"]:
                raise e
        # Otherwise, just log the error message.
        logger.error(f"Error: {e}")
        sys.exit(1)
