from apio.commands.clean import cli as cmd_clean


def test_apio_clean(clirunner):
    result = clirunner.invoke(cmd_clean)
    assert result.exit_code == 0
