"""Test for the "apio upgrade" command."""

from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_upgrade(apio_runner: ApioRunner):
    """Test "apio upgrade" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upgrade"
        result = sb.invoke_apio_cmd(apio, ["upgrade"])
        sb.assert_ok(result)
