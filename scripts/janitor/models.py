"""
Contains the dataclasses that are used to communicate data
between janitor steps. Having them in a separate python
module resolves some issues with the pickling.
"""

from typing import List, Dict
from datetime import date
from dataclasses import dataclass
from packaging.version import Version

# ---------- Common


@dataclass(frozen=True, order=True)
class GithubReleaseRef:
    """Represents a single release on a github repo."""

    # -- The github repo. E.g. "fpgawars/apio"
    repo: str
    # -- The release tag, e.g. "2026-08-13"
    tag: str

    def __post_init__(self):
        """Assert repo is all lower case. Use 'fpgawars' and not 'FPGAWars'."""
        assert self.repo == self.repo.lower(), self

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return self.repo + " #" + self.tag


# ---------- Crawler output


@dataclass(frozen=True)
class PypiReleaseCrawl:
    """Crawling information of a single Pypi Apio CLI release. See
    https://pypi.org/project/apio/#history
    """

    # -- The apio CLI version as appearing on Pypi.
    # version: Version
    # -- The date on which the released for published on Pypi.
    published: date

    apio_cli_release: GithubReleaseRef

    # apio_cli_release_repo
    # apio_cli_release_tag: str


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
    """Crawling result of a single package configuration in a remote
    config file.
    """

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

    remote_configs: Dict[str, RemoteConfigFileCrawl]


@dataclass(frozen=True)
class CrawlResults:
    """Crawl results"""

    # -- Results of crawling Apio CLI releases on Pypi.
    pypi_crawl: PypiCrawl
    # -- Results of crawling Apio VSCode releases on the VSCode Marketplace.
    vscode_marketplace_crawl: VscodeMarketplaceCrawl
    # -- Results of crawling the remote config files on fpgawars/apio.
    remote_configs_crawl: RemoteConfigsCrawl


# ---------- Analyzer output


@dataclass(frozen=True)
class AnalysisResults:
    """Contains analysis reports."""

    should_be_stable: Dict[str, List[str]]
    should_be_latest: Dict[str, str]


# ---------- Checker output


@dataclass(frozen=True)
class CheckFailures:
    """Checks that failed."""

    missing: Dict[str, List[str]]
    non_stable: Dict[str, List[str]]
    non_latest: Dict[str, str]

    def has_failures(self) -> bool:
        """Returns True if has any error."""
        return (
            len(self.missing) > 0
            or len(self.non_stable) > 0
            or len(self.non_latest) > 0
        )


@dataclass(frozen=True)
class CheckSuccesses:
    """Checks that were successful."""

    releases_stable: Dict[str, List[str]]
    releases_latest: Dict[str, str]


@dataclass(frozen=True)
class CheckResults:
    """The results of the Repos Check step."""

    # -- We include an explicit passed field so we can easily access
    # -- it in bash script using jq.
    passed: bool
    failures: CheckFailures
    successes: CheckSuccesses

    def __post_init__(self):
        assert self.passed == (not self.has_failures())

    def has_failures(self) -> bool:
        """Returns True if has any error."""
        return self.failures.has_failures()
