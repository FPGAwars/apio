"""
Experimental program to collect information about Apio releases.
"""

# pylint: disable=fixme

# TODO: Change lists to dictionaries keyed by versions.
# TODO: Include in apio BUILD-INFO.json list of supported platforms.
# TODO: Allow to map from pypi to apio repo releases

import re
import json
import json5
from typing import List, Dict
from datetime import datetime, date
from urllib.request import Request, urlopen
import ssl
from dataclasses import dataclass, asdict
from io import BytesIO
from zipfile import ZipFile
import certifi
from packaging.version import Version

# APIO_PLATFORMS = ["darwin-arm64", "linux-x86-64", "windows-amd64"]

VERBOSE = False

# -- Used for outgoing https requests.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


# -- A regex to validate n.n.n version string.
_THREE_NUM_VERSION_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)


@dataclass(frozen=True)
class GithubReleaseRef:
    """Represents a single release on a github repo."""

    # -- The github repo. E.g. "fpgawars/apio"
    repo: str
    # -- The release tag, e.g. "2026-08-13"
    tag: str

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return self.repo + " #" + self.tag


@dataclass(frozen=True)
class PypiReleaseCrawl:
    """Crawling information of a single Pypi Apio CLI release. See
    https://pypi.org/project/apio/#history
    """

    # -- The apio CLI version as appearing on Pypi.
    # version: Version
    # -- The date on which the released for published on Pypi.
    published: date


@dataclass(frozen=True)
class PypiCrawl:
    """Pypi crawling information."""

    # -- The default release for 'pip install apio', this is considered the
    # -- 'latest' stable release.
    latest: Version
    # -- List of Apio releases on Pypi.
    # releases: List[PypiReleaseCrawl]
    releases: Dict[str, PypiReleaseCrawl]
    # -- Version of Pypi releases that were skipped, e.g. for being too old.
    skipped_versions: List[Version]


@dataclass(frozen=True)
class VscodeReleaseCrawl:
    """Crawling information of a single VSCode Marketplace Apio IDE release.
    https://marketplace.visualstudio.com/items?itemName=fpgawars.apio
    """

    # -- The vscode extension release is it appears in the marketplace.
    # version: Version
    # -- The date on which the release was published on the VSCode Marketplace.
    published: date
    # -- The github release of this extension version.
    apio_vscode_release: GithubReleaseRef
    # -- The github release of the underlying Apio CLI that is used by this
    # -- extension.
    apio_cli_release: GithubReleaseRef


@dataclass(frozen=True)
class VscodeMarketplaceCrawl:
    """VSCode Marketplace crawling information."""

    # -- The default Apio Vscode extension version. This considered to be the
    # -- 'latest' stable release.
    latest: Version
    # -- List of relevant releases that were crawled.
    releases: Dict[str, VscodeReleaseCrawl]
    # -- List of extension versions that were skipped, e.g. for being too old.
    skipped_versions: List[Version]


@dataclass(frozen=True)
class RemoteConfigPackageCrawl:
    """Crawling result of a single package configuration in a remote config file."""

    # -- Package repo and release tag
    package_release: GithubReleaseRef
    # -- True iff the asset contains a ${PLATFORM} placeholder.
    platform_dependent: bool
    # -- The asset name.
    asset: str


@dataclass(frozen=True)
class RemoteConfigFileCrawl:
    """Crawling results of a single remote config file."""

    # -- Two num version of the file, e.g. (1, 5) for "1.7.x"
    # version_selector: Version
    # -- List of crawled package configurations..
    packages: Dict[str, RemoteConfigPackageCrawl]


@dataclass(frozen=True)
class RemoteConfigsCrawl:
    """Crawling results of all the remote config files."""

    remote_configs: Dict[Version, RemoteConfigFileCrawl]


@dataclass(frozen=True)
class CrawlResults:
    """Crawl results"""

    # -- Results of crawling Apio CLI releases on Pypi.
    pypi_crawl: PypiCrawl
    # -- Results of crawling Apio VSCode releases on the VSCode Marketplace.
    vscode_marketplace_crawl: VscodeMarketplaceCrawl
    # -- Results of crawling the remote config files on fpgawars/apio.
    remote_configs_crawl: RemoteConfigsCrawl


