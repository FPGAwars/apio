"""
This is the first step of the apio repos janitor, it collects information
from pypi, vscode market, and apio repos and writes it to file.
"""

import re
import json
import pickle
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import argparse
from urllib.request import Request, urlopen
from dataclasses import asdict
from io import BytesIO
from zipfile import ZipFile
import requests
import json5
from packaging.version import Version
from scripts.janitor import util, consts
from scripts.janitor.models import (
    GithubReleaseRef,
    PypiCrawl,
    PypiReleaseCrawl,
    CrawlResults,
    VscodeMarketplaceCrawl,
    RemoteConfigsCrawl,
    ReposCrawl,
    ReleaseState,
    RepoCrawl,
    VscodeReleaseCrawl,
    RemoteConfigFileCrawl,
    RemoteConfigPackageCrawl,
    ReleaseCrawl,
)

# -- A regex to validate n.n.n version string.
_THREE_NUM_VERSION_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)


# -- Used to extract apio cli release tag from __init__.py of old PyPi
# -- releases. For newer releases we include that information in
# -- pyproject.toml.
_RELEASE_INFO_RE = re.compile(r'RELEASE_INFO\s*=\s*"(generic-)?pypi-([^"]*)"')


def _crawl_pypi() -> PypiCrawl:
    """Crawl pypi for Apio CLI releases."""

    print("Crawling PyPi.")

    # -- Query PyPi.
    api_url = "https://pypi.org/pypi/apio/json"
    with urlopen(api_url, context=util.SSL_REQUEST_CONTEXT, timeout=30) as r:
        json_data = json.load(r)

    # -- Extract default Apio version on PyPi.
    default_version_str = json_data["info"]["version"]
    default_version = Version(default_version_str)

    # -- Collect the releases.
    releases: Dict[str, PypiReleaseCrawl] = {}
    skipped_versions: List[str] = []
    for version_str, files in json_data["releases"].items():

        if version_str in consts.PYPI_RELEASES_TO_IGNORE:
            skipped_versions.append(version_str)
            print(f"Skipping Pypi release {version_str:12} (ignore list)")
            continue

        # -- Ignore releases that marked with 'yanked'.
        if not files or all(f.get("yanked") for f in files):
            skipped_versions.append(version_str)
            print(f"Skipping pypi release {version_str:12} (yanked)")
            continue

        # -- At this point we expect the release string to be a clean
        # -- three numbers value.
        assert re.fullmatch(_THREE_NUM_VERSION_REGEX, version_str), version_str

        # -- Parse version string.
        version = Version(version_str)

        # -- Extract the publishing time.
        publishing_time_str = max(f["upload_time_iso_8601"] for f in files)
        publishing_time = datetime.fromisoformat(publishing_time_str)

        # -- Extract the apio release that was used to publish this pypi
        # -- release.
        init_py_text = util.download_file_from_pypi_apio_release(
            version_str, "apio/__init__.py"
        )

        match = _RELEASE_INFO_RE.search(init_py_text)
        apio_cli_tag = match.group(2)

        # -- Append the release to the result list.
        assert str(version) not in releases
        releases[str(version)] = PypiReleaseCrawl(
            publishing_time.date(),
            GithubReleaseRef("fpgawars/apio", apio_cli_tag),
        )

    # -- Sort in place in decreasing semantic version key.
    releases = dict(
        sorted(
            releases.items(), key=lambda item: Version(item[0]), reverse=True
        )
    )

    # -- Sort in place in descending order.
    skipped_versions.sort(reverse=True)

    # -- All done ok.
    return PypiCrawl(default_version, releases, skipped_versions)


# -- Microsoft VSCode Marketplace consts.
# https://learn.microsoft.com/en-us/javascript/api/azure-devops-extension-api/extensionqueryflags
_FLAG_INCLUDE_VERSIONS = 1
_FLAG_INCLUDE_FILES = 2
_FLAG_INCLUDE_VERSION_PROPERTIES = 16
_FLAG_INCLUDE_ASSET_URI = 128
_FLAG_INCLUDE_STATISTICS = 256

_MICROSOFT_VSIX_ASSET = "Microsoft.VisualStudio.Services.VSIXPackage"
_MICROSOFT_PRE_RELEASE = "Microsoft.VisualStudio.Code.PreRelease"


