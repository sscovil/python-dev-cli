# Python Developer CLI

![PyPI - Version](https://img.shields.io/pypi/v/python-dev-cli)
![PyPI - License](https://img.shields.io/pypi/l/python-dev-cli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-dev-cli)
![GitHub issues](https://img.shields.io/github/issues/sscovil/python-dev-cli?link=https%3A%2F%2Fgithub.com%2Fsscovil%2Fpython-dev-cli%2Fissues)
![GitHub issues by-label](https://img.shields.io/github/issues/sscovil/python-dev-cli/bug?link=https%3A%2F%2Fgithub.com%2Fsscovil%2Fpython-dev-cli%2Flabels%2Fbug)

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
# pyproject.toml
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
# pyproject.toml
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
# pyproject.toml
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
# pyproject.toml
[tool.python-dev-cli.settings]
include = ["uuid:uuid4 as uuid"]

[tool.python-dev-cli.scripts]
python = "echo {{ 1 + 1 }}"
module = "echo {{ uuid() }}"
other_scripts = "echo {{ dev._foo }}{{ dev._bar }}"
_foo = "foo"
_bar = "bar"
```

```shell
dev python
# 2

dev module
# 2b2e0b9e-0b9e-4a4a-9a9a-9a9a9a9a9a9a

dev other_scripts
# foobar
```

Script template functionality can be disabled, if you prefer to keep things simple. See the [Settings] section below for
more information.

## Settings

You can configure this package by adding a `tool.python-dev-cli.settings` section to your `pyproject.toml` file (default
values shown):

```toml
# pyproject.toml
[tool.python-dev-cli.settings]
enable_templates = true
parse_help = true
include = []
script_refs = "dev"
```

### enable_templates

Enable or disable the use of [Jinja2] templates in your scripts. If you disable this, all other settings will be ignored
and scripts will be run as-is, without any preprocessing.

> **NOTE:** Disabling this setting will prevent you from referencing other scripts from within a script, but you will
> still be able to reference other scripts in a list of scripts.

For example, this will still work:

```toml
# pyproject.toml
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
# pyproject.toml
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

### parse_help

Enable or disable the parsing of script templates in the `dev` CLI help page. If you disable this, the help page will
show the raw script template, rather than the parsed script command.

```toml
# pyproject.toml
[tool.python-dev-cli.settings]
parse_help = false

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
#     foobar              ['echo {{ dev._foo }}{{ dev._bar }}']
```

### include

A list of modules to include in the [Jinja2] environment, when parsing scripts. This enables you to reference Python
modules in your scripts:

```toml
# pyproject.toml
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
# pyproject.toml
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
# pyproject.toml
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
run in. As a result, shell features such as pipes `|`; filename wildcards `*`; redirects `>`, `>>`, `<`; backgrounding
`&`; and expansion of `~` to a user's home directory are not supported.

> **NOTE:** Environment variables can still be referenced as you would in a shell script (e.g. `$HOME` or `${HOME}`),
> because the `dev` CLI uses [os.path.expandvars()] when resolving scripts.

To work around this limitation, you can use the `subprocess` module to run shell commands with the `shell=True` flag:

```toml
# pyproject.toml
[tool.python-dev-cli.settings]
include = ["subprocess"]

[tool.python-dev-cli.scripts]
shell = "echo {{ subprocess.run('echo foo | tr a-z A-Z', shell=True, capture_output=True).stdout.decode().strip() }}"
```

```shell
dev shell
# FOO
```

However, by not running scripts with the `shell=True` flag, the `dev` CLI has the benefit of making your scripts more
cross-platform compatible, as they do not rely on any shell-specific syntax. This means your scripts will typically work
on Windows, Linux, and macOS (unless you do something like in the example above).

Also, it's worth pointing out that the example above would be better written as a Python script, rather than a `dev`
script in your `pyproject.toml` file:

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
# pyproject.toml
[tool.python-dev-cli.scripts]
shell = "python -m scripts.shell"
```

This is a better design pattern, as it keeps your Python logic in a Python file rather than a TOML file, where it cannot
be easily tested or linted.

An even better approach would be to use the various Python implementations of shell-like features (e.g. [glob],
[fnmatch], [os.walk()], [os.path.expanduser()], and [shutil]) to achieve the desired result, rather than calling
out to a shell command.

### Script Names

Script names must be valid Python identifiers, which means they must start with a letter or underscore (`_`), and can
only contain letters, numbers, and underscores (`_`).  This is because script names are used as attribute names on the
`dev` object, which means they must be valid Python identifiers.

Also, keep in mind that any scripts prefixed with an underscore (`_`) will be hidden from the help page and cannot be
run directly. Think of these as "private" script variables, which can only be referenced by other scripts.

### Template Parsing

By default, script templates are parsed using [Jinja2] before being run. They are also parsed whenever the `dev` CLI
help page is displayed, to generate examples of the actual commands that will be run for each script. This means that
any function calls or other Python syntax in your scripts will be evaluated **even when a script is not being run**
(potentially multiple times, depending on your configuration). This is important to understand, because it could have
unintended consequences.

For example, let's say you have one script that generates a random UUID and another script that runs the first script
three times:

```toml
# pyproject.toml
[tool.python-dev-cli.settings]
include = ["uuid:uuid4 as uuid"]

[tool.python-dev-cli.scripts]
uuid = "echo {{ uuid() }}"
uuids = ["uuid", "uuid", "uuid"]
```

When you run `dev uuids`, the `uuid()` function gets called three times, generating three unique IDs as expected.

```shell
dev uuids
# affa5cf5-8d1d-43c6-806f-c561d91f7d05
# d8dd276d-1cc8-4dcf-9e0d-6f3fcbdbcc22
# ac5a0a59-4510-4609-9734-7c238652f59a
```

When you run `dev --help`, the same thing happens, this time to generate the help page examples:

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
#   {uuid,uuids}
#     uuid                ['echo 2afa5b31-159c-45e5-b7e3-ad935a48cef0']
#     uuids               ['echo 2c7fe6e2-01a0-4cd9-90fe-50816a2ed316', 'echo 51ca85c8-b69b-4151-ab3f-5bf2a148a058', 'echo 6595e224-3e24-463c-9cc4-98c9bf0ecddb']
```

Now, consider the following scripts that make API calls to a third-party service:

```toml
# pyproject.toml
[tool.python-dev-cli.settings]
include = ["json", "requests"]

[tool.python-dev-cli.scripts]
curl = "curl https://cat-fact.herokuapp.com/facts/random?amount=1"
req = "echo {{ json.loads(requests.get('https://cat-fact.herokuapp.com/facts/random?amount=1').content).text }}"
```

When you run `dev curl`, the API call is made as expected:

```shell
 dev curl
# {"status":{"verified":true,"sentCount":1},"_id":"591f98783b90f7150a19c1c5","__v":0,"text":"Baking chocolate is the most dangerous chocolate to your cat.","source":"api","updatedAt":"2020-08-23T20:20:01.611Z","type":"cat","createdAt":"2018-04-17T20:20:02.627Z","deleted":false,"used":false,"user":"5a9ac18c7478810ea6c06381"}
```

When you run `dev req`, the API call is also made as expected:

```shell
dev req
# Cats are amazing animals.
```

When you run `dev --help`, the API call is made while parsing the `req` script template, even though the script is not
being run:

```shell
dev --help
# usage: dev [-h] [-d] {curl,req} ...
# Python developer CLI for running custom scripts defined in pyproject.toml
#
# options:
#   -h, --help            show this help message and exit
#   -d, --debug           enable debug logging
#
# available scripts:
#   {curl,req}
#     curl                ['curl https://cat-fact.herokuapp.com/facts/random?amount=1']
#     req                 ['echo When asked if her husband had any hobbies, Mary Todd Lincoln is said to have replied cats.']
```

If that were an API call that had a side effect, such as creating a new record in a database, then that side effect
would happen every time the `dev --help` command was run. This is probably not what you want.

To prevent this from happening, you can disable template parsing in the `dev` CLI help page by setting the `parse_help`
value to `false`:

```toml
# pyproject.toml
[tool.python-dev-cli.settings]
parse_help = false
```

However, a better solution in most cases would be to use the `curl` command, or move the API call to a Python script
that can be run using the `python -m` syntax:

```toml
# pyproject.toml
[tool.python-dev-cli.scripts]
req = "python -m scripts.req"
```

```python
# scripts/req.py
import json
import requests

def main() -> str:
    return json.loads(requests.get('https://cat-fact.herokuapp.com/facts/random?amount=1').content).text

if __name__ == '__main__':
    output: str = main()
    print(output)
```

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
[fnmatch]: https://docs.python.org/3/library/fnmatch.html#module-fnmatch
[glob]: https://docs.python.org/3/library/glob.html#module-glob
[Jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
[os.path.expanduser()]: https://docs.python.org/3/library/os.path.html#os.path.expanduser
[os.path.expandvars()]: https://docs.python.org/3/library/os.path.html#os.path.expandvars
[os.walk()]: https://docs.python.org/3/library/os.html#os.walk
[pyproject.toml]: https://peps.python.org/pep-0518/#tool-table
[Settings]: https://github.com/sscovil/python-dev-cli/blob/main/README.md#settings
[shutil]: https://docs.python.org/3/library/shutil.html#module-shutil
[subprocess.run()]: https://docs.python.org/3/library/subprocess.html#subprocess.run
