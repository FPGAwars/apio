import apio
from click.testing import CliRunner


def test_apio_build_board():
    runner = CliRunner()
    result = runner.invoke(apio.build, ['--board', 'icezum'])
    assert result.exit_code == 1
