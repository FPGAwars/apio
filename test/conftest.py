"""
Pytest
TEST configuration file
"""

# os.environ: Access to environment variables
#   https://docs.python.org/3/library/os.html#os.environ
from os import environ, listdir
from pathlib import Path
from typing import Dict

import pytest

# -- Class for executing click commands
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.CliRunner
from click.testing import CliRunner

# -- Class for storing the results of executing a click command
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.Result
from click.testing import Result

# -- Debug mode on/off
DEBUG = True


@pytest.fixture(scope="module")
def click_cmd_runner():
    """A pytest fixture that provides tests with a click commands runner."""
    return CliRunner()


@pytest.fixture(scope="session")
def setup_apio_test_env():
    """An pytest fixture that provides tests with a function to set up the
    apio test environment. By default, the tests run in a temporaly folder
    (in /tmp/xxxxx).
    """

    def decorator():
        # -- Current directory is the project dir.
        project_dir = Path.cwd()

        # -- Set a strange directory for executing
        # -- apio: it contains spaces and unicode characters
        # -- for testing. It should work
        apio_home_dir = project_dir / " ñ"
        apio_packages_dir = apio_home_dir / "packages"

        # -- Debug
        if DEBUG:
            print("")
            print("  --> setup_apio_test_env():")
            print(f"     apio project dir  : {str(project_dir)}")
            print(f"     apio home dir     : {str(apio_home_dir)}")
            print(f"     apio packages dir : {str(apio_packages_dir)}")

        # -- Since the test run in a fresh temp directory, we expect it to be
        # -- empty with no left over files (such as apio.ini) from a previous
        # -- tests.
        project_dir_content = listdir(".")
        assert not project_dir_content, project_dir_content

        # -- Set the apio home dir and apio packages dir to
        # -- this test folder
        environ["APIO_HOME_DIR"] = str(apio_home_dir)
        environ["APIO_PACKAGES_DIR"] = str(apio_packages_dir)
        environ["TESTING"] = ""

    return decorator


@pytest.fixture(scope="session")
def assert_apio_cmd_ok():
    """A pytest fixture that provides a function to assert that apio click
    command result were ok.
    """

    def decorator(result: Result):
        """Check if the result is ok"""

        # -- It should return an exit code of 0: success
        assert result.exit_code == 0, result.output

        # -- There should be no exceptions raised
        assert not result.exception

        # -- The word 'error' should NOT appear on the standard output
        assert "error" not in result.output.lower()

    return decorator


@pytest.fixture(scope="session")
def write_apio_ini():
    """A pytest fixture to write a project apio.ini file. If properties
    is Nonethe file apio.ini is deleted if it exists.
    """

    def decorator(properties: Dict[str, str]):
        """The apio.ini actual writer"""

        path = Path("apio.ini")

        if properties is None:
            path.unlink(missing_ok=True)
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write("[env]\n")
            for name, value in properties.items():
                f.write(f"{name} = {value}\n")

    return decorator


# -- This function is called by pytest. It addes the pytest --offline flag
# -- which is is passed to tests that ask for it using the fixture
# -- 'offline_flag' below.
# --
# -- More info: https://docs.pytest.org/en/7.1.x/example/simple.html
def pytest_addoption(parser: pytest.Parser):
    """Register the --offline command line option when invoking pytest"""

    # -- Option: --offline
    # -- It is used by the function test that requieres
    # -- internet connnection for testing
    parser.addoption(
        "--offline", action="store_true", help="Run tests in offline mode"
    )


@pytest.fixture
def offline_flag(request):
    """Return the value of the pytest '--offline' flag register above.
    This flag can be set by the user when invoking pytest to disable
    test functionality that requires internet connectivity.
    """
    return request.config.getoption("--offline")
