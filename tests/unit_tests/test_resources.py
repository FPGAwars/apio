"""
Tests apio/resources.
"""

from tests.conftest import ApioRunner
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils.resource_util import validate_config, validate_packages


def test_resources_are_valid(apio_runner: ApioRunner):
    """Validate resources against a schema."""
    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        validate_config(apio_ctx.config)
        validate_packages(apio_ctx.all_packages)
