"""Test for the "apio sim" command"""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_sim(apio_runner: ApioRunner):
    """Test: apio sim
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- apio sim
        result = sb.invoke_apio_cmd(apio, ["sim"])
        assert result.exit_code != 0, result.output
        # -- TODO


def test_sim_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio sim --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["sim", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
