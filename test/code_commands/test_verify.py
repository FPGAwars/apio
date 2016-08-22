import apio
from click.testing import CliRunner


def test_apio_verify():
    runner = CliRunner()
    result = runner.invoke(apio.verify)
    assert result.exit_code == 1
