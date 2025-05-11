"""Test for the "apio format" command."""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_format_without_apio_ini(apio_runner: ApioRunner):
    """Tests the apio format command with a missing apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio format" with no apio.ini
        result = sb.invoke_apio_cmd(apio, "format")
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_format_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio format --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, "format", "--env", "no-such-env")
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
