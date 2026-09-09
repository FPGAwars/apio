"""
The first step of the Apio Repos Janitor workflow. It scans the repos and
PyPi and VSCode Marketplace and outputs a pickled CrawlResults file with its
results.
"""

import re
import json
import tarfile
import pickle
import urllib.request
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import argparse
from urllib.request import Request, urlopen
import ssl
from dataclasses import asdict
from io import BytesIO
from zipfile import ZipFile
import json5
import certifi
from packaging.version import Version
from scripts.janitor import models

parser = argparse.ArgumentParser(
    description="Apio Repos Janitor's crawl phase."
)
parser.add_argument(
    "--work-dir",
    type=Path,
    default=Path("./_janitor"),
    help="Janitor's temp data dir (default = ./_janitor)",
)
args = parser.parse_args()


# -- Used for outgoing https requests.
_SSL_REQUEST_CONTEXT = ssl.create_default_context(cafile=certifi.where())


# -- A regex to validate n.n.n version string.
_THREE_NUM_VERSION_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)


def read_file_from_pypi_apio_release(
    version: str, file_path_in_package: str
) -> str:
    """Read a text file from a pypi apio release"""
    meta_url = f"https://pypi.org/pypi/apio/{version}/json"
    with urllib.request.urlopen(
        meta_url, context=_SSL_REQUEST_CONTEXT
    ) as resp:
        data = json.load(resp)
    tarball_url = next(
        (
            item["url"]
            for item in data["urls"]
            if item["packagetype"] == "sdist"
        ),
        None,
    )

    assert tarball_url, meta_url

    with urllib.request.urlopen(
        tarball_url, context=_SSL_REQUEST_CONTEXT
    ) as resp:
        blob = resp.read()
    with tarfile.open(fileobj=BytesIO(blob), mode="r:gz") as tf:
        suffix = "/" + file_path_in_package
        member = next(
            (
                m
                for m in tf.getmembers()
                if m.name.endswith(suffix) and m.isfile()
            ),
            None,
        )
        if member is None:
            raise FileNotFoundError(file_path_in_package)
        with tf.extractfile(member) as f:
            return f.read().decode("utf-8")


# -- Used to extract apio cli release tag from __init__.py of old PyPi
# -- releases. For newer releases we include that information in
# -- pyproject.toml.
_RELEASE_INFO_RE = re.compile(r'RELEASE_INFO\s*=\s*"(generic-)?pypi-([^"]*)"')


