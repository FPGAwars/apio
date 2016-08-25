from apio.commands.upload import cli as cmd_upload


def test_apio_upload_board(clirunner):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_upload, ['--board', 'icezum'])
        assert result.exit_code == 1
        assert 'apio install system' in result.output
