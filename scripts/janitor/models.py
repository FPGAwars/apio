"""
Contains the dataclasses that are used to communicate data
between janitor steps. Having them in a separate python
module resolves some issues with the pickling.
"""

from typing import List, Dict, Any, Set, Optional
from datetime import date
from dataclasses import dataclass, field
from enum import Enum
from packaging.version import Version
from scripts.janitor import consts

# ---------- Common


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


def _check_repo_str(repo: str):
    """Check repo string."""
    assert repo == repo.lower(), repo
    assert repo in consts.APIO_REPOS, repo


# def _check_release_tag_str(release_tag: str):
#     """Check release tag string."""
#     # -- This throws an exception if not yyyy-mm-dd of a valid date.
#     d = datetime.strptime(release_tag, "%Y-%m-%d").date()
#     assert 2000 <= d.year < 2100


def _repo_and_tag_to_str(repo: str, tag: str) -> str:
    """Convert repo and release tag string to a string for humans."""
    _check_repo_str(repo)
    # _check_release_tag_str(tag)
    return f"{repo} #{tag}"


@dataclass(frozen=True)
class GithubReleaseRef:
    """A reference to an Apio github repo."""

    repo: str
    release_tag: str

    def __post_init__(self):
        """Sanity checks."""
        _check_repo_str(self.repo)
        # _check_release_tag_str(self.release_tag)

    def __str__(self) -> str:
        """Human friendly representation of the object."""
        return _repo_and_tag_to_str(self.repo, self.release_tag)


class RequirementType(Enum):
    """Represents the state of a release."""

    RELEASE_SHOULD_BE_STABLE = "release-should-be-stable"
    RELEASE_SHOULD_BE_LATEST = "release-should-be-latest"
    RELEASE_SHOULD_BE_CONSISTENT = "release-should-be-consistent"
    DRAFT_SHOULD_BE_DELETED = "draft-should-be-deleted"
    PRERELEASE_SHOULD_BE_DELETED = "prerelease-should-be-deleted"
    REPO_SHOULD_HAVE_A_RECENT_BUILD = "repo-should-have-a-recent-build"

    @property
    def is_repo_scope(self) -> bool:
        """Returns true if this requirement type is of repo scope and thus
        should not contain release tag"""
        return self in {
            RequirementType.REPO_SHOULD_HAVE_A_RECENT_BUILD,
        }

    @property
    def is_release_scope(self) -> bool:
        """Returns true if this requirement type is of release scope and thus
        should contain a release tag"""
        return not self.is_repo_scope


# @dataclass(frozen=True, kw_only=True, order=True)
@dataclass(frozen=True, order=True)
class Requirement:
    """Represent a requirement that should met."""

    # -- The requirement type.
    req_type: RequirementType
    # -- The repo name, e.g. "fpgawars/apio"
    repo: str
    # -- The release tag, only if req_type.is_repo_scope.
    release_tag: Optional[str]
    # -- List of notes regarding the processing of the requirement.
    # -- This field does not participate in comparison or set lookup.
    notes: List[str] = field(compare=False)

    def __post_init__(self):
        """Sanity checks."""
        assert self.repo == self.repo.lower(), self
        assert self.repo in consts.APIO_REPOS, self
        assert (self.release_tag is None) == self.req_type.is_repo_scope
        assert isinstance(self.notes, list)

    def release_ref(self) -> GithubReleaseRef:
        """Return a reference for the underlying release of this requirement.
        Applies only to requirements of release scope."""
        assert self.req_type.is_release_scope
        assert self.release_tag is not None
        return GithubReleaseRef(self.repo, self.release_tag)

    def append_note(self, note: str) -> "Requirement":
        """Append note to self.notes. Returns self."""
        self.notes.append(note)
        return self


