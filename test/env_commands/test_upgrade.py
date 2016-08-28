import pytest
from apio.commands.upgrade import cli as cmd_upgrade


@pytest.mark.skipif(pytest.config.getvalue('offline'),
                    reason="requires internet connection")
def test_upgrade(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_upgrade)
    validate_cliresult(result)
