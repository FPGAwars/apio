from apio.commands.upload import cli as cmd_upload


def test_apio_upload_board(clirunner):
    result = clirunner.invoke(cmd_upload, ['--board', 'icezum'])
    assert result.exit_code == 1
