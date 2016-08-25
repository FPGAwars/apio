from apio.commands.time import cli as cmd_time


def test_apio_time_board(clirunner):
    result = clirunner.invoke(cmd_time, ['--board', 'icezum'])
    assert result.exit_code == 1