def _crawl_vscode_marketplace() -> VscodeMarketplaceCrawl:
    """Get info of last Apio IDE version on VSCode marketplace"""

    # pylint: disable=too-many-locals

    print("Crawling VSCode marketplace.")

    query_url = (
        "https://marketplace.visualstudio.com/"
        + "_apis/public/gallery/extensionquery"
    )

    flags = (
        _FLAG_INCLUDE_VERSIONS
        | _FLAG_INCLUDE_FILES
        | _FLAG_INCLUDE_VERSION_PROPERTIES
        | _FLAG_INCLUDE_ASSET_URI
        | _FLAG_INCLUDE_STATISTICS
    )

    body = {
        "filters": [
            {
                "criteria": [{"filterType": 7, "value": "fpgawars.apio"}],
                "pageNumber": 1,
                "pageSize": 1,
            }
        ],
        "flags": flags,
    }

    req = Request(
        query_url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json;api-version=7.2-preview.1",
            "User-Agent": "apio-dev-scanner",
        },
        method="POST",
    )

    with urlopen(req, context=util.SSL_REQUEST_CONTEXT, timeout=30) as r:
        data = json.load(r)

    releases: Dict[str, VscodeReleaseCrawl] = {}
    skipped_versions: List[str] = []
    default_version = None

    for rel in data["results"][0]["extensions"][0]["versions"]:

        version_str = rel["version"]

        if version_str in consts.VSCODE_MARKETPLACE_RELEASES_TO_IGNORE:
            skipped_versions.append(version_str)
            print(f"Skipping vscode release {version_str:8} (ignore list)")
            continue

        is_prerelease = any(
            p.get("key") == _MICROSOFT_PRE_RELEASE
            and str(p.get("value")).lower() == "true"
            for p in rel.get("properties") or []
        )
        if is_prerelease:
            skipped_versions.append(version_str)
            print(f"Skipping vscode version {version_str:8} (pre-release)")
            continue

        # -- At this point we expect the release string to be a clean
        # -- three numbers value.
        assert re.fullmatch(_THREE_NUM_VERSION_REGEX, version_str), version_str

        # -- Parse the version.
        version = Version(version_str)

        last_updated_time_str = rel["lastUpdated"]
        last_updated_time = datetime.fromisoformat(last_updated_time_str)

        vsix_url = next(
            f["source"]
            for f in rel.get("files") or []
            if f.get("assetType") == _MICROSOFT_VSIX_ASSET
        )
        assert vsix_url

        req = Request(
            vsix_url,
            headers={"User-Agent": "apio-dev-scanner", "Accept": "*/*"},
        )

        with urlopen(
            req, context=util.SSL_REQUEST_CONTEXT, timeout=30
        ) as resp:
            vsix_package = resp.read()

        if version <= Version("0.1.9"):
            build_info_member = "extension/build-info.json"
        else:
            build_info_member = "extension/BUILD-INFO.json"

        with ZipFile(BytesIO(vsix_package)) as zf:
            build_info_text = zf.read(build_info_member).decode("utf-8")

        build_info_json = json.loads(build_info_text)

        # print(extracted)
        repo = build_info_json["source-repo"].lower()
        tag = build_info_json["apio-ide-release-tag"]
        apio_cli_repo = build_info_json["apio-cli-release-repo"]
        apio_cli_tag = build_info_json["apio-cli-release-tag"]

        # -- First item is the 'latest' or default.
        if default_version is None:
            default_version = version

        assert str(version) not in releases
        releases[str(version)] = VscodeReleaseCrawl(
            # version,
            last_updated_time.date(),
            GithubReleaseRef(repo, tag),
            # cli_version,
            GithubReleaseRef(apio_cli_repo, apio_cli_tag),
        )
    # default_version = releases.keys()[0]

    assert default_version is not None
    return VscodeMarketplaceCrawl(default_version, releases, skipped_versions)


# -- Regex to parse remote config file names.
_REMOTE_CONFIG_NAME_REGEX = re.compile(r"^apio-(\d+)\.(\d+)\.x\.jsonc$")