class RequirementsSet:
    """A set of Requirement with Janitor specific operations."""

    def __init__(self) -> None:
        self._members: Set[Requirement] = set()

    def add(self, requirement: Requirement) -> None:
        """Add a member to the set. If already in the set, the notes of the
        new requirements are appended to the one in the set."""
        assert isinstance(requirement, Requirement)
        for existing in self._members:
            if existing == requirement:
                existing.notes.extend(requirement.notes)
                return
        self._members.add(requirement)

    # def add_with_verifier_note(
    #     self, requirement: Requirement, verifier_note: str
    # ) -> None:
    #     """A shortcut for adding a requirement while attaching to it
    #     a verifier note"""
    #     self.add(requirement.copy_with_verifier_note(verifier_note))

    def add_by_ref(
        self,
        req_type: RequirementType,
        release_ref: GithubReleaseRef,
        notes: List[str],
    ) -> None:
        """Similar to add() but from different args."""
        self.add(
            Requirement(
                req_type=req_type,
                repo=release_ref.repo,
                release_tag=release_ref.release_tag,
                notes=notes,
            )
        )

    def __len__(self) -> int:
        """Allows to use len(release_set) to find the number of releases."""
        return len(self._members)

    def __contains__(self, requirement: Requirement) -> bool:
        """Allows to use 'requirement in set' operator"""
        assert isinstance(requirement, Requirement)
        return requirement in self._members

    def group_by_repo_and_type(
        self,
    ) -> Dict[str, Dict[RequirementType, List[Requirement]]]:
        """Return all the members as a repo/type/requirement tree. The tree
        is sorted for intuitive order."""
        # -- Sort by
        # --    repo (ascending),
        # --    requirement type (ascending),
        # --    release tag (descending)
        members = sorted(
            self._members, key=lambda r: r.release_tag or "", reverse=True
        )
        members = sorted(members, key=lambda r: (r.repo, r.req_type.value))

        # -- Construct the tree.
        result: Dict[str, Dict[RequirementType, List[Requirement]]] = {}
        for req in members:
            by_type = result.setdefault(req.repo, {})
            by_type.setdefault(req.req_type, []).append(req)
        return result

    def group_by_type_and_repo(
        self,
    ) -> Dict[RequirementType, Dict[str, List[Requirement]]]:
        """Return all the members as a type/repo/requirement tree."""
        # --    requirement type (ascending),
        # --    repo (ascending),
        # --    release tag (descending)
        members = sorted(
            self._members, key=lambda r: r.release_tag or "", reverse=True
        )
        members = sorted(members, key=lambda r: (r.req_type.value, r.repo))

        # -- Construct the tree.
        result: Dict[RequirementType, Dict[str, List[Requirement]]] = {}
        for req in members:
            by_repo = result.setdefault(req.req_type, {})
            by_repo.setdefault(req.repo, []).append(req)
        return result

    def repos(self) -> Set[str]:
        """Return a set of repos that have at least one requirement."""
        return {m.repo for m in self._members}

    def members(self) -> Set[Requirement]:
        """Returns a flat set of all members."""
        return self._members

    def members_of_type(self, req_type: RequirementType) -> Set[Requirement]:
        """Return the subset of requirements of given type."""
        return {req for req in self._members if req.req_type == req_type}

    # TODO: Tweak the json tree.
    def to_json_dict(self) -> Dict[str, Any]:
        """Return a dict that can be serialized to json. Called from
        the json serializer. The returned dict is tweaked for human
        consumption and does not necessarily contain all the information."""

        def requirement_type_to_key(req_type: RequirementType) -> str:
            return req_type.name.lower().replace("_", "-")

        def requirement_to_dict(requirement: Requirement) -> Dict[str, Any]:
            # -- We drop the req_type and repo fields which which already
            # -- appear in the dict tree in the path to this item.
            result: Dict[str, Any] = {}
            if requirement.req_type.is_release_scope:
                result["release_tag"] = requirement.release_tag
            if requirement.notes:
                result["notes"] = requirement.notes
            return result

        result: Dict[str, Dict[str, Any]] = {}
        for req_type, by_repo in self.group_by_type_and_repo().items():
            for repo, requirements in by_repo.items():
                result.setdefault(repo, {})[
                    requirement_type_to_key(req_type)
                ] = [requirement_to_dict(req) for req in requirements]
        return result

    def check_partitioning(
        self,
        partition1: "RequirementsSet",
        partition2: "RequirementsSet",
    ):
        """Check that partition1 and partition2 are proper partitioning of this
        set."""
        assert isinstance(partition1, RequirementsSet)
        assert isinstance(partition2, RequirementsSet)

        # -- Check that there are no dupes and no missing.
        members1 = partition1.members()
        members2 = partition2.members()

        assert members1.isdisjoint(members2)
        assert members1.union(members2) == self._members


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
    skipped_versions: List[str]


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
    skipped_versions: List[str]


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
    published_date: date


@dataclass(frozen=True)
class RepoCrawl:
    """Results of crawling a single repo"""

    # -- Maps release tag to release info. Order is
    # -- descending published_date.
    releases: Dict[str, ReleaseCrawl]


@dataclass(frozen=True)
class ReposCrawl:
    """The repos crawling results."""

    repos: Dict[str, RepoCrawl]

    def get_release_crawl(
        self, release: GithubReleaseRef, default: Any
    ) -> ReleaseCrawl | Any:
        """Lookup the given release crawl. If found, return it, otherwise
        return 'default'."""
        assert isinstance(release, GithubReleaseRef)

        # -- Lookup at repo level
        repo_crawl = self.repos.get(release.repo, None)
        if repo_crawl is None:
            return default

        # -- Lookup at release tag level
        assert isinstance(repo_crawl, RepoCrawl)
        release_crawl = repo_crawl.releases.get(release.release_tag, None)
        if repo_crawl is None:
            return default

        # -- All done.
        assert isinstance(release_crawl, ReleaseCrawl)
        return release_crawl


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


# # ---------- Analyzer output


@dataclass
class AnalysisResults:
    """Analyzer results."""

    requirements: RequirementsSet


# ---------- Verifier output


@dataclass(frozen=True)
class VerificationResults:
    """The results of the Verifier step."""

    # -- An explicit pass/fail flag to make it accessible for the
    # -- workflow using jq.
    passed: bool

    # -- Requirements that are not met.
    failures: RequirementsSet
    # -- Requirements that are met.
    successes: RequirementsSet

    def __post_init__(self):
        """Sanity check."""
        assert self.passed == (len(self.failures) == 0)
