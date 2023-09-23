from typing import List, Dict, Any

from .config import get_pyproject_toml


class Settings:
    """A container for storing dev module settings, with defaults for any missing values."""

    def __init__(self, **kwargs) -> None:
        self.enable_templates = kwargs.get("enable_templates", True)
        self.include = kwargs.get("include", None)
        self.script_refs = kwargs.get("script_refs", "dev")

    def __dir__(self) -> List[str]:
        return sorted([key for key in self.__dict__.keys()])

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    @property
    def enable_templates(self):
        """Whether to enable Jinja2 templates. Defaults to True. This enables the use of built-in Python syntax,
        arbitrary Python modules, and references to other scripts. For example, the following script command will print
        the current working directory (if the `os` module is added to the `include` settings list):

        `echo {{ os.getcwd() }}` => `echo /path/to/current/working/directory`

        If False, scripts are parsed as plain strings and the `include` and `script_refs` settings are ignored.
        """
        return self._enable_templates

    @enable_templates.setter
    def enable_templates(self, value: bool | int):
        self._enable_templates = bool(value)

    @property
    def include(self):
        """A list of Python modules to include when parsing script templates. Defaults to an empty list. Modules in this
        list are imported and added to the Jinja2 environment, so they can be called in script templates if the setting
        `enable_templates` is True. This allows you to specify which modules are available in script templates, and use
        them like this: `echo {{ os.getcwd() }}` => `echo /path/to/current/working/directory`

        Valid module formats are: ["os", "os.path", "os.path:join", "os.path:join as path_join"]
        - "os" => import os
        - "os:path" => from os import path
        - "os.path:join" => from os.path import join
        - "os.path:join as path_join" => from os.path import join as path_join
        """
        return self._include

    @include.setter
    def include(self, value: List[str] | None):
        self._include = list(value) if value is not None else []

    @property
    def script_refs(self):
        """Name of the object used to store scripts defined under [tool.python-dev-cli.scripts] in pyproject.toml.
        Defaults to 'dev'. These references are available in script templates, if `enable_templates` is True.
        """
        return self._script_refs

    @script_refs.setter
    def script_refs(self, value: str):
        self._script_refs = str(value)

    @staticmethod
    def from_config(config: Dict[str, Any] | None = None) -> "Settings":
        """Returns an instance of Settings, populated with values from the given configuration dictionary. If the
        configuration dictionary is not provided, the pyproject.toml file in the project root is used.

        :param config: An optional dictionary representing a pyproject.toml file.
        :return: An instance of Settings, populated with values from the given configuration dictionary.
        """
        config = config or get_pyproject_toml()
        settings: Dict[str, bool] = config.get("tool", {}).get("python-dev-cli", {}).get("settings", {})
        return Settings(**settings)
