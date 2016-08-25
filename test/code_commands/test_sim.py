from apio.commands.sim import cli as cmd_sim


def test_apio_sim(clirunner):
    result = clirunner.invoke(cmd_sim)
    assert result.exit_code == 1
