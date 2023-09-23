# Python Developer CLI

Python developer CLI enables you to run custom scripts defined in your [pyproject.toml] file, eliminating the need for
shell scripts and Makefiles, and reducing extraneous cognitive load on your teammates and contributors.

- Optional [Jinja2] template support enables you to reference built-in Python syntax, arbitrary Python modules, and even
other scripts from within your script configurations.
- String together multiple scripts with a single command, to simplify complex workflows.
- All custom scripts are automatically documented in the `dev` CLI help page. Just run `dev --help` to see exactly what
each script does.

## Installation

```shell
pip install python-dev-cli
```

## Usage

Define custom scripts in your `pyproject.toml` file:

```toml
[tool.python-dev-cli.scripts]
up = "docker compose up -d"
down = "docker compose down -v --remove-orphans"
```

Then run the `dev` command followed by the script name:

```shell
dev up
# docker compose up -d

dev down
# docker compose down -v --remove-orphans
```

All scripts defined in your `pyproject.toml` file will be automatically documented in the `dev` CLI help page:

```shell
dev --help
# usage: dev [-h] [-d] {down,up} ...
# 
# Python developer CLI for running custom scripts defined in pyproject.toml
# 
# options:
#   -h, --help            show this help message and exit
#   -d, --debug           enable debug logging
# 
# available scripts:
#   {down,up}
#     down                ['docker compose down -v --remove-orphans']
#     up                  ['docker compose up -d']
```

Any script that is prefixed with an underscore (`_`) will be hidden from the help page and cannot be run directly:

```toml
[tool.python-dev-cli.scripts]
_foo = "foo"
_bar = "bar"
foobar = "echo {{ dev._foo }}{{ dev._bar }}"
```

```shell
dev -h
# usage: dev [-h] [-d] {foobar} ...
# Python developer CLI for running custom scripts defined in pyproject.toml
# 
# options:
#   -h, --help            show this help message and exit
#   -d, --debug           enable debug logging
# 
# available scripts:
#   {foobar}
#     foobar              ['echo foobar']
```

You can also define scripts as a list of script references, which will be run in order:

```toml
[tool.python-dev-cli.scripts]
black = "black --check --config pyproject.toml ."
black_fix = "black --config pyproject.toml ."
ruff = "ruff --config pyproject.toml ."
ruff_fix = "ruff --fix --exit-non-zero-on-fix --config pyproject.toml ."
lint = ["black", "ruff"]
lint_fix = ["black_fix", "ruff_fix"]
```

```shell
dev lint
# black --check --config pyproject.toml .
# ruff --config pyproject.toml .

dev lint_fix
# black --config pyproject.toml .
# ruff --fix --exit-non-zero-on-fix --config pyproject.toml .
```

By default, scripts can utilize [Jinja2] template syntax, enabling you to reference built-in Python syntax, arbitrary
Python modules, and even other scripts:

```toml
[tool.python-dev-cli.settings]
include = ["os", "uuid:uuid4 as uuid"]

[tool.python-dev-cli.scripts]
python = "echo {{ 1 + 1 }}"
module = "echo {{ uuid() }}"
env_vars = "echo PATH={{ os.getenv('PATH') }} PWD={{ os.getenv('PWD') }} HOME={{ os.getenv('HOME') }}"
other_scripts = "echo {{ dev._foo }}{{ dev._bar }}"
_foo = "foo"
_bar = "bar"
```

```shell
dev python
# 2

dev module
# 2b2e0b9e-0b9e-4a4a-9a9a-9a9a9a9a9a9a

dev env_vars
# PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin PWD=/Users/username/Projects HOME=/Users/username

dev other_scripts
# foobar
```

