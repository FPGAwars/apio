"""
  Test for the "apio sim" command
"""

from test.conftest import ApioRunner

# -- apio sim entry point
from apio.commands.sim import cli as apio_sim


def test_sim(apio_runner: ApioRunner):
    """Test: apio sim
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- apio sim --board icezum
        result = sb.invoke_apio_cmd(apio_sim)
        assert result.exit_code != 0, result.output
        # -- TODO
