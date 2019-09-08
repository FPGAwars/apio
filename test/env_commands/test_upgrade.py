import pytest
from apio.commands.upgrade import cli as cmd_upgrade


def test_upgrade(clirunner, validate_cliresult, offline):
    if offline:
        pytest.skip('requires internet connection')

    result = clirunner.invoke(cmd_upgrade)
    validate_cliresult(result)
