from apio.commands.sim import cli as cmd_sim


def test_sim(clirunner):
    with clirunner.isolated_filesystem():
        result = clirunner.invoke(cmd_sim)
        assert result.exit_code == 1
        assert 'apio install scons' in result.output
