"""
This step of the apio repos janitor reads the requirements from the
analyzer step and classifies them as failures (not met) and success (met),
write the results to a file and generated a human readable markdown
report.
"""

from typing import Optional, List, Set
from dataclasses import asdict, dataclass
import pickle
import json
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

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

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
    for repo, releases in requirements.release_should_be_stable.items():
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
                successes.release_should_be_stable.add(release)
            else:
                failures.release_should_be_stable.add(release)

    # -- Iterate the 'should be latest' requirements and partition them to
    # -- success and failures.
    for repo, releases in requirements.release_should_be_latest.items():
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
                successes.release_should_be_latest.add(release)

            else:
                failures.release_should_be_latest.add(release)

    # -- Process the release_should_be_consistent requirements.

    for repo, releases in requirements.release_should_be_consistent.items():
        assert repo == "fpgawars/tools-openxc7", repo
        for release in releases:
            # -- Older version didn't have the parts index so we just
            # -- assume they are ok.
            if release.tag < "2026-09-10":
                successes.release_should_be_consistent.add(release)
                continue

            print(f"Checking consistency of release {release}")

            # -- Get the parts index and collect the chipdb file names.
            json_bytes = util.download_release_asset(
                release, "XILINX-PARTS-INDEX.json"
            )
            index = json.loads(json_bytes)
            index_chipdbs: Set[str] = set()
            for part in index["parts"].values():
                chipdb_asset = part.get("asset", None)
                if chipdb_asset:
                    index_chipdbs.add(chipdb_asset)
            print(f"index_chipdbs has {len(index_chipdbs)} members.")

            # -- Get the release metadata and collects the asset chipdb
            release_metadata = util.download_release_metadata(release)
            assets_chipdbs: Set[str] = set()
            for asset_name in release_metadata.assets.keys():
                if asset_name.startswith("apio-xilinx-chipdb-"):
                    assets_chipdbs.add(asset_name)
            print(f"assets_chipdbs has {len(assets_chipdbs)} members.")

            # -- The two sets should be identical
            ok = index_chipdbs == assets_chipdbs
            if ok:
                successes.release_should_be_consistent.add(release)
            else:
                only_in_index = sorted(index_chipdbs - assets_chipdbs)
                only_in_assets = sorted(assets_chipdbs - index_chipdbs)
                print(f"*** Release {release} chipdb mismatch")
                print(f"{only_in_index=}")
                print(f"{only_in_assets=}")
                failures.release_should_be_consistent.add(release)

    # TODO: The logic of verifying the draft and the releases are very
    # similar, consider to refactor to a shared method.

    # -- Iterate the 'draft_should_be_deleted' requirements and
    # -- partition them to success and failures.
    for repo, releases in requirements.draft_should_be_deleted.items():
        # -- Get repo crawl information.
        # -- We expect the repo to be in the crawling data.
        repo_crawl: models.RepoCrawl = fresh_repo_crawl.repos[repo]
        # -- Iterate and check if the releases exist.
        for release in releases:
            assert isinstance(release, models.GithubReleaseRef)
            assert release.repo == repo
            # -- Determine if the draft exists.
            release_crawl: Optional[models.ReleaseCrawl] = (
                repo_crawl.releases.get(release.tag, None)
            )
            # -- Save this requirement as a success or failure.
            if release_crawl is None:
                successes.draft_should_be_deleted.add(release)
            else:
                failures.draft_should_be_deleted.add(release)

    # -- Iterate the 'pre_release_should_be_deleted' requirements and
    # -- partition them to success and failures.
    for repo, releases in requirements.pre_release_should_be_deleted.items():
        # -- Get repo crawl information.
        # -- We expect the repo to be in the crawling data.
        repo_crawl: models.RepoCrawl = fresh_repo_crawl.repos[repo]
        # -- Iterate and check if the releases exist.
        for release in releases:
            assert isinstance(release, models.GithubReleaseRef)
            assert release.repo == repo
            # -- Determine if the prerelease exists.
            release_crawl: Optional[models.ReleaseCrawl] = (
                repo_crawl.releases.get(release.tag, None)
            )
            # -- Save this requirement as a success or failure.
            if release_crawl is None:
                successes.pre_release_should_be_deleted.add(release)
            else:
                failures.pre_release_should_be_deleted.add(release)

    # -- Check that the requirements from the analyzer are properly
    # -- partitioned among the failures and successes.
    requirements.check_partitioning(failures, successes)

    # -- All done.
    return models.VerificationResults(
        failures.is_empty(),
        failures,
        successes,
    )


def _generate_markdown_report(
    verification_results: models.VerificationResults,
) -> str:
    """Generates a markdown report for human consumption with the verification
    results."""
    lines = []
    # -- Get the failing requirements
    failures: models.JanitorRequirements = verification_results.failures
    if failures.is_empty():
        lines.append("No errors found.")
        return "\n".join(lines)

    # -- Get a sorted list of the repos that have at least one failure
    active_repos: List[str] = sorted(failures.get_repos())
    assert len(active_repos) > 1

    lines.append("**Error founds**")

    # -- Generate a report section for each repo.
    for repo in active_repos:
        lines.append("\n<br>\n")
        lines.append(f"**{repo}**")

        # for title, release_set in sections.items():
        for field_name, release_set in failures.release_sets().items():
            title = field_name.replace("_", " ").capitalize()
            releases = release_set.repo_releases(repo)
            if not releases:
                continue
            lines.append(f"- {title}")
            for release in releases:
                release_link = (
                    f"[{release.tag}]"
                    + f"(https://github.com/{repo}/releases/tag/"
                    + f"{release.tag})"
                )
                lines.append(f"  - {release_link}")

    # -- All done.
    return "\n".join(lines)


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
    args = parser.parse_args()

    # -- Get the work dir path.
    janitor_data_dir = args.janitor_data_dir
    print(f"janitor_data_dir = {str(janitor_data_dir)}")

    # -- Load the analyzer results
    with open(janitor_data_dir / "analysis-results.pkl", "rb") as f:
        analysis_results = pickle.load(f)

    # -- Verify
    verification_results: models.VerificationResults = verify(analysis_results)

    # -- Write results as json, for human consumption.
    (janitor_data_dir / "verification-results.json").write_text(
        util.to_json_text(asdict(verification_results)),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (janitor_data_dir / "verification-results.pkl").open("wb") as f:
        pickle.dump(verification_results, f)

    # -- Write markdown report.
    (janitor_data_dir / "verification-results.md").write_text(
        _generate_markdown_report(verification_results),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
