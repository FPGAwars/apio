import apio


def test_apio_time_board(clirunner):
    result = clirunner.invoke(apio.time, ['--board', 'icezum'])
    assert result.exit_code == 1
