"""
A program to check the the published Apio remote configurations. It scans
the 'remote-config' directory of the apio repository and for each remote
config file it verified all the packages versions referred by it do exist
and are stable.

The program exists with an error status upon any error.
"""

# -- Standard python
import os
import sys
from typing import Dict

# -- Third party
import json5
import requests

# -- The github repo that contains the remote configs in its 'main' branch.
REMOTE_CONFIG_REPO = "fpgawars/apio"

# -- Names of files and dirs in the remote-config dir that should be ignored.
SKIP_FILES = ["README.md"]

# -- Connect and read timeouts in secs
TIMEOUT = (10, 60)

# -- Names under which a release publishes its parts index: the name the
# -- document has inside the package, and the dated asset name apio derives
# -- from the tag. Both are accepted, so that renaming the asset to the
# -- former does not need this script and the toolchain to change at once.
PARTS_INDEX_NAME = "PARTS-INDEX.json"
PARTS_INDEX_PREFIX = "apio-xilinx-parts-index-"

# -- Packages whose device databases are fetched on demand, and the first
# -- release tag that is. Their earlier releases carried the databases
# -- inside the package and need no index; from these tags on, a release
# -- without one is broken, not old.
PARTS_INDEX_REQUIRED_FROM = {"openxc7": "2026-08-29"}

# -- The parts index schema that apio's loader
# -- (apio/managers/xilinx_chipdb.py) knows how to read. A release with a
# -- different schema renamed or reshaped the fields the loader uses, so
# -- bump this together with the loader.
PARTS_INDEX_SCHEMA_VERSION = 5


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
        print(f"Error: release '{tag}' not found in {org}/{repo}")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"Error: GitHub API returned {resp.status_code} for {api_url}")
        sys.exit(1)

    # -- Check release metadata.
    print("Release exists")

    data = resp.json()

    if data.get("draft", False):
        print(f"Error: release '{tag}' exists but is still a draft")
        sys.exit(1)
    else:
        print("Release is not a draft")

    if data.get("prerelease", False):
        print(f"Error: release '{tag}' exists but is a pre-release")
        sys.exit(1)
    else:
        print("Release is not a pre-release")

    assets = {asset["name"]: asset for asset in data["assets"]}
    for asset_name in assets:
        print(f"- {asset_name}")

    print("Release exists and is stable")

    # -- If this package fetches its device databases on demand, check that
    # -- the databases its index promises are actually published.
    check_parts_index(package_name, tag, assets)


def check_parts_index_content(index_name: str, index: Dict, assets: Dict):
    """Check the content of a parts index against the release that
    publishes it. 'assets' maps the release's asset names to their github
    metadata."""

    # -- The document counts what it contains. A mismatch means the index
    # -- was built from a different set of parts than it describes.
    parts = index["parts"]
    generated = {n: p for n, p in parts.items() if p["generated"]}
    databases = {p["chipdb"] for p in generated.values()}
    for key, actual in [
        ("part-count", len(parts)),
        ("generated-count", len(generated)),
        ("chipdb-count", len(databases)),
    ]:
        if index.get(key) != actual:
            print(
                f"Error: {index_name}: {key} is {index.get(key)}, "
                f"but the document describes {actual}"
            )
            sys.exit(1)

    # -- Every part that has a database must have it published, at the size
    # -- the index promises. Apio is dead in the water for a part whose
    # -- asset is missing or truncated, and nothing else would notice.
    # -- One check per FILE: the speed grades of a part share one asset.
    checked = {}
    for part_name, part in generated.items():
        asset_name = part["asset"]
        if asset_name in checked:
            continue
        checked[asset_name] = part_name
        asset = assets.get(asset_name)
        if asset is None:
            print(
                f"Error: part '{part_name}' needs asset "
                f"'{asset_name}', which this release does not publish"
            )
            sys.exit(1)
        if asset["size"] != part["asset-size"]:
            print(
                f"Error: asset '{asset_name}' is {asset['size']} "
                f"bytes, but the index says {part['asset-size']}"
            )
            sys.exit(1)

    print(
        f"Parts index OK ({len(parts)} parts, {len(generated)} of them "
        f"with a database, in {len(checked)} assets)"
    )


def find_parts_index(package_name: str, tag: str, assets: Dict) -> str:
    """Return the name of the release's parts index asset, or None if the
    release has none and is not required to have one."""

    # -- Preferred name, the one the document has inside the package.
    if PARTS_INDEX_NAME in assets:
        return PARTS_INDEX_NAME

    # -- Dated name. Asset names are derived from the tag's date, so it
    # -- must be the one named after this tag: an index from another
    # -- release describes another release's assets.
    dated = [n for n in assets if n.startswith(PARTS_INDEX_PREFIX)]
    assert len(dated) <= 1, dated
    if dated:
        expected_name = PARTS_INDEX_PREFIX + tag.replace("-", "") + ".json"
        if dated[0] != expected_name:
            print(
                f"Error: expected index '{expected_name}', "
                f"found '{dated[0]}'"
            )
            sys.exit(1)
        return dated[0]

    # -- No index. For a package that fetches its databases on demand that
    # -- is a broken release, not an old one, so do not pass it silently.
    required_from = PARTS_INDEX_REQUIRED_FROM.get(package_name)
    if required_from and tag >= required_from:
        print(
            f"Error: release '{tag}' of package '{package_name}' has no "
            f"parts index, and releases from '{required_from}' on need one"
        )
        sys.exit(1)

    return None


def check_parts_index(package_name: str, tag: str, assets: Dict):
    """Check the on-demand device databases of a release, if it has any.

    Packages whose device databases are fetched on demand (openxc7)
    publish an index asset that tells apio which database file to download
    for a given part. 'assets' maps the release's asset names to their
    github metadata."""

    index_name = find_parts_index(package_name, tag, assets)
    if index_name is None:
        return

    print()
    print(f"Checking parts index [{index_name}]")

    # -- Fetch the index. It is a small json (tens of KB). No github token
    # -- here: the download url redirects to blob storage, which rejects a
    # -- forwarded Authorization header.
    resp = requests.get(
        assets[index_name]["browser_download_url"], timeout=TIMEOUT
    )
    resp.raise_for_status()
    index = resp.json()

    # -- A different schema means the fields apio's loader reads were
    # -- renamed or reshaped.
    if index.get("schema") != PARTS_INDEX_SCHEMA_VERSION:
        print(
            f"Error: {index_name} has schema {index.get('schema')}, but "
            f"apio's loader expects schema {PARTS_INDEX_SCHEMA_VERSION}"
        )
        sys.exit(1)

    # -- The index names the release it belongs to. A mismatch sends apio
    # -- to the assets of another release.
    if index.get("release-tag") != tag:
        print(
            f"Error: {index_name} belongs to release "
            f"'{index.get('release-tag')}', not '{tag}'"
        )
        sys.exit(1)

    check_parts_index_content(index_name, index, assets)


def check_remote_config(jsonc_text: str):
    """Check a given remote config file given its content as a parsed json
    dict."""

    # -- Since the remote config files are .jsonc files with comments,
    # -- we use a json5 parser.
    json_data = json5.loads(jsonc_text)

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

        # if file_name != "apio-1.6.x.jsonc":
        #     continue

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

    print(f"\nDone (Check OK {files_checked} remote configs).")


if __name__ == "__main__":
    main()
