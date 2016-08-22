import apio
from click.testing import CliRunner


def test_apio_sim():
    runner = CliRunner()
    result = runner.invoke(apio.sim)
    assert result.exit_code == 1
