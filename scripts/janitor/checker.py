"""
The third step of the Apio Repos Janitor workflow. It it reads the analyzer
requirements to check as a pickled AnalysisResults, performs the checks, and
output its results as a pickled CheckResults file.
"""

import os
from dataclasses import asdict, dataclass
import pickle
import json
import argparse
from pathlib import Path
from typing import List, Dict
import requests

from scripts.janitor import models

parser = argparse.ArgumentParser(
    description="Apio Repos Janitor's check phase."
)
parser.add_argument(
    "--work-dir",
    type=Path,
    default=Path("./_janitor"),
    help="Janitor's temp data dir (default = ./_janitor)",
)
args = parser.parse_args()


@dataclass(frozen=True)
class ReleaseStatus:
    """Release status lookup result. Note that is_latest requires a separate
    request to Github so not included here."""

    exists: bool
    is_draft: bool
    is_prerelease: bool
    is_stable: bool


def _github_release_status(repo: str, tag: str) -> ReleaseStatus:
    """Lookup the status of given release."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(
        f"https://api.github.com/repos/{repo}/releases/tags/{tag}",
        headers=headers,
        timeout=30,
    )
    if r.status_code == 404:
        return ReleaseStatus(
            exists=False,
            is_draft=False,
            is_prerelease=False,
            is_stable=False,
        )
    r.raise_for_status()
    data = r.json()

    is_draft = bool(data.get("draft"))
    is_prerelease = bool(data.get("prerelease"))
    return ReleaseStatus(
        exists=True,
        is_draft=is_draft,
        is_prerelease=is_prerelease,
        is_stable=not is_draft and not is_prerelease,
    )


def _github_release_is_latest(repo: str, tag: str) -> bool:
    """Test if given release exists and is 'latest'."""
    print(f"Verifying that {repo} #{tag} is latest.")

    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 404:
        return False
    r.raise_for_status()

    data = r.json()
    return data.get("tag_name") == tag


def check(analysis_results: models.AnalysisResults) -> models.CheckResults:
    """Check requirements from analysis report"""

    # -- Should-be-stable requests are split into these three dicts, two for
    # -- failures and one for success.
    missing: Dict[str, List[str]] = {}
    not_stable: Dict[str, List[str]] = {}
    is_stable: Dict[str, List[str]] = {}

    for repo, release_tags in analysis_results.should_be_stable.items():
        for release_tag in release_tags:
            release_status: ReleaseStatus = _github_release_status(
                repo, release_tag
            )
            if not release_status.exists:
                missing[repo] = missing.get(repo, []) + [release_tag]
            elif not release_status.is_stable:
                not_stable[repo] = not_stable.get(repo, []) + [release_tag]
            else:
                is_stable[repo] = is_stable.get(repo, []) + [release_tag]

    # -- Should-be-latest requests are split into these two dicts, one for
    # -- failure and one for success.
    not_latest: Dict[str, str] = {}
    is_latest: Dict[str, str] = {}
    for repo, release_tag in analysis_results.should_be_latest.items():
        if not _github_release_is_latest(repo, release_tag):
            not_latest[repo] = release_tag
        else:
            is_latest[repo] = release_tag

    check_failures = models.CheckFailures(
        missing,
        not_stable,
        not_latest,
        analysis_results.garbage_prereleases,
    )
    check_successes = (models.CheckSuccesses(is_stable, is_latest),)

    return models.CheckResults(
        not check_failures.has_failures(),
        check_failures,
        check_successes,
    )


def main():
    """Main for testing."""

    # -- Get the work dir path.
    work_dir_path = args.work_dir
    print(f"work_dir = {str(work_dir_path)}")

    # -- Load the crawler results
    with open(work_dir_path / "analysis_results.pkl", "rb") as f:
        analysis_results = pickle.load(f)

    # -- Check
    check_results: models.CheckResults = check(analysis_results)

    # -- Write results as json, for human consumption.
    (work_dir_path / "check_results.json").write_text(
        json.dumps(asdict(check_results), indent=2, default=str),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (work_dir_path / "check_results.pkl").open("wb") as f:
        pickle.dump(check_results, f)


if __name__ == "__main__":
    main()