def _crawl_pypi() -> PypiCrawl:
    """Crawl pypi for Apio CLI releases."""

    # -- Query PyPi.
    api_url = "https://pypi.org/pypi/apio/json"
    with urlopen(api_url, context=_SSL_CONTEXT, timeout=30) as r:
        data = json.load(r)

    # -- Extract default Apio version on PyPi.
    default_version_str = data["info"]["version"]
    default_version = Version(default_version_str)

    # -- Collect the releases.
    releases: Dict[str, PypiReleaseCrawl] = dict()
    skipped_versions: List[Version] = []
    for version_str, files in data["releases"].items():
        # -- Parse release string.
        version = Version(version_str)

        # -- Ignore releases that marked with 'yanked'.
        if not files or all(f.get("yanked") for f in files):
            skipped_versions.append(version)
            if VERBOSE:
                print(f"Skipped release {version_str:12} (yanked)")
            continue

        # -- Ignore 0.x releases. They are too old and don't use remote
        # -- config.
        if version.major < 1:
            skipped_versions.append(version)
            if VERBOSE:
                print(f"Skipped release {version_str:12} (old 0.x)")
            continue

        # -- At this point we expect the release string to be a clean
        # -- three numbers value.
        assert re.fullmatch(_THREE_NUM_VERSION_REGEX, version_str), version_str

        # -- Extract the publishing time.
        publishing_time_str = max(f["upload_time_iso_8601"] for f in files)
        publishing_time = datetime.fromisoformat(publishing_time_str)
        # print(f"{type(publishing_time)=}")

        # -- Append the release to the result list.
        assert str(version) not in releases
        releases[str(version)] = PypiReleaseCrawl(publishing_time.date())

    # -- Sort in place in decreasing semantic version key.
    releases = dict(sorted(releases.items(), key=lambda item: Version(item[0]), reverse=True))

    # -- All done ok.
    # return releases, skipped_versions
    return PypiCrawl(default_version, releases, skipped_versions)


# -- Microsoft VSCode Marketplace consts.
# https://learn.microsoft.com/en-us/javascript/api/azure-devops-extension-api/extensionqueryflags
_FLAG_INCLUDE_VERSIONS = 1
_FLAG_INCLUDE_FILES = 2
_FLAG_INCLUDE_VERSION_PROPERTIES = 16
_FLAG_INCLUDE_ASSET_URI = 128
_FLAG_INCLUDE_STATISTICS = 256


# _VSCODE_PUBLISHER = "fpgawars"
# _VSCODE_EXTENSION = "apio"
_MICROSOFT_VSIX_ASSET = "Microsoft.VisualStudio.Services.VSIXPackage"
_MICROSOFT_PRE_RELEASE = "Microsoft.VisualStudio.Code.PreRelease"


# -- Regex to extract the value of APIO_CLI_RELEASE_REPO from constants.js.
_REPO_RE = re.compile(
    r'^\s*const\s+APIO_CLI_RELEASE_REPO\s*=\s*"([^"]*)"\s*;\s*$',
    re.MULTILINE,
)

# -- Regex to extract the value of APIO_CLI_RELEASE_TAG from constants.js.
_TAG_RE = re.compile(
    r'^\s*const\s+APIO_CLI_RELEASE_TAG\s*=\s*"([^"]*)"\s*;\s*$',
    re.MULTILINE,
)


