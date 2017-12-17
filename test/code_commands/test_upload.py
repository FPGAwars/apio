from apio.commands.upload import cli as cmd_upload


def test_upload(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_serial_port(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, ['--serial-port', 'COM0'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_ftdi_id(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, ['--ftdi-id', '0'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_sram(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, ['--sram'])
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_upload_board(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, ['--board', 'icezum'])
        assert result.exit_code == 1


def test_upload_board_serial_port(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--serial-port', 'COM0'])
        assert result.exit_code == 1


def test_upload_board_ftdi_id(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--ftdi-id', '0'])
        assert result.exit_code == 1


def test_upload_board_sram(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_upload, [
            '--board', 'icezum', '--sram'])
        assert result.exit_code == 1
