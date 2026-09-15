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
# NUM_PRE_RELEASES_TO_KEEP = 3  # For testing

# -- Number of days before a draft release is deleted.
MAX_DRAFT_AGE_DAYS = 7

# -- Max age in days for the should-have-recent-release requirements. It's
# -- supposed to identify broken builds.
MAX_RECENT_RELEASE_DAYS = 1

# -- Set of Apio CLI PyPi releases that should be ignored.
PYPI_RELEASES_TO_IGNORE = {
    # -- New releases but broken.
    "1.5.0",  # Broken  apio CLI release 2026-06-19
    "1.4.2",  # Missing apio CLI release 2026-04-05
    "1.4.1",  # Missing apio CLI release 2026-04-05
    # --
    # -- Old releases, with old repos structures.
    "1.2.1",
    "1.2.0",
    "0.9.5",
    "0.9.4",
    "0.9.3",
    "0.9.2",
    "0.9.1",
    "0.8.4",
    "0.8.3",
    "0.8.2",
    "0.8.1",
    "0.8.0",
    "0.8.0.post1",
    "0.7.6",
    "0.7.5",
    "0.7.4",
    "0.7.3",
    "0.6rc2",
    "0.6rc1",
    "0.6.7",
    "0.6.6",
    "0.6.4",
    "0.6.3",
    "0.6.2",
    "0.6.1",
    "0.6.0",
    "0.5.6rc1",
    "0.5.4",
    "0.5.3",
    "0.5.2",
    "0.5.1",
    "0.5.0",
    "0.4.1",
    "0.4.0b5",
    "0.4.0b3",
    "0.4.0b2",
    "0.4.0b1",
    "0.4.0",
    "0.3.6",
    "0.3.5",
    "0.3.4b1",
    "0.3.4",
    "0.3.3",
    "0.3.2",
    "0.3.1",
    "0.3.0rc1",
    "0.3.0b5",
    "0.3.0b4",
    "0.3.0b3",
    "0.3.0b2",
    "0.3.0b1",
    "0.3.0",
    "0.2.4",
    "0.2.4.3",
    "0.2.4.2",
    "0.2.4.1",
    "0.2.3",
    "0.2.2",
    "0.2.2.2",
    "0.2.2.1",
    "0.2.1",
    "0.2.1.2",
    "0.2.1.1",
    "0.2.0",
    "0.1",
    "0.1.9.2",
    "0.1.9.1",
    "0.1.9.0",
    "0.1.8",
    "0.1.8.2",
    "0.1.7",
    "0.1.7.7",
    "0.1.7.6",
    "0.1.7.5",
    "0.1.7.4",
    "0.1.7.3",
    "0.1.7.2",
    "0.1.7.1",
    "0.1.6",
    "0.1.6.4",
    "0.1.6.3",
    "0.1.6.2",
    "0.1.6.1",
    "0.1.5",
    "0.1.5.1",
    "0.1.4",
    "0.1.3",
    "0.1.2",
    "0.1.2.3",
    "0.1.2.2",
    "0.1.2.1",
    "0.1.1.7",
    "0.1.1.6",
    "0.1.1.5",
    "0.1.1.4",
    "0.1.1.3",
    "0.1.1.2",
    "0.1.1.1",
    "0.1.0",  #
    "0.1.0.9",
    "0.1.0.8",
    "0.1.0.7",
    "0.1.0.6",
    "0.1.0.5",
    "0.1.0.4",
    "0.1.0.3",
    "0.1.0.2",
    "0.1.0.18",
    "0.1.0.17",
    "0.1.0.16",
    "0.1.0.15",
    "0.1.0.14",
    "0.1.0.13",
    "0.1.0.12",
    "0.1.0.11",
    "0.1.0.10",
    "0.1.0.1",
    "0.0.5",
    "0.0.5.2",
    "0.0.5.1",
    "0.0.4",
    "0.0.4.7",
    "0.0.4.6",
    "0.0.4.5",
    "0.0.4.4",
    "0.0.4.3",
    "0.0.4.2",
    "0.0.4.1",
    "0.0.3.9",
    "0.0.3.8",
    "0.0.3.7",
    "0.0.3.6",
    "0.0.3.5",
    "0.0.3.4",
    "0.0.3.3",
}

# -- Set of Apio Apio VSCode Marketplace releases that should be ignored.
VSCODE_MARKETPLACE_RELEASES_TO_IGNORE = {
    # -- Old releases, with old repos structures.
    "0.1.5",
    "0.1.4",
    "0.1.3",
    "0.1.2",
    "0.1.1",
    "0.1.0",
}
