import apio


def test_apio_sim(clirunner):
    result = clirunner.invoke(apio.sim)
    assert result.exit_code == 1