Script template functionality can be disabled, if you prefer to keep things simple. See the [Settings](#settings)
section below for more information.

## Settings

You can configure this package by adding a `tool.python-dev-cli.settings` section to your `pyproject.toml` file:

```toml
[tool.python-dev-cli.settings]
enable_templates = true
include = ["os", "sys"]
script_refs = "dev"
```

### enable_templates

Enable or disable the use of [Jinja2] templates in your scripts. If you disable this, all other settings will be ignored
and scripts will be run as-is, without any preprocessing.

> **NOTE:** Disabling this setting will prevent you from referencing other scripts from within a script, but you will
> still be able to reference other scripts in a list of scripts.

For example, this will still work:

```toml
[tool.python-dev-cli.settings]
enable_templates = false

[tool.python-dev-cli.scripts]
_foo = "echo foo"
_bar = "echo bar"
foobar = ["_foo", "_bar"]
```

```shell
dev foobar
# foo
# bar
```

However, this will not work as intended because the template will not be parsed:

```toml
[tool.python-dev-cli.settings]
enable_templates = false

[tool.python-dev-cli.scripts]
_foo = "foo"
_bar = "bar"
foobar = "echo {{ dev._foo }}{{ dev._bar }}"
```

```shell
dev foobar
# {{ dev._foo }}{{ dev._bar }}
```

### include

A list of modules to include in the [Jinja2] environment, when parsing scripts. This enables you to reference Python
modules in your scripts:

```toml
[tool.python-dev-cli.settings]
include = ["os:getcwd", "os:getenv as env"]

[tool.python-dev-cli.scripts]
test_docker = "docker run -it --rm -v {{ getcwd() }}:/app -w /app --name test {{ env('MY_DOCKER_IMAGE', 'python:3.11-alpine') }} echo test"
```

```shell
dev test_docker
# docker run -it --rm -v /Users/username/Projects/dev:/app -w /app --name test python:3.11-alpine echo test

MY_DOCKER_IMAGE="python:3.11-slim-bookworm"; dev test_docker
# docker run -it --rm -v /Users/username/Projects/dev:/app -w /app --name test python:3.11-slim-bookworm echo test
```

Valid formats for including modules are:

| Include Syntax                | Python Equivalent                       |
|-------------------------------|-----------------------------------------|
| `"os"`                        | `import os`                             |
| `"os:path"`                   | `from os import path`                   |
| `"os.path:join"`              | `from os.path import join`              |
| `"os.path:join as path_join"` | `from os.path import join as path_join` |

> **NOTE:** Any module available in your project can be made available to your scripts, including third-party modules
> and even your own modules.

### script_refs

Scripts can contain references to other scripts, using the `{{ dev.my_script }}` syntax:

```toml
[tool.python-dev-cli.scripts]
_foo = "foo"
_bar = "bar"
foobar = "echo {{ dev._foo }}{{ dev._bar }}"
```

```shell
dev foobar
# foobar
```

The name of the `dev` object is configurable using the `script_refs` setting. For example, you could change it to
`scripts`:

```toml
[tool.python-dev-cli.settings]
script_refs = "scripts"

[tool.python-dev-cli.scripts]
_foo = "foo"
_bar = "bar"
foobar = "echo {{ scripts._foo }}{{ scripts._bar }}"
```

```shell
dev foobar
# foobar
```

## Caveats

### Shell Syntax

Scripts are run in a Python subprocess using [subprocess.run()], not the shell interpreter that the `dev` CLI is being
run in. As a result, it has the following limitations:

- Environment variables cannot be referenced as you would in a shell script (e.g. `$HOME` or `${HOME}`).
- Shell syntax (e.g. pipes `|`; redirects `>`, `>>`, `<`; backgrounding [`&`]) is not supported.

To work around these limitations, you can use the `os` module to reference environment variables, and the `subprocess`
module to run shell commands:

```toml
[tool.python-dev-cli.settings]
include = ["os", "subprocess"]

[tool.python-dev-cli.scripts]
env_vars = "echo PATH={{ os.getenv('PATH') }} PWD={{ os.getenv('PWD') }} HOME={{ os.getenv('HOME') }}"
shell = "echo {{ subprocess.run('echo foo | tr a-z A-Z', shell=True, capture_output=True).stdout.decode().strip() }}"
```

```shell
dev env_vars
# PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin PWD=/Users/username/Projects HOME=/Users/username

dev shell
# FOO
```

These constraints actually have the benefit of making your `dev` scripts more cross-platform compatible, as they do not
rely on any shell-specific syntax (unless you use the `subprocess` workaround, as in the example above). This means your
scripts should work on Windows, Linux, and macOS.

Also, it's worth pointing out that the `shell` example above would be better written as a Python script, rather than a
`dev` script in your `pyproject.toml` file:

```python
# scripts/shell.py
import subprocess

def main() -> str:
    return subprocess.run('echo foo | tr a-z A-Z', shell=True, capture_output=True).stdout.decode().strip()

if __name__ == '__main__':
    output: str = main()
    print(output)
```

Then, you could reference it in your script definition:

```toml
[tool.python-dev-cli.scripts]
shell = "python -m scripts.shell"
```

This is a better design pattern, as it keeps your Python logic in a Python file rather than a TOML file, where it cannot
be easily tested or linted.

### Script Names

Script names must be valid Python identifiers, which means they must start with a letter or underscore (`_`), and can
only contain letters, numbers, and underscores (`_`).  This is because script names are used as attribute names on the
`dev` object, which means they must be valid Python identifiers.

Also, keep in mind that any scripts prefixed with an underscore (`_`) will be hidden from the help page and cannot be
run directly. Think of these as "private" script variables, which can only be referenced by other scripts.

## License

This open source project is licensed under the terms of the [BSD 3-Clause License].

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md] for details.

### Code of Conduct

This project has adopted the [Contributor Covenant]. For more information, see the [Code of Conduct]
page.


[BSD 3-Clause License]: https://github.com/sscovil/devblob/master/LICENSE
[Code of Conduct]: https://github.com/sscovil/devblob/master/CODE_OF_CONDUCT.md
[CONTRIBUTING.md]: https://github.com/sscovil/devblob/master/CONTRIBUTING.md
[Contributor Covenant]: https://contributor-covenant.org/
[Jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
[pyproject.toml]: https://peps.python.org/pep-0518/#tool-table
[subprocess.run()]: https://docs.python.org/3/library/subprocess.html#subprocess.run
