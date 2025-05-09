"""Test for the "apio build" command."""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_build_without_apio_init(apio_runner: ApioRunner):
    """Tests build with various valid and invalid apio variation, all tests
    are offline and without any apio package installed."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build" without apio.ini
        result = sb.invoke_apio_cmd(apio, "build")
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_build_with_apio_init(apio_runner: ApioRunner):
    """Tests build with various valid and invalid apio variation, all tests
    are offline and without any apio package installed."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build" with a missing board var.
        sb.write_apio_ini({"[env]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, "build")
        assert result.exit_code == 1, result.output
        assert "Error: Missing option 'board'" in result.output

        # -- Run "apio build" with an invalid board
        sb.write_apio_ini(
            {
                "[env]": {
                    "board": "no-such-board",
                    "top-module": "main",
                }
            }
        )
        result = sb.invoke_apio_cmd(apio, "build")
        assert result.exit_code == 1, result.output
        assert "no such board 'no-such-board'" in result.output.lower()

        # -- Run "apio build" with an unknown option.
        sb.write_apio_ini(
            {
                "[env]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                    "unknown": "xyz",
                }
            }
        )
        result = sb.invoke_apio_cmd(apio, "build")
        assert result.exit_code == 1, result.output
        assert (
            "Error: Unknown option 'unknown' in [env:default] section "
            "of apio.ini" in result.output
        )
