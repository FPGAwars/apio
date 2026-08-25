"""
A program to check the the published Apio remote configurations. It scans
the 'remote-config' directory of the apio repository and for each remote
config file it verified all the packages versions referred by it do exist
and are stable.

The program exists with an error status upon any error.
"""

import os
import sys
import json
from typing import Dict
import requests
from apio.utils import jsonc

# -- The github repo that contains the remote configs in its 'main' branch.
REMOTE_CONFIG_REPO = "fpgawars/apio"

# -- Names of files and dirs in the remote-config dir that should be ignored.
SKIP_FILES = ["README.md"]

# -- Connect and read timeouts in secs
TIMEOUT = (10, 60)


def github_api_headers() -> dict[str, str]:
    """Construct HTTP headers to pass to the github API. If the env
    var GITHUB_TOKEN is defined, it is used as the github token for
    less restrictive rate quota, otherwise the default anonymous identity
    which has small quota"""
    headers = {
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("Using GITHUB_TOKEN from env")
        headers["Authorization"] = f"Bearer {token}"
    else:
        print("Env var GITHUB_TOKEN not found, using anonymous identity")

    return headers


def check_package(package_name: str, package_config: Dict):
    """Check a single package release of a single remote config given its
    name and json configuration."""
    org = package_config["repository"]["organization"]
    repo = package_config["repository"]["name"]
    tag = package_config["release"]["tag"]

    print()
    print(f"Checking package [{package_name}] release [{tag}]")

    # -- Get release info.
    api_url = f"https://api.github.com/repos/{org}/{repo}/releases/tags/{tag}"
    resp = requests.get(api_url, headers=github_api_headers(), timeout=TIMEOUT)

    # -- Check http status.
    if resp.status_code == 404:
        print(
            f"Error: release '{tag}' not found in {org}/{repo}",
            file=sys.stderr,
        )
        sys.exit(1)

    if resp.status_code != 200:
        print(
            f"Error: GitHub API returned {resp.status_code} for {api_url}",
            file=sys.stderr,
        )
        sys.exit(1)

    # -- Check release metadata.
    print("Release exists")

    data = resp.json()

    if data.get("draft", False):
        print(
            f"Error: release '{tag}' exists but is still a draft",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print("Release is not a draft")

    if data.get("prerelease", False):
        print(
            f"Error: release '{tag}' exists but is a pre-release",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print("Release is not a pre-release")

    asset_names = [asset["name"] for asset in data["assets"]]
    for asset_name in asset_names:
        print(f"- {asset_name}")

    print("Release exists and is stable")


def check_remote_config(jsonc_text: Dict):
    """Check a given remote config file given its content as a parsed json
    dict."""
    json_text = jsonc.to_json(jsonc_text)
    json_data = json.loads(json_text)

    # -- Sanity check the package count
    assert 5 <= len(json_data["packages"]) <= 15

    # -- Check each package.
    for package_name, package_config in json_data["packages"].items():
        check_package(package_name, package_config)


def main():
    """Check all packages releases that are referred to by apio remote config
    files."""

    # -- Dump out rate throttling state on github. Having GITHUB_TOKEN
    # -- env-var will increase out quote.
    resp = requests.get("https://api.github.com/rate_limit", timeout=TIMEOUT)
    throttling_info = resp.json()["rate"]
    print(f"Github rate throttling: {throttling_info}")
    print()

    # -- Fetch the list of *.jsonc files in the remote-config dir. This
    # -- is where each apio instance looks up its remote config based its
    # -- version.
    api_url = (
        f"https://api.github.com/repos/{REMOTE_CONFIG_REPO}/"
        "contents/remote-config?ref=main"
    )
    print("Fetching remote-config files list")
    print("URL: {api_url} ...")
    resp = requests.get(api_url, headers=github_api_headers(), timeout=TIMEOUT)
    resp.raise_for_status()

    # -- Extract the list of directory entries.
    files_infos = resp.json()

    # -- Process directory entries.
    files_checked = 0
    for file_info in files_infos:

        # -- Skip files that are in SKIP_FILES.
        file_name: str = file_info["name"]
        if file_name in SKIP_FILES:
            print(f"Skipping {file_name}")
            continue

        # -- Announce remote config file name.
        print(f"\n\n===== Remote Config {file_name} =====\n")

        # -- Should be *.jsonc
        assert file_name.endswith(".jsonc"), file_name

        # -- Fetch the content of the remote config file.
        download_url = file_info["download_url"]
        print(f"URL: {download_url} ...")
        r = requests.get(download_url, timeout=TIMEOUT)
        r.raise_for_status()

        # Extract the remote config file content
        jsonc_text = r.content.decode("utf-8", errors="strict")

        # Check this remote config.
        check_remote_config(jsonc_text)
        files_checked += 1

    # -- Sanity check
    assert files_checked >= 3, files_checked

    print(f"\nDone ({files_checked} remote configs).")


if __name__ == "__main__":
    main()
