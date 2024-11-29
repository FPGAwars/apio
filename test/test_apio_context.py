"""
Tests of scons_util.py
"""

import os
from test.conftest import ApioRunner
from apio.apio_context import ApioContext

# pylint: disable=fixme
# TODO: Add more tests.


def test_init(apio_runner: ApioRunner):
    """Tests the initialization of the apio context."""

    with apio_runner.in_disposable_temp_dir():
        apio_runner.setup_env()
        apio_runner.proj_dir.mkdir(parents=False, exist_ok=False)
        os.chdir(apio_runner.proj_dir)

        # -- Default init.
        apio_ctx = ApioContext(load_project=False)

        assert not apio_ctx.has_project_loaded
