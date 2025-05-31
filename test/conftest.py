"""Pytest TEST configuration file"""

import sys
import subprocess
from subprocess import CompletedProcess
from dataclasses import dataclass
import shutil
import tempfile
import contextlib
from pathlib import Path
from typing import List, Union, cast, Optional
from typing import Dict, Any
import os
import pytest
from click.testing import CliRunner, Result
from apio import __main__
from apio.common import apio_console
from apio.common.proto.apio_pb2 import FORCE_PIPE, FORCE_TERMINAL


# -- Debug mode on/off
DEBUG = True

# -- This is the marker we use to identify the sandbox directories.
SANDBOX_MARKER = "apio-sandbox"


# -- This function is called by pytest. It adds the pytest --offline flag
# -- which is is passed to tests that ask for it using the fixture
# -- 'offline_flag' below.
# --
# -- More info: https://docs.pytest.org/en/7.1.x/example/simple.html
def pytest_addoption(parser: pytest.Parser):
    """Register the --offline command line option when invoking pytest"""

    # -- Option: --offline
    # -- It is used by the function test that requires
    # -- internet connection for testing
    parser.addoption(
        "--offline", action="store_true", help="Run tests in offline mode"
    )


@dataclass(frozen=True)
class ApioResult:
    """Represent the outcome of an apio invocation."""

    exit_code: int
    output: str  # stdout only
    exception: Any


