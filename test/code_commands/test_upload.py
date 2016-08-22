import apio
from click.testing import CliRunner


def test_apio_upload_board():
    runner = CliRunner()
    result = runner.invoke(apio.upload, ['--board', 'icezum'])
    assert result.exit_code == 1
