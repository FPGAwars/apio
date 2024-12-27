"""
  Test for the "apio test" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_test(apio_runner: ApioRunner):
    """Test: apio test
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio test"
        result = sb.invoke_apio_cmd(apio, ["test"])
        assert result.exit_code != 0, result.output
        assert "Error: missing project file apio.ini" in result.output