def _crawl_remote_configs() -> RemoteConfigsCrawl:
    """Crawls the latest version of the apio remote config files."""

    # pylint: disable=too-many-locals

    print("Crawling apio remote configs.")

    url = "https://api.github.com/repos/FPGAwars/apio/contents/remote-config"
    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "apio-script",
            **util.github_headers(),
        },
    )

    with urlopen(req, context=util.SSL_REQUEST_CONTEXT, timeout=30) as resp:
        entries = json.loads(resp.read().decode("utf-8"))

    # -- Iterate files
    files_crawls: Dict[str, RemoteConfigFileCrawl] = {}
    for entry in entries:
        package_name = entry["name"]
        if package_name in ["README.md"]:
            continue
        m = _REMOTE_CONFIG_NAME_REGEX.match(package_name)
        assert m, package_name
        version = Version(f"{m.group(1)}.{m.group(2)}")

        download_url = entry["download_url"]
        req = Request(download_url, headers={"User-Agent": "apio-script"})

        with urlopen(
            req, context=util.SSL_REQUEST_CONTEXT, timeout=30
        ) as resp:
            remote_config_text = resp.read().decode("utf-8")

        remote_config_json = json5.loads(remote_config_text)

        packages_crawls: Dict[str, RemoteConfigPackageCrawl] = {}

        for package_name, package_config in remote_config_json[
            "packages"
        ].items():
            # print(package_name)

            package_repo = (
                package_config["repository"]["organization"]
                + "/"
                + package_config["repository"]["name"]
            )
            package_tag = package_config["release"]["tag"]
            asset = package_config["release"]["package"]

            yyyymmdd = package_tag.replace("-", "")
            asset = asset.replace("${YYYYMMDD}", yyyymmdd)

            assert package_name not in packages_crawls
            packages_crawls[package_name] = RemoteConfigPackageCrawl(
                # package_name,
                GithubReleaseRef(package_repo, package_tag),
                "${PLATFORM}" in asset,
                asset,
            )

        key = str(version)
        assert key not in files_crawls
        files_crawls[key] = RemoteConfigFileCrawl(packages_crawls)

    return RemoteConfigsCrawl(files_crawls)


def _crawl_apio_repo(repo: str) -> RepoCrawl:
    """Crawl a single repo and get its releases states."""
    headers = {
        "Accept": "application/vnd.github+json",
        **util.github_headers(),
    }

    latest_tag = None
    latest = requests.get(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers=headers,
        timeout=30,
    )
    if latest.status_code != 404:
        latest.raise_for_status()
        latest_tag = latest.json().get("tag_name")

    releases: Dict[str, ReleaseState] = {}
    url = f"https://api.github.com/repos/{repo}/releases"
    params = {"per_page": 100}
    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        params = None
        for release in resp.json():
            release_tag = release["tag_name"]
            # if release_tag in {"v1.5.0"}:
            #     print(f"Skipping blacklisted {repo} {release_tag}")
            #     continue
            release_state = ReleaseState.from_flags(
                draft=bool(release.get("draft")),
                prerelease=bool(release.get("prerelease")),
                is_latest=release_tag == latest_tag,
            )
            published_date = datetime.fromisoformat(
                release["published_at"]
            ).date()
            releases[release_tag] = ReleaseCrawl(release_state, published_date)
        url = resp.links.get("next", {}).get("url")

    # -- Sort the releases by descending order of published_date.
    releases = dict(
        sorted(
            releases.items(),
            key=lambda item: item[1].published_date,
            reverse=True,
        )
    )

    return RepoCrawl(releases)


def crawl_apio_repos() -> ReposCrawl:
    """Crawl the given repos. This function is called multiple times
    during the execution of the janitor, including from other steps,
    since the state of the apio repos may be changed by the fixing
    step."""

    print("Crawling apio repos.")

    repos_dict: Dict[str, Dict[str, ReleaseState]] = {}
    for repo in consts.APIO_REPOS:
        repo_crawl = _crawl_apio_repo(repo)
        repos_dict[repo] = repo_crawl

    return ReposCrawl(repos_dict)


def crawl() -> CrawlResults:
    """Crawl pypi, vscode market, and the apio related repos."""

    # -- Crawl the various sources.
    pypi_crawl: PypiCrawl = _crawl_pypi()
    vscode_marketplace_crawl = _crawl_vscode_marketplace()
    remote_configs_crawl = _crawl_remote_configs()
    repos_crawl = crawl_apio_repos()

    # -- All done.
    print("Crawling done")
    return CrawlResults(
        pypi_crawl,
        vscode_marketplace_crawl,
        remote_configs_crawl,
        repos_crawl,
    )


def main():
    """Program entry point."""

    parser = argparse.ArgumentParser(
        description="Apio Repos Janitor's crawl phase."
    )
    parser.add_argument(
        "--janitor-data-dir",
        type=Path,
        help="Janitor's temp data dir",
    )
    args = parser.parse_args()

    # -- Get the work dir path.
    janitor_data_dir = args.janitor_data_dir
    print(f"janitor_data_dir = {str(janitor_data_dir)}")
    janitor_data_dir.mkdir(parents=True, exist_ok=True)

    # -- Do the crawling.
    crawl_results: CrawlResults = crawl()

    # -- Write results as json, for human consumption.
    (janitor_data_dir / "crawl-results.json").write_text(
        json.dumps(asdict(crawl_results), indent=2, default=str),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (janitor_data_dir / "crawl-results.pkl").open("wb") as f:
        pickle.dump(crawl_results, f)


if __name__ == "__main__":
    main()
