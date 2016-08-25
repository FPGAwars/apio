from apio.commands.build import cli as cmd_build


def test_build(clirunner):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_build)
        assert result.exit_code == 1
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_build_board(clirunner):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_build, ['--board', 'icezum'])
        assert result.exit_code == 1
        assert 'apio install scons' in result.output
