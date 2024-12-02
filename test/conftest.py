"""
Pytest
TEST configuration file
"""

import shutil
import tempfile
import contextlib
from pathlib import Path
from typing import List, Union, cast, Optional
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


class ApioSandbox:
    """Accessor for sandbox values. Available to the user inside an
    ApioRunner sandbox scope."""

    def __init__(
        self,
        apio_runner_: "ApioRunner",
        proj_dir: Path,
        home_dir: Path,
        packages_dir: Path,
    ):
        self._apio_runner = apio_runner_
        self._proj_dir = proj_dir
        self._home_dir = home_dir
        self._packages_dir = packages_dir
        self._click_runner = CliRunner()

    @property
    def expired(self) -> bool:
        """Returns true if this sandbox was expired."""
        # -- This tests if this sandbox is still the active sandbox at the
        # -- apio runner that creates it.
        return self is not self._apio_runner.sandbox

    @property
    def proj_dir(self) -> Path:
        """Returns the sandbox's apio project dir."""
        assert not self.expired, "Sanbox expired"
        return self._proj_dir

    @property
    def home_dir(self) -> Path:
        """Returns the sandbox's apio home dir."""
        assert not self.expired, "Sanbox expired"
        return self._home_dir

    @property
    def packages_dir(self) -> Path:
        """Returns the sandbox's apio packages dir."""
        assert not self.expired, "Sanbox expired"
        return self._packages_dir

    # R0913: Too many arguments (7/5) (too-many-arguments)
    # pylint: disable=R0913
    # W0622: Redefining built-in 'input' (redefined-builtin)
    # pylint: disable=W0622
    # R0917: Too many positional arguments (7/5)
    # pylint: disable=R0917
    def invoke_apio_cmd(
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

        print(f"\nInvoking apio command [{cli.name}], args={args}.")

        # -- Check that this sandbox is still alive.
        assert not self.expired, "Sandbox expired."

        # -- Since we restore the env after invoking the apio command, we
        # -- don't expect path changes by the command to survive here.
        assert FUNNY_MARKER not in os.environ["PATH"]

        # -- Take a snapshot of the system env.
        original_env = os.environ.copy()

        # -- These two env vars are set when creating the context. Let's
        # -- check that the test didn't corrupt them.
        assert os.environ["APIO_HOME_DIR"] == str(self.home_dir)
        assert os.environ["APIO_PACKAGES_DIR"] == str(self.packages_dir)

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

        # -- Restore system env. Since apio commands tend to change vars
        # -- such as PATH.
        self.set_system_env(original_env)

        return result

    def assert_ok(self, result: Result):
        """Check if apio command results where ok"""

        # -- It should return an exit code of 0: success
        assert result.exit_code == 0, result.output

        # -- There should be no exceptions raised
        assert not result.exception

        # -- The word 'error' should NOT appear on the standard output
        assert "error" not in result.output.lower()

    def set_system_env(self, new_vars: Dict[str, str]) -> None:
        """Overwirte the existing sys.environ with the given dirct. Vars
        that are not in the dict are deleted and vars that have a different
        value in the dict is updated.  Can be called only within a
        an apio sandbox."""

        # -- Check that the sandox not expired.
        assert not self.expired, "Sandox expired"

        # -- NOTE: naivly assining the dict to os.environ will break
        # -- os.environ since a simple dict doesn't update the underlying
        # -- system env when it's mutated.

        print("\nRestoring os.environ:")

        # -- Construct the union of the env and the dict var names.
        all_var_names = set(os.environ.keys()).union(new_vars.keys())
        for name in all_var_names:
            # Get the env and dict values. None if doesn't exist.
            env_val = os.environ.get(name, None)
            dict_val = new_vars.get(name, None)
            # -- If values are not the same, update the env.
            if env_val != dict_val:
                print(f"  set ${name}={dict_val}  (was {env_val})")
                if dict_val is None:
                    os.environ.pop(name)
                else:
                    os.environ[name] = dict_val

        # -- Sanity check. System env and the dict should be the same.
        assert os.environ == new_vars

    def write_file(
        self,
        file: Union[str, Path],
        text: Union[str, List[str]],
        exists_ok=False,
    ) -> None:
        """Write text to given file. If text is a list, items are joined with
        "\n". 'file' can be a string or a Path."""

        assert exists_ok or not Path(file).exists(), f"File exists: {file}"

        # -- If a list is given, join with '\n"
        if isinstance(text, list):
            text = "\n".join(text)

        # -- Write.
        with open(file, "w", encoding="utf-8") as f:
            f.write(text)

    def read_file(
        self, file: Union[str, Path], lines_mode=False
    ) -> Union[str, List[str]]:
        """Read a text file. Returns a string with the text or if
        lines_mode is True, a list with the individual lines (excluding
        the \n delimiters)
        """

        # -- Read the text.
        with open(file, "r", encoding="utf8") as f:
            text = f.read()

        # -- Split to lines if requested.
        if lines_mode:
            text = text.split("\n")

        # -- All done
        return text

    def write_apio_ini(self, properties: Dict[str, str]):
        """Write in the current directory an apio.ini file with given
        values. If an apio.ini file alread exists, it is overwritten."""

        path = Path("apio.ini")

        # -- Handle a deletion request.
        if properties is None:
            properties = {"board": "icezum", "top-module": "main"}

        # -- Requested to write. Construct the lines.
        lines = ["[env]"]
        for name, value in properties.items():
            lines.append(f"{name} = {value}")

        # -- Write the file.
        self.write_file(path, lines)

    @property
    def offline_flag(self):
        """Returns True if pytest was invoked with --offline to skip
        tests that require internet connectivity and are slower in general."""
        assert not self.expired, "Trying to use an expired sandbox"
        return self._apio_runner.offline_flag


class ApioRunner:
    """Apio commands test helper. Provides an apio sandbox functionality
    (disposable temp dirs and sys.environ restoration) as well as a few
    utility functions. A typical test with the ApiRunner looks like this:

    def test_my_cmd(apio_runner):
        with apio_runner.in_sandbox() as sb:

           <the test body>
    """

    def __init__(self, request):
        # -- A CliRunner instance that is used for creating temp directories
        # -- and to invoke apio commands.
        self._request = request

        # -- Indicate that we are not in a sandbox
        self._sandbox: ApioSandbox = None

    @property
    def sandbox(self) -> Optional[ApioSandbox]:
        """Returns the sandbox object or None if not in a sandbox."""
        return self._sandbox

    @contextlib.contextmanager
    def in_sandbox(self):
        """Create an apio sandbox context manager that delete the temp dir
        and restore the system env upon exist. A typical invocation is

        with apio_runner.in_sandbox() as sb:

           ...
        """
        # -- Make sure we don't try to nest sandboxes.
        assert self._sandbox is None, "Already in a sandbox."

        # -- Snatpshot the system env.
        original_env: Dict[str, str] = os.environ.copy()

        # -- Snapshot the current directory.
        original_cwd = os.getcwd()

        # -- Create a temp dir that will be deleted on exit and change to it.
        temp_dir = Path(tempfile.mkdtemp(prefix=FUNNY_MARKER + "-"))
        os.chdir(temp_dir)

        # -- Construct the sandbox dir pathes. User will create the dirs
        # -- as needed.
        proj_dir = temp_dir / "proj"
        home_dir = temp_dir / "apio"
        packages_dir = temp_dir / "packages"

        if DEBUG:
            print()
            print("--> apio sandbox:")
            print(f"       test dir          : {str(temp_dir)}")
            print(f"       apio proj dir     : {str(proj_dir)}")
            print(f"       apio home dir     : {str(home_dir)}")
            print(f"       apio packages dir : {str(packages_dir)}")
            print()

        # -- Register a sanbox objet to indicate that we are in a sandbox.
        assert self._sandbox is None
        self._sandbox = ApioSandbox(self, proj_dir, home_dir, packages_dir)

        # -- Set the system env vars to inform ApioContext what are the
        # -- home and packages dirs.
        os.environ["APIO_HOME_DIR"] = str(home_dir)
        os.environ["APIO_PACKAGES_DIR"] = str(packages_dir)

        try:
            # -- This is the end of the context manager _entry part. The
            # -- call to _exit will continue execution after the yeield.
            # -- Value is the sandox object we pass to the user.
            yield cast(ApioSandbox, self._sandbox)

        finally:
            # -- Here when the context manager exit, normally or through an
            # -- exception.

            # -- Restore the original system env.
            self._sandbox.set_system_env(original_env)

            # -- Mark that we exited the sanbox. This expires the sandbox.
            self._sandbox = None

            # -- Change back to the original directory.
            os.chdir(original_cwd)

            # -- Delete the temp directory.
            shutil.rmtree(temp_dir)

            print("\nSandbox deleted. ")

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
