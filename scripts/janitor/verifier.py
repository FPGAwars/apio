"""
This step of the apio repos janitor reads the requirements from the
analyzer step and classifies them as failures (not met) or success (met).
It is invoked twice, once before the fixer (pre) and once after the fixer
(post).
"""

from typing import Optional
from dataclasses import asdict, dataclass
import pickle
import argparse
from pathlib import Path
from scripts.janitor import models, crawler, util


@dataclass(frozen=True)
class ReleaseStatus:
    """Release status lookup result. Note that is_latest requires a separate
    request to Github so not included here."""

    exists: bool
    is_draft: bool
    is_prerelease: bool
    is_stable: bool


def verify(
    analysis_results: models.AnalysisResults,
) -> models.VerificationResults:
    """Verifies that the analyzer requirements where fixed."""

    # -- Perform a fresh crawl of the repos.
    fresh_repo_crawl: models.ReposCrawl = crawler.crawl_apio_repos()

    # -- The requirement from the analyzer
    requirements: models.JanitorRequirements = analysis_results.requirements

    # -- We are going to partitions the requirements into successes and
    # -- failures.
    failures: models.JanitorRequirements = (
        models.JanitorRequirements.make_empty()
    )
    successes: models.JanitorRequirements = (
        models.JanitorRequirements.make_empty()
    )

    # -- Iterate the 'should be stable' requirements and partition them to
    # -- success and failures.
    for repo, releases in requirements.should_be_stable.items():
        # -- Get the garbage releases of this repo.
        # -- We expect the repo to be in the crawling data.
        repo_crawl: models.RepoCrawl = fresh_repo_crawl.repos[repo]
        assert isinstance(repo_crawl, models.RepoCrawl)
        for release in releases:
            assert isinstance(release, models.GithubReleaseRef)
            assert release.repo == repo

            # -- Determine if this release exists and is stable.
            release_crawl: Optional[models.ReleaseCrawl] = (
                repo_crawl.releases.get(release.tag, None)
            )
            is_stable = (
                release_crawl is not None and release_crawl.state.is_stable
            )

            # -- Save this requirement as a success or failure.
            if is_stable:
                successes.should_be_stable.add(release, may_exists=False)
            else:
                failures.should_be_stable.add(release, may_exists=False)

    # -- Iterate the 'should be latest' requirements and partition them to
    # -- success and failures.
    for repo, releases in requirements.should_be_latest.items():
        # -- Get the garbage releases of this repo.
        # -- We expect the repo to be in the crawling data.
        repo_crawl: models.RepoCrawl = fresh_repo_crawl.repos[repo]
        assert isinstance(repo_crawl, models.RepoCrawl)
        for release in releases:
            assert isinstance(release, models.GithubReleaseRef)
            assert release.repo == repo

            # -- Determine if this release is latest.
            release_crawl: Optional[models.ReleaseCrawl] = (
                repo_crawl.releases.get(release.tag, None)
            )
            is_latest = (
                release_crawl is not None and release_crawl.state.is_latest
            )

            # -- Save this requirement as a success or failure.
            if is_latest:
                successes.should_be_latest.add(release, may_exists=False)

            else:
                failures.should_be_latest.add(release, may_exists=False)

    # -- Iterate the 'garbage pre-releases' requirements and partition them to
    # -- success and failures.
    for repo, releases in requirements.should_be_deleted.items():
        # -- Get the garbage releases of this repo.
        # -- We expect the repo to be in the crawling data.
        repo_crawl: models.RepoCrawl = fresh_repo_crawl.repos[repo]
        # -- Iterate the garbage releases of this repo
        for release in releases:
            assert isinstance(release, models.GithubReleaseRef)
            assert release.repo == repo
            # -- Determine if the release exists.
            release_crawl: Optional[models.ReleaseCrawl] = (
                repo_crawl.releases.get(release.tag, None)
            )

            # release_state = repo_crawl.get(release_tag.tag, None)
            # -- Save this requirement as a success or failure.
            if release_crawl is None:
                successes.should_be_deleted.add(release, may_exists=False)

            else:
                failures.should_be_deleted.add(release, may_exists=False)

    # -- Check that the requirements from the analyzer are properly
    # -- partitioned among the failures and successes.
    requirements.check_partitioning(failures, successes)

    # -- All done.
    return models.VerificationResults(
        failures.is_empty(),
        failures,
        successes,
    )


def main():
    """Program entry point."""

    parser = argparse.ArgumentParser(
        description="Apio Repos Janitor's verification phase."
    )
    parser.add_argument(
        "--janitor-data-dir",
        type=Path,
        required=True,
        help="Janitor's temp data dir",
    )
    parser.add_argument(
        "--phase",
        required=True,
        help="The verification phase, determines output file names.",
    )
    args = parser.parse_args()

    # -- Get the work dir path.
    janitor_data_dir = args.janitor_data_dir
    print(f"janitor_data_dir = {str(janitor_data_dir)}")

    phase = args.phase
    print(f"phase = {phase}")

    # -- Load the analyzer results
    with open(janitor_data_dir / "analysis-results.pkl", "rb") as f:
        analysis_results = pickle.load(f)

    # -- Verify
    verification_results: models.VerificationResults = verify(analysis_results)

    # -- Write results as json, for human consumption.
    (janitor_data_dir / f"{phase}-verification-results.json").write_text(
        util.to_json_text(asdict(verification_results)),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (janitor_data_dir / f"{phase}-verification-results.pkl").open(
        "wb"
    ) as f:
        pickle.dump(verification_results, f)


if __name__ == "__main__":
    main()
