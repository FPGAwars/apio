import apio


def test_apio_build_board(clirunner):
    result = clirunner.invoke(apio.build, ['--board', 'icezum'])
    assert result.exit_code == 1
