from apio.commands.sim import cli as cmd_test


def test_test(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_test, ['--board', 'icezum'])
        assert result.exit_code != 0
        if result.exit_code == 1:
            assert 'apio install iverilog' in result.output