class ApioSandbox:
    """Accessor for sandbox values. Available to the user inside an
    ApioRunner sandbox scope."""

    def __init__(
        self,
        apio_runner_: "ApioRunner",
        sandbox_dir: Path,
        proj_dir: Path,
        home_dir: Path,
    ):
        self._apio_runner = apio_runner_
        self._sandbox_dir = sandbox_dir
        self._proj_dir = proj_dir
        self._home_dir = home_dir
        self._click_runner = CliRunner()

    @property
    def expired(self) -> bool:
        """Returns true if this sandbox was expired."""
        # -- This tests if this sandbox is still the active sandbox at the
        # -- apio runner that creates it.
        return self is not self._apio_runner.sandbox

    @property
    def sandbox_dir(self) -> Path:
        """Returns the sandbox's dir."""
        assert not self.expired, "Sandbox expired"
        return self._sandbox_dir

    @property
    def proj_dir(self) -> Path:
        """Returns the sandbox's apio project dir."""
        assert not self.expired, "Sandbox expired"
        return self._proj_dir

    @property
    def home_dir(self) -> Path:
        """Returns the sandbox's apio home dir."""
        assert not self.expired, "Sandbox expired"
        return self._home_dir

    @property
    def packages_dir(self) -> Path:
        """Returns the sandbox's apio packages dir."""
        return self.home_dir / "packages"

    def invoke_apio_cmd(
        self,
        cli,
        args: List[str],
        terminal_mode: bool = True,
        in_subprocess: bool = True,
    ) -> ApioResult:
        """Invoke an apio command.  in_subprocess run apios in a subprocess,
        currently this suppresses colors because of the piping."""

        print(f"\nInvoking apio command [{cli.name}], args={args}.")

        # -- Check that this sandbox is still alive.
        assert not self.expired, "Sandbox expired."

        # -- Since we restore the env after invoking the apio command, we
        # -- don't expect path changes by the command to survive here.
        assert SANDBOX_MARKER not in os.environ["PATH"]

        # -- Take a snapshot of the system env.
        original_env = os.environ.copy()

        # -- These two env vars are set when creating the context. Let's
        # -- check that the test didn't corrupt them.
        assert os.environ["APIO_HOME"] == str(self.home_dir)

        # -- If True, force terminal mode, if False, forces pipe mode,
        # -- otherwise auto which is pipe mode under pytest.
        apio_console.configure(
            terminal_mode=FORCE_TERMINAL if terminal_mode else FORCE_PIPE,
        )

        if in_subprocess:
            # -- Invoke apio in a sub process.
            print("Invoking apio in a sub process.")
            process_result: CompletedProcess = subprocess.run(
                [
                    sys.executable,
                    __main__.__file__,
                ]
                + args,
                capture_output=True,
                text=True,
                check=False,
            )

            apio_result = ApioResult(
                process_result.returncode,
                process_result.stdout,
                None,
            )

        else:
            # -- Invoke the command in the same process using click.
            print("Invoking apio in-process using click")
            click_result: Result = self._click_runner.invoke(
                prog_name="apio",
                cli=cli,
                args=args,
                color=terminal_mode,
            )

            # -- Convert click result to apio result.
            apio_result = ApioResult(
                click_result.exit_code,
                click_result.output,
                click_result.exception,
            )

        # -- Dump to test log.
        print(f"result.exit_code:{apio_result.exit_code}")
        print("result.output:")
        print(Result.output)

        # -- Restore system env. Since apio commands tend to change vars
        # -- such as PATH.
        self.set_system_env(original_env)

        return apio_result

    def assert_ok(self, result: ApioResult):
        """Check if apio command results where ok"""

        assert isinstance(result, ApioResult)

        # -- It should return an exit code of 0: success
        assert result.exit_code == 0, result.output

        # -- There should be no exceptions raised
        assert not result.exception

        # -- The word 'error' should NOT appear on the standard output
        assert "error" not in result.output.lower()

    def set_system_env(self, new_vars: Dict[str, str]) -> None:
        """Overwrites the existing sys.environ with the given dict. Vars
        that are not in the dict are deleted and vars that have a different
        value in the dict is updated.  Can be called only within a
        an apio sandbox."""

        # -- Check that the sandbox not expired.
        assert not self.expired, "Sandbox expired"

        # -- NOTE: naively assigning the dict to os.environ will break
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

        # -- Make dir(s) if needed.
        Path(file).parent.mkdir(parents=True, exist_ok=True)

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

    def write_apio_ini(
        self,
        sections: Dict[str, Dict[str, str]] = None,
    ):
        """Write in the current directory an apio.ini file with given
        section. If an apio.ini file already exists, overwrite it."""

        assert isinstance(sections, dict)

        # -- Construct output file path.
        path = Path("apio.ini")

        # -- List with text of each section.
        sections_texts: List[str] = []

        # -- Add the apio section if specified.
        for section_header, section_options in sections.items():
            lines = [section_header]
            for name, value in section_options.items():
                lines.append(f"{name} = {value}")
            sections_texts.append("\n".join(lines))

        # -- Join the sections with a blank line.
        file_text = "\n\n".join(sections_texts)

        # # -- Write the file.
        self.write_file(path, file_text, exists_ok=True)

    def write_default_apio_ini(self):
        """Write in the local directory an apio.ini file with default values
        for testing. If the file exists, it's overwritten."""

        default_apio_ini = {
            "[env:default]": {
                "board": "alhambra-ii",
                "top-module": "main",
            }
        }
        self.write_apio_ini(default_apio_ini)

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

    def __init__(self, request: pytest.FixtureRequest):
        print("*** creating ApioRunner")
        assert isinstance(request, pytest.FixtureRequest)

        # -- A CliRunner instance that is used for creating temp directories
        # -- and to invoke apio commands.
        self._request = request

        # -- Indicate that we are not in a sandbox
        self._sandbox: ApioSandbox = None

        # -- A placeholder for a shared apio home that we may use in some
        # -- of the sandboxes.
        self._shared_apio_home: Path = None

        # -- Register a cleanup method. It's called at the end of the
        # -- apio_runner fixture scope.
        request.addfinalizer(self._teardown)

    def _teardown(self):
        """Teardown at the end of the apio_runner fixture scope."""
        if self._shared_apio_home:
            print(f"Deleting apio shared home {str(self._shared_apio_home)}")
            assert "apio" in str(self._shared_apio_home)
            shutil.rmtree(self._shared_apio_home)
            self._shared_apio_home = None

    @property
    def sandbox(self) -> Optional[ApioSandbox]:
        """Returns the sandbox object or None if not in a sandbox."""
        return self._sandbox

    @contextlib.contextmanager
    def in_sandbox(self, shared_home: bool = False):
        """Create an apio sandbox context manager that delete the temp dir
        and restore the system env upon exist. Shared_home indicates if the
        sandbox uses a unique apio shared home directory or shares it with
        other sandboxes in the same apio_runner scope that set it to True.

        Upon return, the current directory is proj_dir.
        """
        # -- Make sure we don't try to nest sandboxes.
        assert self._sandbox is None, "Already in a sandbox."

        # -- Snapshot the system env.
        original_env: Dict[str, str] = os.environ.copy()

        # -- Snapshot the current directory.
        original_cwd = os.getcwd()

        # -- Create a temp sandbox dir that will be deleted on exit and
        # -- change to it.
        sandbox_dir = Path(tempfile.mkdtemp(prefix=SANDBOX_MARKER + "-"))

        # -- Make the sandbox's project directory. We intentionally use a
        # -- directory name with a space and a non ascii character to test
        # -- that apio can handle it.
        proj_dir = sandbox_dir / "apio prój"
        proj_dir.mkdir()
        os.chdir(proj_dir)

        # -- Determine if we use a shared home or a unique home for this
        # -- sandbox.
        if shared_home:
            # -- Using a shared home. If first time, create and save the path.
            if self._shared_apio_home is None:
                self._shared_apio_home = (
                    Path(tempfile.mkdtemp(prefix=SANDBOX_MARKER + "-"))
                    / "shared-apio-home"
                )
            # -- Use the shared home. It's common to all the sandboxes with
            # -- this instance of ApioRunner fixture.
            home_dir = self._shared_apio_home
        else:
            # -- Using a home dir unique to this sandbox.
            home_dir = sandbox_dir / "apio-home"

        if DEBUG:
            print()
            print("--> apio sandbox:")
            print(f"       sandbox dir       : {str(sandbox_dir)}")
            print(f"       apio proj dir     : {str(proj_dir)}")
            print(f"       apio home dir     : {str(home_dir)}")
            print()

        # -- Register a sandbox objet to indicate that we are in a sandbox.
        assert self._sandbox is None
        self._sandbox = ApioSandbox(self, sandbox_dir, proj_dir, home_dir)

        # -- Set the system env vars to inform ApioContext what are the
        # -- home and packages dirs.
        os.environ["APIO_HOME"] = str(home_dir)

        # -- Reset the apio console, since we run multiple sandboxes in the
        # -- same process.
        apio_console.configure(
            terminal_mode=FORCE_TERMINAL, theme_name="light"
        )

        try:
            # -- This is the end of the context manager _entry part. The
            # -- call to _exit will continue execution after the yield.
            # -- Value is the sandbox object we pass to the user.
            yield cast(ApioSandbox, self._sandbox)

        finally:
            # -- Here when the context manager exit, normally or through an
            # -- exception.

            # -- Restore the original system env.
            self._sandbox.set_system_env(original_env)

            # -- Mark that we exited the sandbox. This expires the sandbox.
            self._sandbox = None

            # -- Change back to the original directory.
            os.chdir(original_cwd)

            # -- Delete the temp directory. This also deletes the apio home
            # -- if it's not shared but doesn't touch it if we use a shared
            # -- home.
            shutil.rmtree(sandbox_dir)

            print("\nSandbox deleted. ")

    @property
    def offline_flag(self) -> bool:
        """Returns True if pytest was invoked with --offline to skip
        tests that require internet connectivity and are slower in general."""
        return self._request.config.getoption("--offline")


@pytest.fixture(scope="module")
def apio_runner(request):
    """A pytest fixture that provides tests with a ApioRunner test
    helper object. We use a 'module' scope so sandboxes can share the apio
    home with other tests in the same file, if we choose to do so,
    to reused previously installed packages.
    """
    return ApioRunner(request)
