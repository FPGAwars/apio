import pytest

from apio.api import api_request


def test_api_request(capsys, offline):
    if offline:
        pytest.skip('requires internet connection')

    with pytest.raises(SystemExit):
        api_request('missing_command')
    out, err = capsys.readouterr()
    assert "Error: " in out
