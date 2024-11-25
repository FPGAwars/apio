"""
Pytest
TEST configuration file
"""

from pathlib import Path
from typing import Tuple
from typing import Dict
import os

import pytest

# -- Class for executing click commands
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.CliRunner
from click.testing import CliRunner

# -- Class for storing the results of executing a click command
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.Result
from click.testing import Result

# -- Debug mode on/off
DEBUG = True

# -- Apio should be able to handle spaces and unicode in its home, packages,
# -- and project directory path. We insert this marker in the test pathes to
# -- test it.
#
# -- TODO: Currently apio doesn't handle well spaces in the pathes. Fix it and
# -- change this to " fuññy ". For more details see
# -- https://github.com/FPGAwars/apio/issues/474.
FUNNY_MARKER = "fuññy"


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


class ApioRunner:
    """Apio commands test helper. An object of this class is provided to the
    tests via the apio_runner fixture and a typical tests looks like this:

    def test_my_cmd(apio_runner):
        with apio_runner.isolated_filesystem():

           apio_runner.setup_env()

           <the test body>
    """

    def __init__(self, request):
        # -- A CliRunner instance that is used for creating temp directories
        # -- and to invoke apio commands.
        self._request = request
        self._click_runner = CliRunner()

        # -- Save the original system path so we can restore it before each
        # -- invocation since some apio commands mutate it and pytest runs
        # -- multiple apio command in the same python process.
        self._original_path = os.environ["PATH"]

        # -- Set later by set_env().
        self._proj_dir: Path = None
        self._home_dir: Path = None
        self._packages_dir: Path = None

    def in_disposable_temp_dir(self):
        """Returns a context manager which creates a temp directory upon
        entering it and deleting it upon existing."""
        return self._click_runner.isolated_filesystem()

    def setup_env(self) -> Tuple[Path, Path, Path]:
        """Should be called by the test within the 'in_disposable_temp_dir'
        scope to set up the apio specific environment."""
        # -- Current directory is the root test dir. Should be empty.
        test_dir = Path.cwd()
        assert not os.listdir(test_dir)

        # -- Using unicode and space to verify that they are handled correctly.
        funny_dir = test_dir / FUNNY_MARKER
        funny_dir.mkdir(parents=False, exist_ok=False)

        # -- Apio dirs
        self._proj_dir = funny_dir / "proj"
        self._home_dir = funny_dir / "apio"
        self._packages_dir = funny_dir / "packages"

        if DEBUG:
            print("")
            print("  --> apio_runner.setup_env():")
            print(f"       test dir          : {str(test_dir)}")
            print(f"       apio proj dir     : {str(self._proj_dir)}")
            print(f"       apio home dir     : {str(self._home_dir)}")
            print(f"       apio packages dir : {str(self._packages_dir)}")

        # -- Apio dirs do not exist yet.
        assert not self._proj_dir.exists()
        assert not self._home_dir.exists()
        assert not self._packages_dir.exists()

        # -- TODO: This looks like a flag. Describe what it do.
        os.environ["TESTING"] = ""

        # -- All done, return the values.
        return (
            self._proj_dir,
            self._home_dir,
            self._packages_dir,
        )

    # R0913: Too many arguments (7/5) (too-many-arguments)
    # pylint: disable=R0913
    # W0622: Redefining built-in 'input' (redefined-builtin)
    # pylint: disable=W0622
    # R0917: Too many positional arguments (7/5)
    # pylint: disable=R0917
    def invoke(
        self,
        cli,
        args=None,
        input=None,
        env=None,
        catch_exceptions=True,
        color=False,
        **extra,
    ):
        """Invoke an apio command."""

        # -- Restore the original path, since some apio commands mutate it and
        # -- pytest runs multiple commands in the same python process.
        os.environ["PATH"] = self._original_path

        # -- This typically fails if the test did not call setup_env() before4
        # -- invoking a command.
        assert FUNNY_MARKER in str(self._home_dir)
        assert FUNNY_MARKER in str(self._packages_dir)

        # -- Set the env to infrom the apio command where are the apio test
        # -- home and packages dir are.
        os.environ["APIO_HOME_DIR"] = str(self._home_dir)
        os.environ["APIO_PACKAGES_DIR"] = str(self._packages_dir)

        # -- Double check.
        assert FUNNY_MARKER in os.environ["APIO_HOME_DIR"]
        assert FUNNY_MARKER in os.environ["APIO_PACKAGES_DIR"]

        # -- Invoke the command. Get back the collected results.
        result = self._click_runner.invoke(
            cli=cli,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )

        return result

    def assert_ok(self, result: Result):
        """Check if apio command results where ok"""

        # -- It should return an exit code of 0: success
        assert result.exit_code == 0, result.output

        # -- There should be no exceptions raised
        assert not result.exception

        # -- The word 'error' should NOT appear on the standard output
        assert "error" not in result.output.lower()

    def write_apio_ini(self, properties: Dict[str, str]):
        """Write in the current directory an apio.ini file with given
        values. If an apio.ini file alread exists, it is overwritten.
        if properties is None and an apio.ini file exists, it is deleted."""

        path = Path("apio.ini")

        if properties is None:
            path.unlink(missing_ok=True)
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write("[env]\n")
            for name, value in properties.items():
                f.write(f"{name} = {value}\n")

    @property
    def offline_flag(self) -> bool:
        """Returns True if pytest was invoked with --offline to skip
        tests that require internet connectivity and are slower in general."""
        return self._request.config.getoption("--offline")


@pytest.fixture(scope="session")
def apio_runner(request):
    """A pytest fixture that provides tests with a ApioRunner test
    helper object."""
    return ApioRunner(request)
