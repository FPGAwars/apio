"""Utilities related to the Apio resource files."""

from pathlib import Path
import json5
from apio.utils import util
from apio.common.apio_console import fatal_error
from apio.common import proto_util
from apio.common.proto.apio_resources_pb2 import (
    ApioConfig,
    ApioPackageSpec,
)


# -- The resources dir under the Apio package.
RESOURCES_DIR = "resources"

# -- The name of the Apio config file.
CONFIG_JSONC = "config.jsonc"

# -- The name of the packages specification file.
PACKAGES_JSONC = "packages.jsonc"


def read_apio_config_file() -> ApioConfig:
    """Read and validate the config.json resource file."""

    # pylint: disable=broad-exception-caught

    # -- Find config file path within the Apio package
    resources_dir = util.get_path_in_apio_package(RESOURCES_DIR)
    filepath = resources_dir / CONFIG_JSONC

    # -- Read the and parse the jsonc file
    try:
        jsonc_text = filepath.read_text(encoding="utf-8")
        json_dict = json5.loads(jsonc_text)

    except Exception as e:
        fatal_error(
            f"Failed to read json resource file {CONFIG_JSONC}", cause=e
        )

    # -- Convert to proto
    apio_config: ApioConfig = proto_util.proto_from_json_dict(
        json_dict,
        ApioConfig,
        "Failed to parse apio config as a protocol buffer",
    )

    # -- Validate
    assert apio_config.remote_config_ttl_days >= 1, apio_config
    assert apio_config.remote_config_retry_minutes >= 0, apio_config

    # -- All done
    return apio_config


def _expand_env_values(template: str, apio_packages_dir: Path) -> str:
    """Fills a packages env value template as they appear in
    packages.jsonc. Currently it recognizes only a single place holder
    '%p' representing the package absolute path. The '%p" can appear only
    at the beginning of the template.

    E.g. '%p/bin' -> '/users/user/.apio/packages/drivers/bin'

    NOTE: This format is very basic but is sufficient for the current
    needs. If needed, extend or modify it.
    """

    # Case 1: No place holder -> no change.
    if "%p" not in template:
        return template

    # Case 2: The template contains only the placeholder.
    if template == "%p":
        return str(apio_packages_dir)

    # Case 3: The place holder is the prefix of the template's path.
    if template.startswith("%p/"):
        return str(apio_packages_dir / template[3:])

    # Case 4: Unsupported.
    raise RuntimeError(f"Invalid env template: [{template}]")


def _resolve_package_envs(
    packages_: dict[str, dict], apio_packages_dir: Path
) -> None:
    """Resolve in-place the path and var value templates in the
    given packages dictionary. For example, %p is replaced with
    the package's absolute path."""

    for package_name, package_config in packages_.items():

        # -- Get the package root dir.
        package_path = apio_packages_dir / package_name

        # -- Get the json 'env' section. We require it, even if empty,
        # -- for clarity reasons.
        assert "env" in package_config
        package_env = package_config["env"]

        # -- NOTE: There is no need to expand values in the "unset-env"
        # -- section since it contains env names only.

        # -- Expand the values in the "add-to-path" section, if any.
        add_to_path_section = package_env.get("add-to-path", [])
        for i, path_template in enumerate(add_to_path_section):
            add_to_path_section[i] = _expand_env_values(
                path_template, package_path
            )

        # -- Expand the values in the "add-env-vars" section, if any.
        add_env_vars_section = package_env.get("add-env-vars", {})
        for var_name, var_value in add_env_vars_section.items():
            add_env_vars_section[var_name] = _expand_env_values(
                var_value, package_path
            )

        # -- Expand the values in the "define-consts" section, if any.
        define_consts_section = package_env.get("define-consts", {})
        for const_name, const_value in define_consts_section.items():
            define_consts_section[const_name] = _expand_env_values(
                const_value, package_path
            )


def read_apio_packages_file(packages_dir: Path) -> dict[str, ApioPackageSpec]:
    """Read and validate the packages.json resource file. This
    expands the path placeholder in the env fields."""

    # pylint: disable=broad-exception-caught

    # -- Find config file path within the Apio package
    resources_dir = util.get_path_in_apio_package(RESOURCES_DIR)
    filepath = resources_dir / PACKAGES_JSONC

    # -- Read the and parse the jsonc file
    try:
        jsonc_text = filepath.read_text(encoding="utf-8")
        json_dict = json5.loads(jsonc_text)

    except Exception as e:
        fatal_error(
            f"Failed to read json resource file {PACKAGES_JSONC}", cause=e
        )

    # -- Resolve in place the placeholders in the env templates.
    _resolve_package_envs(json_dict, packages_dir)

    # -- Convert to a dict of proto
    packages: dict[str, ApioPackageSpec] = {}
    for name, spec_dict in json_dict.items():

        spec_proto: ApioPackageSpec = proto_util.proto_from_json_dict(
            spec_dict,
            ApioPackageSpec,
            f"Failed to parse package {name} spec as a protocol buffer",
        )
        packages[name] = spec_proto

    # -- All done
    return packages