def _crawl_pypi() -> models.PypiCrawl:
    """Crawl pypi for Apio CLI releases."""

    # -- Query PyPi.
    api_url = "https://pypi.org/pypi/apio/json"
    with urlopen(api_url, context=_SSL_REQUEST_CONTEXT, timeout=30) as r:
        data = json.load(r)

    # -- Extract default Apio version on PyPi.
    default_version_str = data["info"]["version"]
    default_version = Version(default_version_str)

    # -- Collect the releases.
    releases: Dict[str, models.PypiReleaseCrawl] = {}
    skipped_versions: List[Version] = []
    for version_str, files in data["releases"].items():
        # print(f"{version_str=}")
        # -- Parse release string.
        version = Version(version_str)

        # -- Ignore releases that marked with 'yanked'.
        if not files or all(f.get("yanked") for f in files):
            skipped_versions.append(version)
            print(f"Skipped release {version_str:12} (yanked)")
            continue

        # -- Ignore 0.x releases. They are too old and don't use remote
        # -- config.
        if version <= Version("1.2.1"):
            skipped_versions.append(version)
            print(f"Skipped release {version_str:12} (old)")
            continue

        if version in [Version("1.5.0")]:
            skipped_versions.append(version)
            print(f"Skipped release {version_str:12} (blacklisted)")
            continue

        # -- At this point we expect the release string to be a clean
        # -- three numbers value.
        assert re.fullmatch(_THREE_NUM_VERSION_REGEX, version_str), version_str

        # -- Extract the publishing time.
        publishing_time_str = max(f["upload_time_iso_8601"] for f in files)
        publishing_time = datetime.fromisoformat(publishing_time_str)

        # -- Extract the apio release that was used to publish this pypi
        # -- release.
        init_py_text = read_file_from_pypi_apio_release(
            version_str, "apio/__init__.py"
        )

        match = _RELEASE_INFO_RE.search(init_py_text)
        apio_cli_tag = match.group(2)

        # -- Append the release to the result list.
        assert str(version) not in releases
        releases[str(version)] = models.PypiReleaseCrawl(
            publishing_time.date(),
            models.GithubReleaseRef("fpgawars/apio", apio_cli_tag),
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
    # return releases, skipped_versions
    return models.PypiCrawl(default_version, releases, skipped_versions)


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


def _crawl_vscode_marketplace() -> models.VscodeMarketplaceCrawl:
    """Get info of last Apio IDE version on VSCode marketplace"""

    # pylint: disable=too-many-locals

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

    with urlopen(req, context=_SSL_REQUEST_CONTEXT, timeout=30) as r:
        data = json.load(r)

    releases: Dict[str, models.VscodeReleaseCrawl] = {}
    skipped_versions: List[Version] = []
    default_version = None

    for rel in data["results"][0]["extensions"][0]["versions"]:

        version_str = rel["version"]
        version = Version(version_str)

        if version < Version("0.1.6"):
            skipped_versions.append(version)
            print(f"Skipping vscode version {version_str:8} (too old)")
            continue

        is_prerelease = any(
            p.get("key") == _MICROSOFT_PRE_RELEASE
            and str(p.get("value")).lower() == "true"
            for p in rel.get("properties") or []
        )
        if is_prerelease:
            skipped_versions.append(version)
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

        with urlopen(req, context=_SSL_REQUEST_CONTEXT, timeout=30) as resp:
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
        releases[str(version)] = models.VscodeReleaseCrawl(
            # version,
            last_updated_time.date(),
            models.GithubReleaseRef(repo, tag),
            # cli_version,
            models.GithubReleaseRef(apio_cli_repo, apio_cli_tag),
        )
    # default_version = releases.keys()[0]

    assert default_version is not None
    return models.VscodeMarketplaceCrawl(
        default_version, releases, skipped_versions
    )


# -- Regex to parse remote config file names.
_REMOTE_CONFIG_NAME_REGEX = re.compile(r"^apio-(\d+)\.(\d+)\.x\.jsonc$")


def _crawl_remote_configs() -> models.RemoteConfigsCrawl:
    """Crawls the latest version of the apio remote config files."""

    # pylint: disable=too-many-locals

    url = "https://api.github.com/repos/FPGAwars/apio/contents/remote-config"
    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "apio-script",
        },
    )

    with urlopen(req, context=_SSL_REQUEST_CONTEXT, timeout=30) as resp:
        entries = json.loads(resp.read().decode("utf-8"))

    # print(json.dumps(entries, indent=2))

    # -- Iterate files
    files_crawls: Dict[str, models.RemoteConfigFileCrawl] = {}
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

        with urlopen(req, context=_SSL_REQUEST_CONTEXT, timeout=30) as resp:
            remote_config_text = resp.read().decode("utf-8")

        # print("*****")
        # print(remote_config_text)

        remote_config_json = json5.loads(remote_config_text)

        packages_crawls: Dict[str, models.RemoteConfigPackageCrawl] = {}

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
            packages_crawls[package_name] = models.RemoteConfigPackageCrawl(
                # package_name,
                models.GithubReleaseRef(package_repo, package_tag),
                "${PLATFORM}" in asset,
                asset,
            )

        key = str(version)
        assert key not in files_crawls
        files_crawls[key] = models.RemoteConfigFileCrawl(packages_crawls)

    return models.RemoteConfigsCrawl(files_crawls)


def crawl() -> models.CrawlResults:
    """Crawl pypi, vscode market, and the apio related repos."""

    print("Crawling PyPi")
    pypi_crawl: models.PypiCrawl = _crawl_pypi()

    print("Crawling VSCode Marketplace")
    vscode_marketplace_crawl = _crawl_vscode_marketplace()

    print("Crawling Remote Configs")
    remote_configs_crawl = _crawl_remote_configs()

    # print(json.dumps(asdict(remote_configs_crawl), indent=2, default=str))

    print("Crawling done")

    return models.CrawlResults(
        pypi_crawl, vscode_marketplace_crawl, remote_configs_crawl
    )


def main():
    """Main function."""

    # -- Get the work dir path.
    work_dir_path = args.work_dir
    print(f"work_dir = {str(work_dir_path)}")
    work_dir_path.mkdir(parents=True, exist_ok=True)

    # -- Do the crawling.
    crawl_results: models.CrawlResults = crawl()

    # -- Write results as json, for human consumption.
    (work_dir_path / "crawl_results.json").write_text(
        json.dumps(asdict(crawl_results), indent=2, default=str),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (work_dir_path / "crawl_results.pkl").open("wb") as f:
        pickle.dump(crawl_results, f)


if __name__ == "__main__":
    main()
