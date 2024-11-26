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

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- apio sim --board icezum
        result = apio_runner.invoke(apio_sim)
        assert result.exit_code != 0, result.output
        # -- TODO
