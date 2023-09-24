<!-- omit in toc -->
# Contributing to Python Developer CLI

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the [Table of Contents] for different ways to help and details
about how this project handles them. Please make sure to read the relevant section before making your contribution. It
will make it a lot easier for us maintainers and smooth out the experience for all involved. The community looks forward
to your contributions. 🎉

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support
the project and show your appreciation, which we would also be very happy about:
> - Star the project
> - Tweet about it
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues

<!-- omit in toc -->
## Table of Contents

- [Code of Conduct]
- [I Have a Question]
- [I Want To Contribute]
    - [Reporting Bugs]
    - [Suggesting Enhancements]
    - [Your First Code Contribution]
    - [Improving The Documentation]
- [Styleguide]
    - [Commit Messages]

## Code of Conduct

This project and everyone participating in it is governed by the [Python Developer CLI Code of Conduct]. By
participating, you are expected to uphold this code. Please report unacceptable behavior to <report@pythondevcli.io>.

## I Have a Question

> If you want to ask a question, we assume that you have read the available [documentation].

Before you ask a question, it is best to search for existing [issues] that might help you. In case you have found a
suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search
the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [issue].
- Provide as much context as you can about what you're running into.
- Provide project and platform versions, depending on what seems relevant.

We will then take care of the issue as soon as possible.

## I Want To Contribute

<!-- omit in toc -->
> ### Legal Notice
> When contributing to this project, you must agree that you have authored 100% of the content, that you have the
necessary rights to the content and that the content you contribute may be provided under the project license.

### Reporting Bugs

<!-- omit in toc -->
#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to
investigate carefully, collect information and describe the issue in detail in your report. Please complete the
following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment
components/versions (Make sure that you have read the [documentation]. If you are looking for support, you might want to
check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there
is not already a bug report existing for your bug or error in the [bug tracker].
- Also make sure to search the internet (including Stack Overflow) to see if users outside the GitHub community have
discussed the issue.
- Collect information about the bug:
    - Stack trace (Traceback)
    - OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
    - Version of the interpreter, compiler, SDK, runtime environment, package manager, depending on what seems relevant.
    - Possibly your input and the output
    - Can you reliably reproduce the issue? And can you also reproduce it with older versions?

<!-- omit in toc -->
#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including sensitive information to the issue
> tracker, or elsewhere in public. Instead, sensitive bugs must be sent by email to <report@pythondevcli.io>.
<!-- TODO: Add a PGP key to allow the messages to be sent encrypted. -->

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [issue]. Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug
yet and not to label the issue.
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to
recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem
and create a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed:

- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there are no reproduction steps or no
obvious way to reproduce the issue, the team will ask you for those steps and mark the issue as `needs-repro`. Bugs with
the `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be marked `needs-fix`, as well as possibly other tags (such as
`critical`), and the issue will be left to be [implemented by someone].

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Python Developer CLI, **including completely
new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and
the community to understand your suggestion and find related suggestions.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation] carefully and find out if the functionality is already covered, maybe by an individual
configuration.
- Search [Discussions] to see if the enhancement has already been suggested. If it has, add a comment to the existing
issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to
convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful
to the majority of our users and not just a small subset. If you're just targeting a minority of users, consider writing
an add-on/plugin library.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as GitHub [Discussions].

- Use a **clear and descriptive title** to identify your suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point
you can also tell which alternatives do not work for you.
- **Explain why this enhancement would be useful** to most Python Developer CLI users. You may also want to point out
the other projects that solved it better and which could serve as inspiration.

### Your First Code Contribution

This project uses the [GitHub flow] branching model. To contribute a change, you should create a new branch from the
`main` branch, make your changes, and then open a pull request. The pull request will be reviewed by a maintainer, and
merged into the `main` branch if it is accepted.

- All pull requests must be tied to one of the existing [issues]. If there is no existing issue, please open one first
  to discuss your proposed change.
- All pull requests must be made against the `main` branch. Pull requests made against other branches will be closed
  without merging.

To get started, you'll need to clone the git repository and set up your local development environment:

1. Clone the git repository: `git clone git@github.com:sscovil/python-dev-cli.git`
2. Change to the project directory: `cd python-dev-cli`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate` (or `venv\Scripts\activate.bat` on Windows)
5. Install dev dependencies: `pip install -e ".[dev]"`
6. Install git pre-commit hooks: `pre-commit install`
7. View available scripts: `dev -h`

This project uses the `pyproject.toml` file to manage dependencies. Generally, you should avoid adding new dependencies
to the project, but if it is necessary you should add them to the `pyproject.toml` file and then run `dev install`.

### Improving The Documentation

To contribute to the [documentation], please read it carefully and make sure that you understand it. Then you can make
your changes in the `README.md` file and submit a pull request.

## Styleguide

This repository uses [Black] to format Python code, and [Ruff] for linting. You can run both of these tools with the
following command:

```shell
python -m src.python_dev_cli.cli lint_fix
```

You should also run `pre-commit install` to install the pre-commit hooks, which will run the linter and formatter before
each git commit.

### Commit Messages

This repository uses [Conventional Commits] for commit messages. Please follow the [Conventional Commits] specification
when writing commit messages.

You should also run `pre-commit install` to install the pre-commit hooks, which will validate the commit message before
each git commit.

## Attribution

This guide is based on the **contributing-gen**. [Make your own](https://github.com/bttger/contributing-gen)!


[Black]: https://black.readthedocs.io/en/stable/the_black_code_style/index.html
[bug tracker]: https://github.com/sscovil/devissues?q=label%3Abug
[Code of Conduct]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#code-of-conduct
[Commit Messages]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#commit-messages
[Conventional Commits]: https://www.conventionalcommits.org/en/v1.0.0/
[Discussions]: https://github.com/sscovil/python-dev-cli/discussions
[documentation]: https://github.com/sscovil/python-dev-cli/blob/main/README.md
[GitHub flow]: https://docs.github.com/en/get-started/quickstart/github-flow
[I Have a Question]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#i-have-a-question
[I Want To Contribute]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#i-want-to-contribute
[implemented by someone]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#your-first-code-contribution
[Improving The Documentation]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#improving-the-documentation
[issue]: https://github.com/sscovil/python-dev-cli/issues/new
[issues]: https://github.com/sscovil/python-dev-cli/issues
[pip-tools]: https://github.com/jazzband/pip-tools
[Python Developer CLI Code of Conduct]: https://github.com/sscovil/devblob/master/CODE_OF_CONDUCT.md
[Reporting Bugs]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#reporting-bugs
[Ruff]: https://docs.astral.sh/ruff/
[Table of Contents]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#table-of-contents
[Styleguide]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#styleguide
[Suggesting Enhancements]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#suggesting-enhancements
[Your First Code Contribution]: https://github.com/sscovil/python-dev-cli/blob/main/CONTRIBUTING.md#your-first-code-contribution
