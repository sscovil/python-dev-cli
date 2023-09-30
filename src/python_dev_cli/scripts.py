import re
import shlex
import shutil
from functools import lru_cache
from os.path import expandvars
from importlib.util import find_spec
from logging import Logger, getLogger
from subprocess import CompletedProcess, run
from typing import Any, Dict, Final, List, Pattern

from jinja2 import Template
from jinja2.exceptions import TemplateError

from .settings import Settings
from .config import get_pyproject_toml

logger: Logger = getLogger(__name__)

# The include pattern is used when parsing the settings.include property, and captures the following groups:
# - "os" => ("os", None, None, None)
# - "os:path" => ("os", "path", None, None)
# - "os.path:join" => ("os.path", "join", None, None)
# - "os.path:join as path_join" => ("os.path", "join", " as ", "path_join")
include_pattern: Final[Pattern] = re.compile(r"([\w+.?]+):?(\w+)?( as )?(\w+)?")

# The template pattern is used when parsing script templates, as a simple way to determine if a script is a template.
template_pattern: Final[Pattern] = re.compile(r"{{.+}}")


@lru_cache(maxsize=1)
def is_posix():
    try:
        return find_spec("posix") is not None
    except ImportError:
        return False


class ScriptTemplateError(Exception):
    """Raised when an error occurs while parsing a script template."""

    pass


