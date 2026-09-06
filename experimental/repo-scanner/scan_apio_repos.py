"""
Experimental program to collect information about Apio releases.
"""

import re
import json
from typing import List
from datetime import datetime
from urllib.request import Request, urlopen
import ssl
from dataclasses import dataclass
from io import BytesIO
from zipfile import ZipFile
import certifi
from packaging.version import Version

# -- Used for outgoing https requests.
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


# -- A regex to validate n.n.n version string.
THREE_NUM_VERSION_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)

@dataclass(frozen=True)
class GithubRelease:
    """Represents a single release on a github repo."""
    # -- The github repo. E.g. "fpgawars/apio"
    repo: str
    # -- The release tag, e.g. "2026-08-13"
    tag: str

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return (
            self.repo
            + " #"
            + self.tag
        )


@dataclass(frozen=True)
class PyPiRelease:
    """Represents information extracted from a PyPi Apio CLI release."""

    version: Version
    dt: datetime
    is_default: bool

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return (
            "["
            + str(self.version)
            + ", "
            + self.dt.strftime("%Y-%m-%d")
            + "]"
            + ("*" if self.is_default else "")
        )


def get_relevant_apio_pypi_releases() -> list[PyPiRelease]:
    """Return the newest n versions of the PyPI 'apio' project."""

    # -- Query PyPi.
    api_url = "https://pypi.org/pypi/apio/json"
    with urlopen(api_url, context=SSL_CONTEXT, timeout=30) as r:
        data = json.load(r)

    # -- Extract default Apio version on PyPi.
    default_version_str = data["info"]["version"]
    default_version = Version(default_version_str)

    # -- Collect the releases.
    result: List[PyPiRelease] = []
    default_version_matches = 0
    for version_str, files in data["releases"].items():
        # -- Parse release string.
        version = Version(version_str)

        # -- Ignore releases that marked with 'yanked'.
        if not files or all(f.get("yanked") for f in files):
            print(f"Skipped release {version_str:12} (yanked)")
            continue

        # -- Ignore 0.x releases. They are too old and don't use remote
        # -- config.
        if version.major < 1:
            print(f"Skipped release {version_str:12} (old 0.x)")
            continue

        # -- At this point we expect the release string to be a clean
        # -- three numbers value.
        assert re.fullmatch(THREE_NUM_VERSION_REGEX, version_str), version_str

        # -- Extract the publishing time.
        publishing_time_str = max(f["upload_time_iso_8601"] for f in files)
        publishing_time = datetime.fromisoformat(publishing_time_str)
        # print(f"{type(publishing_time)=}")

        # -- Determine if this is the default version.
        is_default = version == default_version
        if is_default:
            default_version_matches += 1

        # -- Append the release to the result list.
        result.append(PyPiRelease(version, publishing_time, is_default))

    # -- Check that exactly one version matches the default version.
    assert default_version_matches == 1, (
        default_version,
        default_version_matches,
    )

    # -- Sort in place in decreasing version num.
    result.sort(key=lambda r: r.version, reverse=True)

    # -- All done ok.
    return result


# -- Microsoft VSCode Marketplace consts.
# https://learn.microsoft.com/en-us/javascript/api/azure-devops-extension-api/extensionqueryflags
INCLUDE_VERSIONS = 1
INCLUDE_FILES = 2
INCLUDE_VERSION_PROPERTIES = 16
INCLUDE_ASSET_URI = 128
INCLUDE_STATISTICS = 256


@dataclass(frozen=True)
class VscodeMarketplaceRelease:
    """Represents information extracted from a VSCode Marketplace Apio CLI release."""

    version: Version
    dt: datetime
    is_default: bool
    apio_cli_version: Version
    github_release: GithubRelease

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return (
            "["
            + str(self.version)
            + ", "
            + self.dt.strftime("%Y-%m-%d")
            + ", apio_cli=("
            + str(self.apio_cli_version)
            + ", "
            + str(self.github_release)
            + ")]"
            + ("*" if self.is_default else "")
        )


VSCODE_PUBLISHER = "fpgawars"
VSCODE_EXTENSION = "apio"
MICROSOFT_VSIX_ASSET = "Microsoft.VisualStudio.Services.VSIXPackage"
MICROSOFT_PRE_RELEASE = "Microsoft.VisualStudio.Code.PreRelease"


