from apio.commands.build import cli as cmd_build


def test_apio_build_board(clirunner):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_build, ['--board', 'icezum'])
        assert result.exit_code == 1
        assert 'apio install scons' in result.output
