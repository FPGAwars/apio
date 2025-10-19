"""Test for the "apio build" command."""

from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_build_without_apio_ini(apio_runner: ApioRunner):
    """Tests build command with no apio.ini."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build" without apio.ini
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_build_with_apio_ini(apio_runner: ApioRunner):
    """Test build command with apio.ini."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build" with a missing board var.
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Missing required option 'board' for env 'default'"
            in result.output
        )

        # -- Run "apio build" with an invalid board
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "no-such-board",
                    "top-module": "main",
                }
            }
        )
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Unknown board id 'no-such-board' in apio.ini"
            in result.output
        )

        # -- Run "apio build" with an unknown option.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                    "unknown": "xyz",
                }
            }
        )
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Unknown option 'unknown' in [env:default] section "
            "of apio.ini" in result.output
        )


def test_build_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["build", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )
