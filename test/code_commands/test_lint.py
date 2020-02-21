from apio.commands.lint import cli as cmd_lint


def test_lint(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_lint, ['--board', 'icezum'])
        assert result.exit_code != 0
        if result.exit_code == 1:
            assert 'apio install verilator' in result.output
