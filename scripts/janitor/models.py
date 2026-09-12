"""
Contains the dataclasses that are used to communicate data
between janitor steps. Having them in a separate python
module resolves some issues with the pickling.
"""

from typing import List, Dict, Any, Set
from datetime import date
from dataclasses import dataclass
from enum import Enum
from packaging.version import Version
from scripts.janitor import consts

# ---------- Common


@dataclass(frozen=True, order=True)
class GithubReleaseRef:
    """Represents a single release on a github repo."""

    # -- The github repo. E.g. "fpgawars/apio"
    repo: str
    # -- The release tag, e.g. "2026-08-13"
    tag: str

    def __post_init__(self):
        """Sanity checks."""
        assert self.repo == self.repo.lower(), self
        assert self.repo in consts.APIO_REPOS, self

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return self.repo + " #" + self.tag


class ReleaseState(Enum):
    """Represents the state of a release."""

    # -- Draft.
    DRAFT = "draft"
    # -- Pre-release.
    PRERELEASE = "pre-release"
    # -- Stable but not latest.
    STABLE = "stable"
    # -- Stable and latest (only one per repo)
    LATEST = "latest"

    @classmethod
    def from_flags(
        cls, draft: bool, prerelease: bool, is_latest: bool
    ) -> "ReleaseState":
        """Map github release flags to a state enum."""
        if draft:
            return cls.DRAFT
        if prerelease:
            return cls.PRERELEASE
        if is_latest:
            return cls.LATEST
        return cls.STABLE

    def __str__(self) -> str:
        """Using the string value as string representation. Used by json dumps
        when default=str.
        """
        return self.value

    @property
    def is_stable(self) -> bool:
        """Returns True if the release is stable."""
        return self in (ReleaseState.STABLE, ReleaseState.LATEST)

    @property
    def is_latest(self) -> bool:
        """Returns true if the release is marked as 'latest'."""
        return self is ReleaseState.LATEST


class ReleaseSet:
    """Represent a set of GithubReleaseRef that can be be grouped by
    repo."""

    def __init__(self, is_singular: bool):
        """Singular means that at most one release is allowed per
        repo."""
        self._is_singular = is_singular
        self._repos: Dict[str, Set[GithubReleaseRef]] = {}

    def __len__(self) -> int:
        """Allows to use len(release_set) to find the number of releases."""
        return sum(len(releases) for releases in self._repos.values())

    def __contains__(self, release: GithubReleaseRef) -> bool:
        """Allows to use 'release in set' operator"""
        assert isinstance(release, GithubReleaseRef), release
        repo_releases: Set[GithubReleaseRef] = self._repos.get(
            release.repo, set()
        )
        return release in repo_releases

    def add(self, release: GithubReleaseRef, *, may_exists: False) -> None:
        """Add a release reference to the set."""
        repo = release.repo
        # -- Case 1: This is the first for this repo.
        if repo not in self._repos:
            self._repos[repo] = set([release])
            return
        # -- Case 2: Repo already has at least one release.
        release_set = self._repos[repo]
        if not may_exists and release in release_set:
            raise ValueError(f"Release {release} already in set.")
        release_set.add(release)
        if self._is_singular and len(release_set) > 1:
            raise ValueError(
                f"Multiple releases in a singular ser: {release_set}."
            )

    def as_dict(self) -> Dict[str, Set[GithubReleaseRef]]:
        """Converts to a dict of repo -> release_ref."""
        return self._repos

    def items(self):
        """Allows for each iteration of (repo, releases)."""
        return self.as_dict().items()

    def releases(self) -> Set[GithubReleaseRef]:
        """Returns a set of all releases in the set."""
        all_releases: Set[GithubReleaseRef] = set()
        for s in self._repos.values():
            all_releases.update(s)
        return all_releases

    def as_tag_dict(self) -> Dict[str, List[str]]:
        """Converts to a dict of repo -> release_tag."""
        result = {}
        for repo in sorted(self._repos.keys()):
            tags = [r.tag for r in self._repos[repo]]
            # tags = sorted(self._repos[repo])
            tags = sorted(tags, reverse=True)
            result[repo] = tags
        return result

    def to_json_dict(self) -> Dict[str, Any]:
        """Return a dict that can be serialized to json. Called from
        the json serializer."""
        return self.as_tag_dict()

    def check_partitioning(
        self,
        partition1: "ReleaseSet",
        partition2: "ReleaseSet",
    ):
        """Check that partition1 and partition2 are proper partitioning of this
        set."""
        assert isinstance(partition1, ReleaseSet)
        assert isinstance(partition2, ReleaseSet)

        # -- Convert to plain sets of releases.
        self_releases = self.releases()
        releases1 = partition1.releases()
        releases2 = partition2.releases()

        # -- Check no dupes and no missing.
        assert releases1.isdisjoint(releases2)
        assert releases1.union(releases2) == self_releases


