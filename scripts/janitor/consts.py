"""
Janitor consts
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RepoAttributes:
    """Represents the attributes of an Apio repo."""

    daily_builds: bool
    check_consistency: bool


# -- Set of apio repos. This set should match the repo list in apio docs
# -- https://fpgawars.github.io/apio/docs/apio-repositories
# --
# -- The repo fpgawars/apio-workflows is not included since it's is not part
# -- of the Apio releases.
APIO_REPOS = {
    # -- Publishing roots.
    "fpgawars/apio": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    "fpgawars/apio-vscode": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    # -- packages
    "fpgawars/apio-definitions": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    "fpgawars/tools-drivers": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    "fpgawars/tools-graphviz": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    "fpgawars/tools-openxc7": RepoAttributes(
        daily_builds=True, check_consistency=True
    ),
    "fpgawars/tools-oss-cad-suite": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    "fpgawars/tools-verible": RepoAttributes(
        daily_builds=True, check_consistency=False
    ),
    "fpgawars/apio-examples": RepoAttributes(
        daily_builds=False, check_consistency=False  # Frozen repo
    ),
}


# -- The number of latest prereleases to keep in each repo.
# -- Currently each repo keeps at most 5 pre-releases so
# -- we add a small margin here.
NUM_PRE_RELEASES_TO_KEEP = 7

# -- Number of days before a draft release is deleted.
MAX_DRAFT_AGE_DAYS = 7

# -- Max age in days for the should-have-recent-release requirements. It's
# -- supposed to identify broken builds.
MAX_RECENT_RELEASE_DAYS = 2
