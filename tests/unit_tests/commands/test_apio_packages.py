# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""Test for the "apio packages" command."""

import json
import os
from datetime import datetime, timedelta
from os import listdir, rename
from unittest.mock import Mock, patch
import pytest
import requests
from tests.conftest import ApioRunner, ApioSandbox
from apio.commands.apio import apio_top_cli as apio
from apio.common.apio_console import cunstyle
from apio.apio_context import ApioContext, PackagesPolicy, ProjectPolicy
from apio.managers.remote_config import RemoteConfigPolicy, get_datetime_stamp


def test_packages(apio_runner: ApioRunner):
    """Test "apio packages" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio packages"
        result = sb.invoke_apio_cmd(apio, ["packages"])
        sb.assert_result_ok(result)
        assert "Subcommands:" in result.output
        assert "apio packages install" in cunstyle(result.output)
        assert "apio packages list" in cunstyle(result.output)
        assert result.output != cunstyle(result.output)  # Colored.


def test_packages_list(apio_runner: ApioRunner):
    """Test "apio packages" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio packages list"
        result = sb.invoke_apio_cmd(apio, ["packages", "list"])
        sb.assert_result_ok(result)


@pytest.fixture(name="cached_packages")
def cached_packages_fixture(apio_runner: ApioRunner):
    """Use real installed packages with an isolated, stale config cache."""
    with apio_runner.in_sandbox() as sb:
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.GET_FRESH,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )
        cache_path = sb.home_dir / "cached-remote-config.json"
        cache = sb.read_json_file(cache_path)
        config_url = "https://example.invalid/remote-config"
        os.environ["APIO_REMOTE_CONFIG_URL"] = config_url
        cache["metadata"]["loaded-from"] = (
            config_url
            + "/"
            + apio_ctx.remote_config.remote_config_file_url.split("/")[-1]
        )
        cache["metadata"]["loaded-at"] = get_datetime_stamp(
            datetime.now() - timedelta(days=31)
        )
        sb.write_json_file(cache_path, cache, exists_ok=True)
        yield sb


@pytest.mark.parametrize("cached_ok", [False, True])
@pytest.mark.parametrize("cache_age", [0, 31])
@pytest.mark.parametrize("verbose", [False, True])
def test_packages_install_offline(
    cached_packages: ApioSandbox,
    cached_ok: bool,
    cache_age: int,
    verbose: bool,
):
    """Only the opt-in command can use a fresh or stale cache offline."""
    sb = cached_packages
    cache_path = sb.home_dir / "cached-remote-config.json"
    cache = sb.read_json_file(cache_path)
    cache["metadata"]["loaded-at"] = get_datetime_stamp(
        datetime.now() - timedelta(days=cache_age)
    )
    sb.write_json_file(cache_path, cache, exists_ok=True)
    args = ["packages", "install"]
    if cached_ok:
        args.append("--cached-ok")
    if verbose:
        args.append("--verbose")
    with patch(
        "requests.get", side_effect=requests.ConnectionError("offline")
    ) as fetch:
        result = sb.invoke_apio_cmd(apio, args)

    if cached_ok:
        # A failed refresh is reported even when the cached config is usable.
        sb.assert_result_ok(result, bad_words=[])
        assert "All Apio packages are installed OK" in result.output
    else:
        assert result.exit_code == 1
    assert fetch.call_count == (0 if cached_ok and cache_age == 0 else 1)
    if fetch.called:
        assert (
            "Downloading of the latest Apio remote config file failed"
            in result.output
        )


