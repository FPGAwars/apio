import pytest

from apio.api import api_request

@pytest.mark.skipif(pytest.config.getvalue('offline'),
                    reason="requires internet connection")
def test_api_request(capsys):
    with pytest.raises(SystemExit):
        api_request('missing_command')
    out, err = capsys.readouterr()
    assert "Error: " in out
