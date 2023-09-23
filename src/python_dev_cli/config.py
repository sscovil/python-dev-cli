import os
import tomllib
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Dict

logger: Logger = getLogger(__name__)


def get_project_root() -> str:
    """Returns the path to the project root. This is the directory that should contain the pyproject.toml file.

    :return: The path to the project root.
    """
    path = Path().cwd()

    while Path(path, "__init__.py").exists():
        if path.parent == path:
            break  # Prevent infinite loop if __init__.py is in the root directory.
        path = path.parent

    return path


def get_pyproject_toml(path: str | None = None) -> Dict[str, Any]:
    """Returns the project configuration from the pyproject.toml file in the project root. If the file is not found, a
    FileNotFoundError is raised.

    :param path: The path to the pyproject.toml file; defaults to the project root.
    :return: A dictionary of project configuration values.
    :raises FileNotFoundError: If the pyproject.toml file is not found.
    """
    path = os.path.join(get_project_root(), "pyproject.toml") if path is None else path

    if not os.path.exists(path):
        raise FileNotFoundError(f"No pyproject.toml fil found in project root: {path}")

    with open(path, "rb") as file:
        return tomllib.load(file)
