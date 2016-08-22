import apio


def test_apio_upload_board(clirunner):
    result = clirunner.invoke(apio.upload, ['--board', 'icezum'])
    assert result.exit_code == 1
