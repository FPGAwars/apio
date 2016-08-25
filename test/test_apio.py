import pytest

from apio import cli as cmd_apio
from apio.api import api_request


def test_apio(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_apio)
    validate_cliresult(result)


def test_apio_wrong_command(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_apio, ['missing_command'])
    assert result.exit_code == 2
    assert 'Error: No such command' in result.output


def test_api_request(capsys):
    with pytest.raises(SystemExit):
        api_request('missing_command')
    out, err = capsys.readouterr()
    assert "Error: " in out
