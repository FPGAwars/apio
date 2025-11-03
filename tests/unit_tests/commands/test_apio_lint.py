"""Test for the "apio lint" command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_lint_apio_init(apio_runner: ApioRunner):
    """Test: apio lint without an apio.ini project file."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio lint"
        result = sb.invoke_apio_cmd(apio, ["lint"])
        assert result.exit_code == 1, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_lint_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio lint --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["lint", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
