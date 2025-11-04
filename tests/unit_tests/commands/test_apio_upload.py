"""Test for the "apio upload" command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_upload_without_apio_ini(apio_runner: ApioRunner):
    """Test: apio upload
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upload"
        result = sb.invoke_apio_cmd(apio, ["upload"])

        # -- Check the result
        assert result.exit_code == 1, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_upload_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio upload --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["upload", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
