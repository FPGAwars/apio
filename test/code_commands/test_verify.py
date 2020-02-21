from apio.commands.verify import cli as cmd_verify


def test_verify(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_verify, ['--board', 'icezum'])
        assert result.exit_code != 0
        if result.exit_code == 1:
            assert 'apio install iverilog' in result.output
