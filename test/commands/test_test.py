"""
  Test for the "apio test" command
"""

from test.conftest import ApioRunner

# -- apio test entry point
from apio.commands.sim import cli as apio_test


def test_test(apio_runner: ApioRunner):
    """Test: apio test
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio test"
        result = sb.invoke_apio_cmd(apio_test)
        assert result.exit_code != 0, result.output
        # -- TODO
