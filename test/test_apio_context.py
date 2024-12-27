"""
Tests of apio_context.py
"""

from pathlib import Path
from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope

# pylint: disable=fixme
# TODO: Add more tests.


def test_init(apio_runner: ApioRunner):
    """Tests the initialization of the apio context."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini file.
        sb.write_default_apio_ini()

        # -- Default init.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        assert apio_ctx.has_project

        # -- Verify context's project dir.
        assert str(apio_ctx.project_dir) == "."
        assert apio_ctx.project_dir.samefile(Path.cwd())
        assert apio_ctx.project_dir.samefile(sb.proj_dir)

        # -- Verify context's home and packages dirs.
        assert apio_ctx.home_dir == sb.home_dir
        assert apio_ctx.packages_dir == sb.packages_dir
