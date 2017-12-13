from apio.commands.clean import cli as cmd_clean


def test_clean(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_clean)
        assert result.exit_code != 0
