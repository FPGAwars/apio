"""
  Test for the "apio upgrade" command
"""

import pytest

# -- apio upgrade entry point
from apio.commands.upgrade import cli as cmd_upgrade


def test_upgrade(clirunner, configenv, validate_cliresult, offline):
    """Test "apio upgrade" """

    # -- If the option 'offline' is passed, the test is skip
    # -- (apio upgrade uses internet)
    if offline:
        pytest.skip('requires internet connection')

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio upgrade"
        result = clirunner.invoke(cmd_upgrade)
        validate_cliresult(result)
