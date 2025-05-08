"""Test for the "apio upgrade" command."""

from test.conftest import ApioRunner
import pytest
from apio.commands.apio import cli as apio


def test_upgrade(apio_runner: ApioRunner):
    """Test "apio upgrade" """

    # -- If the option 'offline' is passed, the test is skip
    # -- (apio upgrade uses internet)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upgrade"
        result = sb.invoke_apio_cmd(apio, "upgrade")
        sb.assert_ok(result)
