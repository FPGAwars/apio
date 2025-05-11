"""
Tests of project.py
"""

from typing import Dict, Optional
from test.conftest import ApioRunner
from pytest import LogCaptureFixture
import pytest
from apio.common.apio_console import cunstyle
from apio.apio_context import ApioContext, ApioContextScope

# TODO: Add more tests.


def test_all_options_env(apio_runner: ApioRunner):
    """Tests an apio.ini with all options"""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    # -- Required.
                    "board": "alhambra-ii",
                    # -- Optional.
                    "top-module": "my_module",
                    "format-verible-options": "\n  --aaa bbb\n  --ccc ddd",
                    "yosys-synth-extra-options": "-dsp -xyz",
                }
            }
        )

        # -- We use ApioContext to instantiate the Project object.
        apio_ctx = ApioContext(
            scope=ApioContextScope.PROJECT_REQUIRED,
            project_dir_arg=sb.proj_dir,
        )
        project = apio_ctx.project

        # -- Verify the required args.
        assert project.get("board") == "alhambra-ii"

        # -- Verify the optional args.
        assert project.get("top-module") == "my_module"
        assert project.get_as_lines_list("format-verible-options") == [
            "--aaa bbb",
            "--ccc ddd",
        ]
        assert project.get("yosys-synth-extra-options") == "-dsp -xyz"

        # -- Try a few as dict lookup.
        assert project["board"] == "alhambra-ii"
        assert project["top-module"] == "my_module"


def test_required_options_only_env(apio_runner: ApioRunner):
    """Tests a minimal apio.ini with required only options."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                }
            }
        )

        # -- We use ApioContext to instantiate the Project object.
        apio_ctx = ApioContext(
            scope=ApioContextScope.PROJECT_REQUIRED,
            project_dir_arg=sb.proj_dir,
        )
        project = apio_ctx.project

        # -- Verify the required args.
        assert project.get("board") == "alhambra-ii"

        # -- Verify the optional args
        assert project.get("top-module") == "main"
        assert project.get_as_lines_list("format-verible-options") is None
        assert project.get("yosys-synth-extra-options") is None

        # -- Verify optionals while specifying explicit defaults.
        assert (
            project.get_as_lines_list("format-verible-options", default=[])
            == []
        )
        assert project.get("yosys-synth-extra-options", "") == ""

        # -- Try a few as dict lookup.
        assert project["board"] == "alhambra-ii"
        assert project["top-module"] == "main"


def error_tester(
    env_arg: Optional[str],
    apio_ini: Dict[str, Dict[str, str]],
    expected_error: str,
    apio_runner: ApioRunner,
    capsys: LogCaptureFixture,
):
    """A helper function to tests apio.ini content that is expected to
    exit with an error."""

    with apio_runner.in_sandbox() as sb:
        # -- Create the apio.ini file
        sb.write_apio_ini(apio_ini)

        # -- Try to create the context with the project info.
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            ApioContext(
                scope=ApioContextScope.PROJECT_REQUIRED,
                project_dir_arg=sb.proj_dir,
                env_arg=env_arg,
            )

        # -- Check the errors.
        capture = cunstyle(capsys.readouterr().out)
        assert e.value.code == 1
        assert expected_error in capture


def test_validation_errors(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests the validation of apio.ini errors."""

    # -- Unknown board name.
    error_tester(
        env_arg=None,
        apio_ini={
            "[env:default]": {
                "board": "no-such-board",
            }
        },
        expected_error="Error: No such board 'no-such-board'",
        apio_runner=apio_runner,
        capsys=capsys,
    )

    # -- Env name has an invalid char (Uppercase).
    error_tester(
        env_arg=None,
        apio_ini={
            "[env:Default]": {
                "board": "alhambra-ii",
            }
        },
        expected_error="Error: Invalid env name 'Default'",
        apio_runner=apio_runner,
        capsys=capsys,
    )

    # -- Env name has an extra space.
    error_tester(
        env_arg=None,
        apio_ini={
            "[env: default]": {
                "board": "alhambra-ii",
            }
        },
        expected_error="Error: Invalid env name ' default'",
        apio_runner=apio_runner,
        capsys=capsys,
    )

    # -- default-env points to a non existing env.
    error_tester(
        env_arg=None,
        apio_ini={
            "[apio]": {
                "default-env": "no-such-env",
            },
            "[env:default]": {
                "board": "alhambra-ii",
            },
        },
        expected_error="Error: Env 'no-such-env' not found in apio.ini",
        apio_runner=apio_runner,
        capsys=capsys,
    )

    # -- Missing required option.
    error_tester(
        env_arg=None,
        apio_ini={
            "[env:default]": {"top-module": "main"},
        },
        expected_error="Error: Missing required option 'board' for "
        "env 'default'.",
        apio_runner=apio_runner,
        capsys=capsys,
    )

    # -- env_arg has a non existing env name.
    error_tester(
        env_arg="no-such-env",
        apio_ini={
            "[env:default]": {"board": "alhambra-ii"},
        },
        expected_error="Active env options [APIO_HOME].\nError: "
        "Env 'no-such-env' not found in apio.ini",
        apio_runner=apio_runner,
        capsys=capsys,
    )

    # -- env_arg has an env name with an invalid char (upper case).
    error_tester(
        env_arg="Default",
        apio_ini={
            "[env:default]": {"board": "alhambra-ii"},
        },
        expected_error="Error: Invalid --env value 'Default'",
        apio_runner=apio_runner,
        capsys=capsys,
    )
