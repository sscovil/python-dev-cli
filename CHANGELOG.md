# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to
[Semantic Versioning](http://semver.org/).

## [1.0.5] - 2023-09-25

### Fixed

- GitHub Action `publish` workflow missing build step

## [1.0.4] - 2023-09-25

### Added

- Separate tests into a different GitHub Actions workflow, for running tests on pull requests

### Changed

- Modify `publish` GitHub Actions workflow to only run on release, using PyPI trusted publishing
- Modify `test` GitHub Actions workflow to test multiple operating systems and Python versions
- Modify `Scripts.run_script()` to not raise a `FileNotFoundError` if the script does not exist; instead, allow
  `subprocess.run()` to raise a `CalledProcessError` if the script command fails to run.

### Fixed

- Add `_version.py` to `.gitignore` ensure `setuptools_scm` updates that file correctly

## [1.0.3] - 2023-09-24

### Fixed

- Tag commit for release, to ensure `setuptools_scm` does not append `.dev` suffix to version

## [1.0.2] - 2023-09-24

### Fixed

- Issue with `_version.py` causing lint to fail during GitHub Actions publish workflow

## [1.0.1] - 2023-09-24

### Added

- Build system requirements: `setuptools_scm[toml] >=8.0`, `wheel`
- Dynamic version using [setuptools_scm](https://pypi.org/project/setuptools-scm/)
- Version specifiers for dependencies and dev dependencies
- GitHub Actions publish workflow, triggered when release is published

### Changed

- Added dynamic badges to `README.md`
- Updated `CONTRIBUTING.md` instructions for setting up local development environment

### Removed

- Static version in `pyproject.toml`
- Optional dev dependency: `pip-tools`
- Superfluous `requirements.txt` and `requirements-dev.txt` files
- Dev scripts for `pip-compile` and `pip-sync` commands

## [1.0.0] - 2023-09-23

### Added

- Initial release (v1.0.0)
