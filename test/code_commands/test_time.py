from apio.commands.time import cli as cmd_time


def test_time(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_time)
        assert result.exit_code != 0
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_time_board(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_time, ['--board', 'icezum'])
        assert result.exit_code != 0
        if result.exit_code == 1:
            assert 'apio install yosys' in result.output
