"""
Tests of apio_definitions.py
"""

# from typing import Dict, Optional, Tuple
# from _pytest.capture import CaptureFixture
# import pytest
from tests.conftest import ApioRunner

# from apio.managers.project import Project, ENV_OPTIONS_SPEC
# from apio.managers.apio_definitions import ApioDefinitions

# from apio.common.apio_console import cunstyle
# from apio.commands.apio import apio_top_cli as apio
# from apio.managers.project import Project
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


def test_default_loading_no_project(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with no project."""

    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        assert not apio_ctx.has_project
        assert "alhambra-ii" in apio_ctx.definitions.boards
        assert "ice40hx4k-tq144-8k" in apio_ctx.definitions.fpgas
        assert "openfpgaloader" in apio_ctx.definitions.programmers


def test_default_loading_with_project(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with a project and
    without project's custom definition."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        assert apio_ctx.has_project
        assert "alhambra-ii" in apio_ctx.definitions.boards
        assert "ice40hx4k-tq144-8k" in apio_ctx.definitions.fpgas
        assert "openfpgaloader" in apio_ctx.definitions.programmers
