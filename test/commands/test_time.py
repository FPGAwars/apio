"""
  Test for the "apio time" command
"""

from test.conftest import ApioRunner

# -- apio time entry point
from apio.commands.time import cli as apio_time


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_time(apio_runner: ApioRunner):
    """Test: apio time
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio time"
        result = sb.invoke_apio_cmd(apio_time)

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_time_board(apio_runner: ApioRunner):
    """Test: apio time
    when parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio time"
        result = sb.invoke_apio_cmd(apio_time, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
