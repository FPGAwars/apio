"""Test for the "apio report" command."""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_report_no_apio(apio_runner: ApioRunner):
    """Tests the apio report command without an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio report" without apio.ini
        result = sb.invoke_apio_cmd(apio, "report")
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_report_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio report --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, "report", "--env", "no-such-env")
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
