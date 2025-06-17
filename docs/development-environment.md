# Apio Developer Environment

## Fork the Apio Repository

The first step in developing for Apio is to fork the [Apio repository](https://github.com/FPGAwars/apio). This will allow you to run the GitHub test workflow before submitting your pull request. In the rest of this document, we assume that you have forked the Apio repository and cloned it locally on your computer.

## Run Your Cloned Apio

The easiest way to develop Apio is to install its source code from your local repo as the Pip `apio` package. This will allow you to test your edited code by running `apio` from the command line.

To install the Apio source code as the Pip `apio` package, run these commands in the root directory of the Apio repository:

```
# In case apio is installed
pip uninstall apio

# Install the repo as the Pip `apio` package.
pip install -e .

# Confirm Apio 'Apio Python package' directory.
apio info system
```

## Test Changes Locally

Before creating a commit, test your code locally by running this in the repo root directory:

```shell
make check
```

During debugging, it is sometimes useful to run quick partial tests before running `make check`. Here are some examples:

```shell
# Run linters only
make lint

# Run offline tests only. These are tests that don't fetch remote Apio packages.
make test

# Run a single test file with verbose info
pytest -vv -s test/managers/test_project.py

# Run a single test with verbose info
pytest -vv -s test/managers/test_project.py::test_first_env_is_default
```

> The page `_pytest-coverage/index.html` shows the coverage of the last test run. The directory `_pytest-coverage` is transient and is ignored by git.

## Confirm Test Workflow Passes

Once you are ready to send a pull request from your forked repository, make sure that the test workflow completed successfully. You can find it in the Actions tab of your forked repo.

> The test workflow tests the `develop` branch, so if you worked on your own branch, merge it with `develop` first.

## Using `APIO_DEBUG` to Print Debug Information

If the environment variable `APIO_DEBUG` is defined (regardless of its value), Apio emits internal debugging information that may be useful for debugging.

```
# Linux and Mac OSX
export APIO_DEBUG=

# Windows
set APIO_DEBUG=
```

## Debugging with Visual Studio Code

The `.vscode/launch.json` file contains debugging targets for the Visual Studio Code (VSC) debugger. To use them, make sure that you open the Apio project at its root directory and select the desired VSC debugging target. To customize the targets for your specific needs, click on the Settings icon (wheel) near the debugging target and edit its definition in `launch.json` (do not submit changes to `launch.json` unless they will benefit other developers).

Since Apio launches Scons as a subprocess, **debugging the Scons code requires a different approach** using these steps:

1. Set the environment variable `APIO_SCONS_DEBUGGER` to cause Scons to wait for the debugger (in `apio/scons/SConstruct`).
2. Set your desired breakpoints in the Scons part of Apio.
3. From the command line, run the Apio command that invokes the Scons subprocess (e.g., `apio build`).
4. In the VSC debugger, start the target `Attach remote debugger`.

## Override Remote Config for Testing

Apio retrieves its package information from a remote config `.jsonc` file whose URL is stored in `api/resources/config.jsonc`. For testing, it may be useful to override it and point to an alternative config file. This can be done by defining the `APIO_REMOTE_CONFIG_URL` variable.

Examples:

```
export APIO_REMOTE_CONFIG_URL="https://github.com/FPGAwars/apio/raw/develop/remote-config/apio-{V}.jsonc"

export APIO_REMOTE_CONFIG_URL="file:///projects/apio-dev/repo/remote-config/apio-{V}.jsonc"

export APIO_REMOTE_CONFIG_URL="file:///tmp/my-config-file.jsonc"
```
