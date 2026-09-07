"""
Experimental program to collect information about Apio releases.
"""

# pylint: disable=fixme

# TODO: Change lists to dictionaries keyed by versions.

import re
import json
from typing import List
from datetime import datetime, date
from urllib.request import Request, urlopen
import ssl
from dataclasses import dataclass, asdict
from io import BytesIO
from zipfile import ZipFile
import certifi
from packaging.version import Version



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
class PypyReleaseCrawl:
    """Crawling information of a single Pypi Apio CLI release. See
    https://pypi.org/project/apio/#history
    """

    # -- The apio CLI version as appearing on Pypi.
    version: Version
    # -- The date on which the released for published on Pypi.
    publishing_date: date


@dataclass(frozen=True)
class PypiCrawl:
    """Pypi crawling information."""

    # -- The default release for 'pip install apio', this is considered the
    # -- 'latest' stable release.
    default_version: Version
    # -- List of Apio releases on Pypi.
    releases: List[PypyReleaseCrawl]
    # -- Version of Pypi releases that were skipped, e.g. for being too old.
    skipped_versions: List[Version]


@dataclass(frozen=True)
class VscodeReleaseCrawl:
    """Crawling information of a single VSCode Marketplace Apio IDE release.
    https://marketplace.visualstudio.com/items?itemName=fpgawars.apio
    """

    # -- The vscode extension release is it appears in the marketplace.
    version: Version
    # -- The date on which the release was published on the VSCode Marketplace.
    publishing_date: date
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
    default_version: Version
    # -- List of relevant releases that were crawled.
    releases: List[VscodeReleaseCrawl]
    # -- List of extension versions that were skipped, e.g. for being too old.
    skipped_versions: List[Version]


@dataclass(frozen=True)
class RemoteConfigPackageCrawl:
    """Crawling result of a single package configuration in a remote config file."""
    package_name: str
    package_release: GithubReleaseRef
    assets: List[str]


@dataclass(frozen=True)
class RemoteConfigFileCrawl:
    """Crawling results of a single remote config file."""
    # -- Two num version of the file, e.g. (1, 5) for "1.7.x"
    version_selector: Version
    # -- List of crawled package configurations..
    packages: RemoteConfigPackageCrawl


@dataclass(frozen=True)
class RemoteConfigCrawl:
    """Crawling results of all the remote config files."""
    remote_configs: List[RemoteConfigFileCrawl]


@dataclass(frozen=True)
class CrawlResults:
    """Crawl results"""

    # -- Results of crawling Apio CLI releases on Pypi.
    pypi_crawl: PypiCrawl
    # -- Results of crawling Apio VSCode releases on the VSCode Marketplace.
    vscode_marketplace_crawl: VscodeMarketplaceCrawl
    # -- Results of crawling the remote config files on fpgawars/apio.
    remote_configs_crawl: RemoteConfigCrawl


def _crawl_pypi() -> PypyReleaseCrawl:
    """Crawl pypi for Apio CLI releases."""

    # -- Query PyPi.
    api_url = "https://pypi.org/pypi/apio/json"
    with urlopen(api_url, context=_SSL_CONTEXT, timeout=30) as r:
        data = json.load(r)

    # -- Extract default Apio version on PyPi.
    default_version_str = data["info"]["version"]
    default_version = Version(default_version_str)

    # -- Collect the releases.
    releases: List[PypyReleaseCrawl] = []
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
        releases.append(PypyReleaseCrawl(version, publishing_time.date()))

    # -- Sort in place in decreasing version num.
    releases.sort(key=lambda r: r.version, reverse=True)

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


_VSCODE_PUBLISHER = "fpgawars"
_VSCODE_EXTENSION = "apio"
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

    releases = []
    skipped_versions: List[Version] = []

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

        releases.append(
            VscodeReleaseCrawl(
                version,
                last_updated_time.date(),
                GithubReleaseRef(repo, tag),
                # cli_version,
                GithubReleaseRef(apio_cli_repo, apio_cli_tag),
            )
        )

    return VscodeMarketplaceCrawl(
        releases[0].version, releases, skipped_versions
    )


def crawl() -> CrawlResults:
    """Crawl pypi, vscode market, and the apio related repos."""

    print("Crawling PyPi")
    pypi_crawl: PypiCrawl = _crawl_pypi()

    print("Crawling VSCode Marketplace")
    vscode_marketplace_crawl = _crawl_vscode_marketplace()

    print("Crawling done")

    return CrawlResults(pypi_crawl, vscode_marketplace_crawl, None)


def main():
    """Main function."""

    crawl_results = crawl()
    print("\nCrawl results:")
    print(json.dumps(asdict(crawl_results), indent=2, default=str))
    print()


if __name__ == "__main__":
    main()