@pytest.mark.parametrize(
    "problem",
    ["no-cache", "wrong-apio-version", "missing", "mismatch", "force"],
)
def test_packages_cached_ok_offline_failure(
    cached_packages: ApioSandbox, problem: str
):
    """A cached config cannot replace a required package download."""
    sb = cached_packages
    cache_path = sb.home_dir / "cached-remote-config.json"
    args = ["packages", "install", "--cached-ok"]
    if problem == "no-cache":
        cache_path.unlink()
    elif problem == "wrong-apio-version":
        cache = sb.read_json_file(cache_path)
        cache["metadata"]["loaded-by"] = "0.0.0"
        sb.write_json_file(cache_path, cache, exists_ok=True)
    elif problem in ("missing", "mismatch"):
        # Keep failure-path repairs away from the shared toolchain cache.
        packages_dir = sb.home_dir / "apio-packages"
        packages_dir.mkdir()
        os.environ["APIO_PACKAGES"] = str(packages_dir)
        if problem == "mismatch":
            installed = sb.read_json_file(
                sb.packages_dir / "installed_packages.json"
            )
            info = installed["definitions"]
            info["version"] = "0.0.0"
            (packages_dir / "definitions").mkdir()
            sb.write_json_file(
                packages_dir / "installed_packages.json", {"definitions": info}
            )
    else:
        args.append("--force")

    with patch(
        "requests.get", side_effect=requests.ConnectionError("offline")
    ) as fetch:
        result = sb.invoke_apio_cmd(apio, args)

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "All Apio packages are installed OK" not in result.output
    if problem in ("no-cache", "wrong-apio-version"):
        assert fetch.call_count == 1
    else:
        assert fetch.call_count == 2
        assert "Failed to download package" in result.output
    if problem == "mismatch":
        assert "Uninstalling broken package 'definitions'" in result.output
    assert (
        sb.packages_dir / "definitions/examples/alhambra-ii/ledon/main.v"
    ).is_file()


def test_packages_cached_ok_refresh(cached_packages: ApioSandbox):
    """A stale cache is refreshed when the remote config is available."""
    sb = cached_packages
    cache_path = sb.home_dir / "cached-remote-config.json"
    cache = sb.read_json_file(cache_path)
    response = Mock(status_code=200, text=json.dumps(cache["remote-config"]))
    with patch("requests.get", return_value=response) as fetch:
        result = sb.invoke_apio_cmd(
            apio, ["packages", "install", "--cached-ok"]
        )
    sb.assert_result_ok(result)
    fetch.assert_called_once_with(cache["metadata"]["loaded-from"], timeout=25)
    updated = sb.read_json_file(cache_path)
    assert updated["metadata"]["loaded-at"] != cache["metadata"]["loaded-at"]


def test_packages_install(apio_runner: ApioRunner):
    """Tests listing, installation and uninstallation of packages."""

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio packages list'
        result = sb.invoke_apio_cmd(apio, ["packages", "list"])
        sb.assert_result_ok(result)
        assert "definitions" in result.output
        assert "oss-cad-suite" in result.output

        # -- Run 'apio packages install'.
        # -- Both 'definitions' and 'oss-cad-suite' should exist, and
        # -- possibly others, depending on the platform.
        result = sb.invoke_apio_cmd(apio, ["packages", "install"])
        sb.assert_result_ok(result)
        assert "All Apio packages are installed OK" in result.output
        assert listdir(sb.packages_dir / "definitions/examples/alhambra-ii")
        assert listdir(sb.packages_dir / "oss-cad-suite/bin")

        # -- Delete a file from the definitions package, we will use it as an
        # -- indicator for the reinstallation of the package.
        marker_file = (
            sb.packages_dir / "definitions/examples/alhambra-ii/ledon/main.v"
        )
        assert marker_file.is_file()
        marker_file.unlink()
        assert not marker_file.exists()

        # -- Run 'apio packages install'.
        # -- This should not do anything since it's considered to be installed.
        result = sb.invoke_apio_cmd(apio, ["packages", "install"])
        sb.assert_result_ok(result)
        assert "Package 'definitions' installed" not in result.output
        assert not marker_file.exists()

        # -- Run 'apio packages install --force'
        # -- This should recover the file.
        result = sb.invoke_apio_cmd(apio, ["packages", "install", "--force"])
        sb.assert_result_ok(result)
        assert "Package 'definitions' installed" in result.output
        assert marker_file.is_file()

        # -- Break the definitions package by renaming it. This also creates an
        # -- orphan dir.
        definitions_package_dir = sb.packages_dir / "definitions"
        bad_package_dir = sb.packages_dir / "unknown-package"
        rename(definitions_package_dir, bad_package_dir)
        assert not definitions_package_dir.exists()
        assert bad_package_dir.is_dir()

        # -- Run 'apio packages install'. This should fix everything.
        result = sb.invoke_apio_cmd(apio, ["packages", "install"])
        sb.assert_result_ok(result)
        assert "Uninstalling broken package 'definitions'" in result.output
        assert (
            "Deleting unknown package dir 'unknown-package'" in result.output
        )
        assert "Package 'definitions' installed successfully" in result.output
        assert definitions_package_dir.is_dir()
        assert marker_file.exists()
        assert not bad_package_dir.exists()
