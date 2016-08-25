from apio.commands.build import cli as cmd_build


def test_apio_build_board(clirunner):
    result = clirunner.invoke(cmd_build, ['--board', 'icezum'])
    assert result.exit_code == 1
