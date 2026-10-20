# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""Utilities related to the Apio resource files."""

import json
import re
from pathlib import Path
from dataclasses import dataclass
from apio.utils import util, jsonc
from apio.common.apio_console import fatal_error
from apio.common.apio_platforms import get_apio_platforms
from apio.common import proto_util
from apio.common.proto.stubs.apio_config_pb2 import (
    ApioRawConfig,
    ApioRemoteConfigSpec,
    ApioPlatformEnvSpec,
    ApioPackageSpec,
)
from apio.common.apio_platforms import ApioPlatform

# -- Relative path from apio root to the config file.
CONFIG_JSON = "resources/config.jsonc"


@dataclass(frozen=True)
class ApioConfig:
    """Represents the information extracted from the config file for the
    scope of current platform."""

    platform_id: str
    all_packages: dict[str, ApioPackageSpec]
    platform_packages: dict[str, ApioPackageSpec]
    platform_env: ApioPlatformEnvSpec
    remote_config: ApioRemoteConfigSpec

    def __post_init__(self) -> None:
        """Verify member types."""
        assert isinstance(self.platform_id, str)
        assert isinstance(self.all_packages, dict)
        assert isinstance(self.platform_packages, dict)
        assert isinstance(self.platform_env, ApioPlatformEnvSpec)
        assert isinstance(self.remote_config, ApioRemoteConfigSpec)

        # Optional: check dict value types
        for k, v in self.all_packages.items():
            assert isinstance(k, str)
            assert isinstance(v, ApioPackageSpec)

        for k, v in self.platform_packages.items():
            assert isinstance(k, str)
            assert isinstance(v, ApioPackageSpec)


def _resolve_str_placeholders(text: str, mapping: dict) -> str:
    """Replace all {key} place holder with their respective values."""

    def replacer(match):
        key = match.group(1)
        assert key in mapping, f"Unknown placeholder '{key}'"
        return str(mapping[key])

    return re.sub(r"\{([^{}]+)\}", replacer, text)


def read_apio_config_file(
    platform: ApioPlatform, packages_dir: Path
) -> ApioConfig:
    """Read and validate the config.json resource file."""

    # pylint: disable=broad-exception-caught
    # pylint: disable=too-many-locals

    # -- Find config file path within the Apio package
    filepath = util.get_path_in_apio_package(CONFIG_JSON)

    # -- Read the and parse the jsonc file
    try:
        jsonc_text = filepath.read_text(encoding="utf-8")
        json_text = jsonc.to_json(jsonc_text)
        json_dict = json.loads(json_text)

    except Exception as e:
        fatal_error(
            "Failed to read Apio json config file file",
            f"File path: '{str(filepath)}'",
            cause=e,
        )

    # -- Convert to proto
    apio_config: ApioRawConfig | None = proto_util.proto_from_json_dict(
        json_dict,
        ApioRawConfig,
    )
    if apio_config is None:
        fatal_error("Failed to parse apio config as a protocol buffer")

    # -- Verify that config includes all platforms
    for p in get_apio_platforms():
        assert p in apio_config.platforms, f"Missing platform {p}"

    # -- verify that config doesn't have additional unknown platforms.
    assert len(get_apio_platforms()) == len(
        apio_config.platforms
    ), "Extra platforms in config files."

    # -- Verify remote config params.
    assert apio_config.remote_config.ttl_days >= 1, apio_config
    assert apio_config.remote_config.retry_minutes >= 0, apio_config

    # -- Get the spec of current platform.
    platform_spec = apio_config.platforms[platform.id]

    # -- Construct a map with all packages specs.
    all_packages_dict: dict[str, ApioPackageSpec] = {}
    for k, v in apio_config.packages.items():
        all_packages_dict[k] = v

    # -- Construct a map with platform packages specs only.
    platform_packages_dict: dict[str, ApioPackageSpec] = {}
    for k, v in apio_config.packages.items():
        if k in platform_spec.packages:
            platform_packages_dict[k] = v

    # -- Construct the result.
    result = ApioConfig(
        platform_id=platform.id,
        all_packages=all_packages_dict,
        platform_packages=platform_packages_dict,
        platform_env=platform_spec.env,
        remote_config=apio_config.remote_config,
    )

    # -- Construct mapping of package name to package string path.
    # -- We will use it to resolve the placeholders.
    mapping: dict[str, str] = {}
    for package_name in result.platform_packages:
        mapping[package_name] = str(packages_dir / package_name)

    # -- NOTE: No need resolve delete_env_vars since they have no values.

    # -- Resolve placeholders in add_to_path
    new_list = [
        _resolve_str_placeholders(v, mapping)
        for v in result.platform_env.add_to_path
    ]
    result.platform_env.add_to_path.clear()
    result.platform_env.add_to_path.extend(new_list)

    # -- Resolve placeholders in add_env_var
    new_dict = {
        k: _resolve_str_placeholders(v, mapping)
        for k, v in result.platform_env.add_env_vars.items()
    }
    result.platform_env.add_env_vars.clear()
    result.platform_env.add_env_vars.update(new_dict)

    # -- Resolve placeholders in define_consts
    new_dict = {
        k: _resolve_str_placeholders(v, mapping)
        for k, v in result.platform_env.define_consts.items()
    }
    result.platform_env.define_consts.clear()
    result.platform_env.define_consts.update(new_dict)

    # -- All done
    return result
