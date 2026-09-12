"""
This step of the apio repos janitor reads the crawler data and writes to
a file a list of requirements that should be met.
"""

from dataclasses import asdict
from datetime import date
import pickle
import argparse
from pathlib import Path
from scripts.janitor import models, consts, util


def analyze(crawl_results: models.CrawlResults) -> models.AnalysisResults:
    """Analyze crawling results and generate requirements report."""

    # pylint: disable=too-many-locals

    # -- A container for the requirements that the analyzer generates.
    # requirements = models.JanitorRequirements({}, {}, {})
    requirements = models.JanitorRequirements.make_empty()

    # -- Each vscode release and the cli releases that it refers to should
    # -- be stable.
    for _, rc in crawl_results.vscode_marketplace_crawl.releases.items():
        requirements.should_be_stable.add(
            rc.apio_vscode_release, may_exists=False
        )
        requirements.should_be_stable.add(
            rc.apio_cli_release, may_exists=False
        )

    # -- All packages that are refereed by a remote config should be stable.
    for _, rc in crawl_results.remote_configs_crawl.remote_configs.items():
        for _, package in rc.packages.items():
            requirements.should_be_stable.add(
                package.package_release, may_exists=True
            )

    # -- The apio vscode release of the latest vscode market release should
    # -- be marked as latest.
    vscode_crawl = crawl_results.vscode_marketplace_crawl
    vscode_latest_release = vscode_crawl.releases[str(vscode_crawl.latest)]
    # apio_vscode_latest_release = vscode_latest_release.apio_vscode_release
    requirements.should_be_latest.add(
        vscode_latest_release.apio_vscode_release, may_exists=False
    )

    # -- The cli release that is the latest on pypi should be latest in the
    # -- apio repository.
    pypi_crawl = crawl_results.pypi_crawl
    pypi_latest_release = pypi_crawl.releases[str(pypi_crawl.latest)]
    # apio_cli_latest_release = pypi_latest_release.apio_cli_release
    requirements.should_be_latest.add(
        pypi_latest_release.apio_cli_release, may_exists=False
    )

    # -- The apio packages releases that are referred by the remote config
    # -- of the latest apio CLI should be marked latest.
    latest_remote_config_key = (
        str(pypi_crawl.latest.major) + "." + str(pypi_crawl.latest.minor)
    )
    latest_remote_config = crawl_results.remote_configs_crawl.remote_configs[
        latest_remote_config_key
    ]
    for _, package in latest_remote_config.packages.items():
        requirements.should_be_latest.add(
            package.package_release, may_exists=False
        )

    # -- Identify the old prereleases that should be deleted.

    today: date = date.today()
    for repo, repo_crawl in crawl_results.repos_crawl.repos.items():
        prereleases_kept = 0
        # -- Iterate releases and process pre-releases. The order is
        # -- in decreasing created_date value.
        for release_tag, release_crawl in repo_crawl.releases.items():
            release = models.GithubReleaseRef(repo, release_tag)

            # -- Case 1: Release is in use.
            if release in requirements.should_be_stable:
                continue

            # -- Case 2: Release is a draft.
            if release_crawl.state == models.ReleaseState.DRAFT:
                draft_date = release_crawl.created_date
                draft_age_days = (today - draft_date).days
                # -- Mark for deletion if too old.
                if draft_age_days > consts.MAX_DRAFT_AGE_DAYS:
                    requirements.draft_should_be_deleted.add(
                        release, may_exists=False
                    )
                continue

            # -- Case 3: Release is a pre-release.
            if release_crawl.state == models.ReleaseState.PRERELEASE:
                # -- NOTE: We rely here on the fact that the releases are in
                # -- descending date (newest first)
                if prereleases_kept < consts.NUM_PRE_RELEASES_TO_KEEP:
                    # -- Keep this prerelease.
                    prereleases_kept += 1
                else:
                    # -- Mark the for deletion if too many.
                    requirements.pre_release_should_be_deleted.add(
                        release, may_exists=False
                    )
                continue

            # -- Case 4: Any other release. Do nothing.
            continue

    # -- All done.
    return models.AnalysisResults(requirements)


def main():
    """Program entry point."""

    parser = argparse.ArgumentParser(
        description="Apio Repos Janitor's analysis phase."
    )
    parser.add_argument(
        "--janitor-data-dir",
        type=Path,
        help="Janitor's temp data dir",
    )
    args = parser.parse_args()

    # -- Get the work dir path.
    janitor_data_dir = args.janitor_data_dir
    print(f"janitor_data_dir = {str(janitor_data_dir)}")

    # -- Load the crawler results
    with open(janitor_data_dir / "crawl-results.pkl", "rb") as f:
        crawl_results = pickle.load(f)

    # -- Analyze
    analysis_results: models.AnalysisResults = analyze(crawl_results)
    assert isinstance(analysis_results, models.AnalysisResults)

    # -- Write results as json, for human consumption.
    (janitor_data_dir / "analysis-results.json").write_text(
        util.to_json_text(asdict(analysis_results)),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (janitor_data_dir / "analysis-results.pkl").open("wb") as f:
        pickle.dump(analysis_results, f)


if __name__ == "__main__":
    main()