class Scripts:
    """A container for storing scripts defined in the pyproject.toml file."""

    def __init__(self, settings: Settings, **kwargs):
        self.__settings: Settings = settings
        self.__scripts: Dict[str, str | List[str] | Dict[str, str]] = {}
        self.__context: Dict[str, Any] | None = None
        self.__context_hash: int | None = None

        for key, value in kwargs.items():
            self[key] = value

    def __dir__(self) -> List[str]:
        return sorted([key for key in self.__scripts.keys()])

    def __getitem__(self, item):
        return self.__scripts.get(item)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(f"Invalid script key: {key}")

        if not isinstance(value, (str, list)):
            raise TypeError(f"Invalid script value: {value}")

        self.__scripts[key] = value

    def __delitem__(self, key):
        del self.__scripts[key]

    def __contains__(self, item):
        return item in self.__scripts

    def __iter__(self):
        return iter(self.__scripts)

    def __len__(self):
        return len(self.__scripts)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.__class__.__name__}({self.__scripts})"

    @property
    def _context(self):
        """A dictionary of context values used in the Jinja2 environment when parsing script templates. This includes
        the script references defined under [tool.python-dev-cli.scripts] in pyproject.toml, as well as any modules
        defined in the `settings.include` property. The context is cached, so it is only built once per instance, unless
        any of the settings or scripts change.
        """
        current_context_hash = self.__build_context_hash()

        if self.__context is None or current_context_hash != self.__context_hash:
            # Rebuild the context if the settings or scripts have changed.
            self.__context = self.__build_context()
            self.__context_hash = current_context_hash

        return self.__context

    @staticmethod
    def from_config(config: Dict[str, Any] | None = None) -> "Scripts":
        """Returns an instance of Scripts, populated with values from the given configuration dictionary. If the
        configuration dictionary is not provided, the pyproject.toml file in the project root is used.

        :param config: An optional dictionary representing a pyproject.toml file.
        :return: An instance of Scripts, populated with values from the given configuration dictionary.
        """
        config = config or get_pyproject_toml()
        settings: Settings = Settings.from_config(config)
        scripts: Dict[str, str | List[str] | Dict[str, str]] = (
            config.get("tool", {}).get("python-dev-cli", {}).get("scripts", {})
        )

        return Scripts(settings, **scripts)

    def get_script_command(self, script_key: str, parse: bool | None = None) -> List[str]:
        """Returns a list of script commands for the given script key. If the script key is not found, a KeyError is
        raised. If the script is a template and templates are enabled, it is parsed and the resulting script commands
        are returned. Otherwise, the script is resolved and returned as a list of commands. This method always returns a
        list, even if the script is a single command.

        :param script_key: The name of the script being retrieved.
        :param parse: Whether to parse the script as a template; defaults to the value of Settings.enable_templates.
        :return: A list of script commands.
        :raises KeyError: If the script key is not found.
        :raises ScriptTemplateError: If an error occurs while parsing a script template.
        """
        parse = self.__settings.enable_templates if parse is None else parse
        return self.__parse(script_key) if parse else self.__resolve(script_key)

    def get_script_help(self, script_key: str) -> List[str]:
        """Returns a list of script commands for the given script key. If the `parse_help` setting is False, it returns
        the unparsed script commands. Otherwise, the behavior is identical to `get_script_command()`.

        :param script_key: The name of the script being retrieved.
        :return: A list of script commands.
        :raises KeyError: If the script key is not found.
        :raises ScriptTemplateError: If an error occurs while parsing a script template.
        """
        parse: bool = self.__settings.enable_templates and self.__settings.parse_help
        return self.get_script_command(script_key, parse=parse)

    def run_script(self, script_key: str, **kwargs) -> List[CompletedProcess]:
        """Runs the script commands for the given script key. If the script key is not found, a KeyError is raised. If
        the script is a template and templates are enabled, it is resolved and parsed, and the resulting list of script
        commands are run. Otherwise, the script is resolved and run as a list of unparsed commands.

        If `check` is True and the exit code was non-zero, it raises a CalledProcessError. The CalledProcessError object
        will have the return code in the `returncode` attribute, and output & stderr attributes if those streams were
        captured. If `timeout` is given, and the process takes too long, a TimeoutExpired exception will be raised.

        :param script_key: The name of the script being run.
        :param kwargs: Additional keyword arguments to pass to subprocess.run().
        :return: A list of CompletedProcess instances; these are the return values of subprocess.run().
        :raises KeyError: If the script key is not found.
        :raises ScriptTemplateError: If an error occurs while parsing a script template.
        :raises CalledProcessError: If `check` is True and the exit code was non-zero.
        :raises TimeoutExpired: If `timeout` is given, and the process takes too long.
        """
        output: List[CompletedProcess] = []

        # By default, tell subprocess.run() to raise an exception if the script fails.
        if "check" not in kwargs:
            kwargs["check"] = True

        for script in self.get_script_command(script_key):
            # Split the script into a list of args, replacing the first arg with the full executable path if possible.
            args: List[str] = shlex.split(script, posix=is_posix())
            executable: str = shutil.which(args[0])
            if executable:
                args[0] = executable

            # Run the script and append the result to the output list.
            logger.info(f"Running script [{script_key}]: {script}")
            output.append(run(args, **kwargs))

        return output

    def __build_context(self) -> Dict[str, Any]:
        """Builds a context dictionary for use when parsing script templates using Jinja2. This includes the script
        references defined under [tool.python-dev-cli.scripts] in pyproject.toml as the `settings.script_refs` property;
        and any modules defined in the `settings.include` property. If a module in the `settings.include` property does
        not match the expected format, a ValueError is raised. If a module in the `settings.include` property is not
        found, a ModuleNotFoundError is raised.

        :return: A dictionary of context values.
        :raises ValueError: If a module in the `settings.include` property does not match the expected format.
        :raises ModuleNotFoundError: If a module in the `settings.include` property is not found.
        """
        context: Dict[str, Any] = {str(self.__settings.script_refs): self.__scripts}

        # TODO: Add support for script-generated environment variables, defined in `config.tool.python_dev_cli.env`.

        # Include any modules defined in the `settings.include` property, if templates are enabled.
        if self.__settings.enable_templates:
            for include in self.__settings.include:
                match = include_pattern.match(include)
                if not match:
                    raise ValueError(f"Invalid module reference in [tool.python-dev-cli.settings.include]: {include}")
                module, attr, _, alias = match.groups()
                key = alias or attr or module
                fromlist = [attr] if attr else None
                value = __import__(module, fromlist=fromlist)  # Raises ModuleNotFoundError if module is not found.
                context[key] = getattr(value, attr) if attr else value

        return context

    def __build_context_hash(self):
        """Returns the hash of a string representation of the current settings, scripts, and context. This is used to
        invalidate the cached context when the settings or scripts change.

        :return: A hash of the string representation of settings and scripts.
        """
        return hash(str((self.__settings.__dict__, self.__scripts, self.__context)))

    def __parse(self, script_key: str) -> List[str]:
        """Parses the given script key as a template and returns the resulting script commands. If the script key is not
        found, a KeyError is raised. If the script is not a template, it is resolved and returned as a list of commands.
        This method always returns a list, even if the script is a single command. If an error occurs while parsing a
        script template, a ScriptTemplateError is raised.

        :param script_key: The name of the script being parsed.
        :return: A list of script commands.
        :raises KeyError: If the script key is not found.
        :raises ScriptTemplateError: If an error occurs while parsing a script template.
        """
        scripts: str | List[str] = self.__resolve(script_key)

        # If the script is a single command, put it in a list.
        if isinstance(scripts, str):
            scripts = [scripts]

        # If templates are enabled, parse each of the script templates.
        if self.__settings.enable_templates:
            for i, script in enumerate(scripts):
                error: str | None = None

                # Scripts can reference other scripts, so parse them recursively.
                while template_pattern.search(script):
                    try:
                        script = Template(script).render(self._context)
                    except TemplateError as e:
                        error = f"Error parsing script template [{script_key}]: {script} => {e}"
                        break

                # If an error occurred while parsing a script template, raise an exception outside the loop.
                if error:
                    raise ScriptTemplateError(error)

                # Replace the script template with the parsed script.
                scripts[i] = script

        return scripts

    def __resolve(self, script_key: str) -> List[str]:
        """Resolves the given script key and returns the resulting script commands. If the script key is not found, a
        KeyError is raised. If the script is a list of script references, they are resolved and returned as a list of
        commands. If there are nested script references, they are resolved recursively. This method always returns a
        flat list, even if the script is a list of nested script references or a single command.

        :param script_key: The name of the script being resolved.
        :return: A list of script commands.
        :raises KeyError: If the script key is not found.
        """
        if script_key not in self.__scripts:
            raise KeyError(f"Script not found: {script_key}")

        script = self.__scripts[script_key]

        if isinstance(script, str):
            return [expandvars(script)]  # Expand environment variables in the script (e.g. $HOME, ${HOME}).
        elif isinstance(script, list):
            return self.__resolve_list(script_key)
        else:
            raise TypeError(f"Invalid script type for `{script_key}`: {type(script)} (must be str or list)")

    def __resolve_list(self, list_key: str) -> List[str]:
        """Resolves the given script key and returns the resulting script commands, for the specific case where the
        script is a list of script references. Do not call this function directly; use `__resolve()` instead.

        A script defined as a list of script references can contain one or more references to other lists, so we need to
        resolve them recursively. We do this by using a stack to keep track of the unresolved script references, and a
        second list to store the resolved script commands as output. This allows us to more easily flatten the output
        list, and is more efficient than recursion in terms of memory usage and execution time, because it avoids the
        overhead of creating new stack frames for each function call.

        :param list_key: The name of the script being resolved; this script must be a list of script references.
        :return: A list of script commands.
        :raises KeyError: If the script key is not found, or if any script reference is not found.
        :raises TypeError: If the script is not a list, or if any script reference is not a str or list.
        """
        if list_key not in self.__scripts:
            raise KeyError(f"Invalid script reference: {list_key}")

        script_list = self.__scripts[list_key]

        if not isinstance(script_list, list):
            raise TypeError(f"Invalid script type for `{list_key}`: {type(script_list)} (must be list)")

        stack: List[str] = self.__scripts[list_key].copy()
        output: List[str] = []

        while len(stack) > 0:
            script_key = stack.pop(0)

            if script_key not in self.__scripts:
                raise KeyError(f"Invalid script reference `{script_key}` in: {list_key}")

            script = self.__scripts[script_key]

            if isinstance(script, str):
                output.append(expandvars(script))  # Expand environment variables in the script (e.g. $HOME, ${HOME}).
            elif isinstance(script, list):
                stack = script + stack
            else:
                raise TypeError(f"Invalid script type for `{script_key}`: {type(script)} (must be str or list)")

        return output
