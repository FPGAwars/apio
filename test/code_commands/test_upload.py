from apio.commands.upload import cli as cmd_upload


def test_upload(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_device(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, ['--device', '0'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_board(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, ['--board', 'icezum'])
        assert result.exit_code == 1
        assert 'apio install system' in result.output


def test_upload_board_device(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--device', '0'])
        assert result.exit_code == 1
        assert 'apio install system' in result.output
