"""
Tests of project.py
"""

from typing import Dict, Optional, Tuple
from test.conftest import ApioRunner
from pytest import LogCaptureFixture
import pytest
from apio.managers.project import Project, ENV_OPTIONS
from apio.common.apio_console import cunstyle
from apio.apio_context import ApioContext, ApioContextScope

# TODO: Add more tests.


def load_apio_ini(
    apio_ini: Dict[str, Dict[str, str]],
    env_arg: Optional[str],
    apio_runner: ApioRunner,
    capsys: LogCaptureFixture,
) -> Tuple[Project, str]:
    """A helper function load apio.ini.  Returns (project, stdout)"""

    with apio_runner.in_sandbox() as sb:
        # -- Create the apio.ini file
        sb.write_apio_ini(apio_ini)

        # -- Try to create the context with the project info.
        capsys.readouterr()  # Reset capture
        apio_ctx = ApioContext(
            scope=ApioContextScope.PROJECT_REQUIRED,
            env_arg=env_arg,
        )

        # -- Return the values.
        return (
            apio_ctx.project,
            cunstyle(capsys.readouterr().out),
        )


def test_all_options_env(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests an apio.ini with all options"""

    apio_ini = {
        "[env:default]": {
            "board": "alhambra-ii",  # required.
            "default-testbench": "main_tb.v",
            "defines": "\n  aaa=111\n  bbb=222",
            "format-verible-options": "\n  --aaa bbb\n  --ccc ddd",
            "programmer-cmd": "iceprog ${VID}:${PID}",
            "top-module": "my_module",
            "yosys-synth-extra-options": "-dsp -xyz",
        }
    }

    # -- Make sure we covered all the options.
    assert len(apio_ini["[env:default]"]) == len(ENV_OPTIONS)

    project, _ = load_apio_ini(
        apio_ini=apio_ini,
        env_arg=None,
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "default"
    assert project.env_options == {
        "board": "alhambra-ii",
        "default-testbench": "main_tb.v",
        "defines": "\naaa=111\nbbb=222",
        "format-verible-options": "\n--aaa bbb\n--ccc ddd",
        "programmer-cmd": "iceprog ${VID}:${PID}",
        "top-module": "my_module",
        "yosys-synth-extra-options": "-dsp -xyz",
    }

    # -- Try a few as dict lookup on the project object.
    assert project["board"] == "alhambra-ii"
    assert project["top-module"] == "my_module"


def test_required_options_only_env(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests a minimal apio.ini with required only options."""

    project, stdout = load_apio_ini(
        apio_ini={
            "[env:default]": {
                "board": "alhambra-ii",
            }
        },
        env_arg=None,
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "default"
    assert project.env_options == {
        "board": "alhambra-ii",
        "top-module": "main",
    }
    assert (
        "Option 'top-module' is missing for env default, assuming 'main'"
        in stdout
    )


def test_legacy_board_name(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests with 'board' option having a legacy board name. It should
    be converted to the canonical board name"""

    project, stdout = load_apio_ini(
        apio_ini={
            "[env:default]": {
                "board": "iCE40-HX8K",
                "top-module": "my_top_module",
            }
        },
        env_arg=None,
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "default"
    assert project.env_options == {
        "board": "ice40-hx8k",
        "top-module": "my_top_module",
    }
    assert (
        "Warning: 'Board iCE40-HX8K' was renamed to 'ice40-hx8k'. "
        "Please update apio.ini" in stdout
    )


def test_legacy_apio_ini(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests with an old style apio.ini that has a single [env] section."""

    project, stdout = load_apio_ini(
        apio_ini={
            "[env]": {
                "board": "alhambra-ii",
            }
        },
        env_arg=None,
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "default"
    assert project.env_options == {
        "board": "alhambra-ii",
        "top-module": "main",
    }
    assert (
        "Warning: Apio.ini has a legacy [env] section. "
        "Please rename it to [env:default]" in stdout
    )


def test_first_env_is_default(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests that with no --env and no default-env, the first env in
    apio.ini is selected"""

    project, _ = load_apio_ini(
        apio_ini={
            "[common]": {
                "default-testbench": "main_tb.v",
            },
            "[env:env1]": {
                "board": "alhambra-ii",
                "top-module": "module1",
            },
            "[env:env2]": {
                "board": "ice40-hx8k",
                "top-module": "module2",
            },
        },
        env_arg=None,
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "env1"
    assert project.env_options == {
        "default-testbench": "main_tb.v",
        "board": "alhambra-ii",
        "top-module": "module1",
    }


def test_env_selection_from_apio_ini(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests that with no --env, and with default env defined in apio.ini
    using default-env option."""

    project, _ = load_apio_ini(
        apio_ini={
            "[apio]": {
                "default-env": "env2",
            },
            "[common]": {
                "default-testbench": "main_tb.v",
            },
            "[env:env1]": {
                "board": "alhambra-ii",
                "top-module": "module1",
            },
            "[env:env2]": {
                "board": "ice40-hx8k",
                "top-module": "module2",
            },
        },
        env_arg=None,
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "env2"
    assert project.env_options == {
        "default-testbench": "main_tb.v",
        "board": "ice40-hx8k",
        "top-module": "module2",
    }


def test_env_selection_from_env_arg(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests that with --env overriding default-env in apio.ini."""

    project, _ = load_apio_ini(
        apio_ini={
            "[apio]": {
                "default-env": "env1",
            },
            "[common]": {
                "default-testbench": "main_tb.v",
            },
            "[env:env1]": {
                "board": "alhambra-ii",
                "top-module": "module1",
            },
            "[env:env2]": {
                "board": "ice40-hx8k",
                "top-module": "module2",
            },
        },
        env_arg="env2",  # --env env2
        apio_runner=apio_runner,
        capsys=capsys,
    )

    assert project.env_name == "env2"
    assert project.env_options == {
        "default-testbench": "main_tb.v",
        "board": "ice40-hx8k",
        "top-module": "module2",
    }


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
        expected_error="Error: Unknown board name 'no-such-board' in apio.ini",
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