# -- Regex to extract the value of APIO_CLI_RELEASE_REPO from constants.js.
REPO_RE = re.compile(
    r'^\s*const\s+APIO_CLI_RELEASE_REPO\s*=\s*"([^"]*)"\s*;\s*$',
    re.MULTILINE,
)

# -- Regex to extract the value of APIO_CLI_RELEASE_TAG from constants.js.
TAG_RE = re.compile(
    r'^\s*const\s+APIO_CLI_RELEASE_TAG\s*=\s*"([^"]*)"\s*;\s*$',
    re.MULTILINE,
)


def get_relevant_apio_vscode_marketplace_releases():
    """Get info of last Apio IDE version on VSCode marketplace"""

    # pylint: disable=too-many-locals

    query_url = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"

    flags = (
        INCLUDE_VERSIONS
        | INCLUDE_FILES
        | INCLUDE_VERSION_PROPERTIES
        | INCLUDE_ASSET_URI
        | INCLUDE_STATISTICS
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

    with urlopen(req, context=SSL_CONTEXT, timeout=30) as r:
        data = json.load(r)

    # print("\nData:")
    # print(json.dumps(data, indent=2, sort_keys=True))
    # print()

    result = []

    for rel in data["results"][0]["extensions"][0]["versions"]:



        version_str = rel["version"]
        version = Version(version_str)

        # print("\n\n")
        # print(f"***** vscode {version_str} *****\n")

        if version < Version("0.1.6"):
            print(f"Skipping vscode version {version_str:8} (too old)")
            continue

        is_prerelease = any(
            p.get("key") == MICROSOFT_PRE_RELEASE
            and str(p.get("value")).lower() == "true"
            for p in rel.get("properties") or []
        )
        if is_prerelease:
            print(f"Skipping vscode version {version_str:8} (pre-release)")
            continue

        # print(f"\n----- {version_str}")
        # print(json.dumps(rel, indent=2, sort_keys=True))
        # print()

        last_updated_time_str = rel["lastUpdated"]
        last_updated_time = datetime.fromisoformat(last_updated_time_str)

        vsix_url = next(
            f["source"]
            for f in rel.get("files") or []
            if f.get("assetType") == MICROSOFT_VSIX_ASSET
        )
        assert vsix_url

        req = Request(
            vsix_url,
            headers={"User-Agent": "apio-dev-scanner", "Accept": "*/*"},
        )

        with urlopen(req, context=SSL_CONTEXT, timeout=30) as resp:
            package = resp.read()

        with ZipFile(BytesIO(package)) as zf:
            extracted = zf.read("extension/src/constants.js").decode("utf-8")

        # print(extracted)

        cli_repo = REPO_RE.search(extracted).group(1)
        cli_tag = TAG_RE.search(extracted).group(1)

        url = f"https://raw.githubusercontent.com/{cli_repo}/{cli_tag}/apio/__init__.py"
        apio_init_py = (
            urlopen(url, context=SSL_CONTEXT, timeout=30)
            .read()
            .decode("utf-8")
        )

        # print(apio_init_py)

        APIO_VERSION_RE = (
            r"VERSION\s*=\s*\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\)"
        )
        m = re.search(APIO_VERSION_RE, apio_init_py)
        cli_version = Version(f"{m.group(1)}.{m.group(2)}.{m.group(3)}")

        # -- By the order of the returned items, the first version that is not
        # -- skipped is the default one (latest)
        is_default = len(result) == 0

        result.append(
            VscodeMarketplaceRelease(
                version,
                last_updated_time,
                is_default,
             
                cli_version,
                GithubRelease(   cli_repo,
                                cli_tag)
            )
        )

    return result


def main():
    """Main function."""

    # -- Extract Pypi's apio versions.
    print("\nQuerying PyPi")
    apio_pypi_releases = get_relevant_apio_pypi_releases()
    print(f"\nCollected {len(apio_pypi_releases)} PyPi releases:")
    for r in apio_pypi_releases:
        print(f"- {r}")

    # -- Extract VSCode Marketplace's apio versions.
    print("\nQuerying VSCode Marketplace")
    apio_vscode_releases = get_relevant_apio_vscode_marketplace_releases()
    print(f"\nCollected {len(apio_vscode_releases)} VScode releases:")
    for r in apio_vscode_releases:
        print(f"- {r}")


if __name__ == "__main__":
    main()