# ---------- Crawler output


@dataclass(frozen=True)
class PypiReleaseCrawl:
    """Crawling information of a single Pypi Apio CLI release. See
    https://pypi.org/project/apio/#history
    """

    # -- The date on which the released for published on Pypi.
    published: date

    # -- A reference to the Apio CLI release from which this pypi release
    # -- was created.
    apio_cli_release: GithubReleaseRef


@dataclass(frozen=True)
class PypiCrawl:
    """Pypi crawling information."""

    # -- The default release for 'pip install apio', this is considered the
    # -- 'latest' stable release.
    latest: Version
    # -- Dict from pypi release version to the release information.
    releases: Dict[str, PypiReleaseCrawl]
    # -- List of pypi apio releases that were skipped, either too old
    # -- or known to be problematic.
    skipped_versions: List[Version]


@dataclass(frozen=True)
class VscodeReleaseCrawl:
    """Crawling information of a single VSCode Marketplace Apio IDE release.
    https://marketplace.visualstudio.com/items?itemName=fpgawars.apio
    """

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
class ReleaseCrawl:
    """Represents crawl information of a single repo release."""

    state: ReleaseState
    created_date: date


@dataclass(frozen=True)
class RepoCrawl:
    """Results of crawling a single repo"""

    # -- Maps release tag to release info. Order is
    # -- descending created_date.
    releases: Dict[str, ReleaseCrawl]


@dataclass(frozen=True)
class ReposCrawl:
    """The repos crawling results."""

    repos: Dict[str, RepoCrawl]


@dataclass(frozen=True)
class CrawlResults:
    """Contains the output of the crawl step with all the information
    collected.
    """

    # -- Results of crawling Apio CLI releases on Pypi.
    pypi_crawl: PypiCrawl
    # -- Results of crawling Apio VSCode releases on the VSCode Marketplace.
    vscode_marketplace_crawl: VscodeMarketplaceCrawl
    # -- Results of crawling the remote config files on fpgawars/apio.
    remote_configs_crawl: RemoteConfigsCrawl
    # -- Results of crawling the repos.
    repos_crawl: ReposCrawl


# ---------- Analyzer output


@dataclass
class JanitorRequirements:
    """Requirements that need to be satisfied."""

    # -- Releases in use that should be stable (including latest)
    should_be_stable: ReleaseSet
    # -- Releases that should be marked latest
    should_be_latest: ReleaseSet  # Singleton
    # -- Prereleases and draft releases that are old enough to be deleted.
    should_be_deleted: ReleaseSet

    def check_partitioning(
        self,
        requirements1: "JanitorRequirements",
        requirements2: "JanitorRequirements",
    ):
        """Checks that the requirements in this object are properly
        partitioned into requirements1 and requirements2 with no missing or
        duplicates. The partitions typically represent success and failure
        sets.
        """
        self.should_be_stable.check_partitioning(
            requirements1.should_be_stable,
            requirements2.should_be_stable,
        )
        self.should_be_latest.check_partitioning(
            requirements1.should_be_latest,
            requirements2.should_be_latest,
        )
        self.should_be_deleted.check_partitioning(
            requirements1.should_be_deleted,
            requirements2.should_be_deleted,
        )

    def __post_init__(self):
        """Sanity checks."""
        assert isinstance(self.should_be_stable, ReleaseSet)
        assert isinstance(self.should_be_latest, ReleaseSet)
        assert isinstance(self.should_be_deleted, ReleaseSet)

    @classmethod
    def make_empty(cls) -> "JanitorRequirements":
        """Make a new Requirements that contains no requirements."""
        return JanitorRequirements(
            should_be_stable=ReleaseSet(is_singular=False),
            should_be_latest=ReleaseSet(is_singular=True),
            should_be_deleted=ReleaseSet(is_singular=False),
        )

    def is_empty(self) -> bool:
        """Returns True if there are no requirements."""
        return (
            len(self.should_be_stable) == 0
            and len(self.should_be_latest) == 0
            and len(self.should_be_deleted) == 0
        )


@dataclass(frozen=True)
class AnalysisResults:
    """Contains the result of the analysis step."""

    requirements: JanitorRequirements


# ---------- Fixer output


@dataclass(frozen=True)
class FixingResults:
    """The results of the Fixer step."""

    # TBD


# ---------- Verifier output


@dataclass(frozen=True)
class VerificationResults:
    """The results of the Verifier step."""

    # -- An explicit pass/fail flag to make it accessible for the
    # -- workflow using jq.
    passed: bool

    # -- Requirements that are not met.
    failures: JanitorRequirements
    # -- Requirements that are met.
    successes: JanitorRequirements

    def __post_init__(self):
        """Sanity check."""
        assert self.passed == self.failures.is_empty()