def _crawl_vscode_marketplace() -> VscodeMarketplaceCrawl:
    """Get info of last Apio IDE version on VSCode marketplace"""

    # pylint: disable=too-many-locals

    query_url = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"

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

    with urlopen(req, context=_SSL_CONTEXT, timeout=30) as r:
        data = json.load(r)

    releases:Dict[str, VscodeReleaseCrawl] = dict()
    skipped_versions: List[Version] = []
    default_version = None

    for rel in data["results"][0]["extensions"][0]["versions"]:

        version_str = rel["version"]
        version = Version(version_str)

        if version < Version("0.1.6"):
            skipped_versions.append(version)
            if VERBOSE:
                print(f"Skipping vscode version {version_str:8} (too old)")
            continue

        is_prerelease = any(
            p.get("key") == _MICROSOFT_PRE_RELEASE
            and str(p.get("value")).lower() == "true"
            for p in rel.get("properties") or []
        )
        if is_prerelease:
            skipped_versions.append(version)
            if VERBOSE:
                print(f"Skipping vscode version {version_str:8} (pre-release)")
            continue

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

        with urlopen(req, context=_SSL_CONTEXT, timeout=30) as resp:
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
        releases[str(version)] = (
            VscodeReleaseCrawl(
                # version,
                last_updated_time.date(),
                GithubReleaseRef(repo, tag),
                # cli_version,
                GithubReleaseRef(apio_cli_repo, apio_cli_tag),
            )
        )
    # default_version = releases.keys()[0]


    assert default_version is not None
    return VscodeMarketplaceCrawl(
        default_version, releases, skipped_versions
    )


# -- Regex to parse remote config file names.
_REMOTE_CONFIG_NAME_REGEX = re.compile(r"^apio-(\d+)\.(\d+)\.x\.jsonc$")


def _crawl_remote_configs() -> RemoteConfigsCrawl:

    url = "https://api.github.com/repos/FPGAwars/apio/contents/remote-config"
    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "apio-script",
        },
    )

    with urlopen(req, context=_SSL_CONTEXT, timeout=30) as resp:
        entries = json.loads(resp.read().decode("utf-8"))

    # print(json.dumps(entries, indent=2))

    # -- Iterate files
    files_crawls: Dict[str, RemoteConfigFileCrawl] = dict()
    for entry in entries:
        package_name = entry["name"]
        if package_name in ["README.md"]:
            continue
        # print(f"{package_name=}")
        m = _REMOTE_CONFIG_NAME_REGEX.match(package_name)
        assert m, package_name
        version = Version(f"{m.group(1)}.{m.group(2)}")
        # print(str(version))

        download_url = entry["download_url"]
        req = Request(download_url, headers={"User-Agent": "apio-script"})

        with urlopen(req, context=_SSL_CONTEXT, timeout=30) as resp:
            remote_config_text = resp.read().decode("utf-8")

        # print("*****")
        # print(remote_config_text)

        remote_config_json = json5.loads(remote_config_text)

        packages_crawls: Dict[str, RemoteConfigPackageCrawl] = dict()

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

            # assert_platform_dependent = "${PLATFORM}" in asset

            # assets = set()
            # for platform in APIO_PLATFORMS:
            #     asset = asset.replace("${PLATFORM}", platform)
            #     assets.add(asset)

            # assets = list(assets)
            # assets.sort(reverse=True)

            assert package_name not in packages_crawls
            packages_crawls[package_name] = RemoteConfigPackageCrawl(
                # package_name,
                GithubReleaseRef(package_repo, package_tag),
                "${PLATFORM}" in asset,
                asset,
            )

        key = str(version)
        assert key not in files_crawls
        files_crawls[key]= RemoteConfigFileCrawl(packages_crawls)
        

    return RemoteConfigsCrawl(files_crawls)

    # print(f"{entries=}")
    # return None


def crawl() -> CrawlResults:
    """Crawl pypi, vscode market, and the apio related repos."""

    print("Crawling PyPi")
    pypi_crawl: PypiCrawl = _crawl_pypi()

    print("Crawling VSCode Marketplace")
    vscode_marketplace_crawl = _crawl_vscode_marketplace()

    print("Crawling Remote Configs")
    remote_configs_crawl = _crawl_remote_configs()

    # print(json.dumps(asdict(remote_configs_crawl), indent=2, default=str))

    print("Crawling done")

    return CrawlResults(pypi_crawl, vscode_marketplace_crawl, remote_configs_crawl)


def main():
    """Main function."""

    crawl_results = crawl()
    print("\nCrawl results:")
    print(json.dumps(asdict(crawl_results), indent=2, default=str))
    print()


if __name__ == "__main__":
    main()
