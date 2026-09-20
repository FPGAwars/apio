"""
This step of the apio repos janitor reads the crawler data and writes to
a file a list of requirements that should be met.
"""

from dataclasses import asdict
from datetime import date
import pickle
import argparse
from pathlib import Path
from scripts.janitor import consts, util
from scripts.janitor.models import (
    CrawlResults,
    AnalysisResults,
    RequirementsSet,
    RequirementType,
    GithubReleaseRef,
    ReleaseState,
    Requirement,
)


def analyze(crawl_results: CrawlResults) -> AnalysisResults:
    """Analyze crawling results and generate requirements report."""

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches

    # -- A container for the requirements that the analyzer generates.
    requirements = RequirementsSet()

    # -- Generate RELEASE_SHOULD_BE_STABLE requirements

    # -- The apio cli release of each pypi release should be stable.
    for ver, pypi_rc in crawl_results.pypi_crawl.releases.items():
        requirements.add_by_ref(
            RequirementType.RELEASE_SHOULD_BE_STABLE,
            pypi_rc.apio_cli_release,
            [f"[Analyzer] Published as pypi {ver}."],
        )

    # -- Each vscode market release, the apio vscode and the apio cli
    # -- releases should be stable.
    for (
        ver,
        vscode_rc,
    ) in crawl_results.vscode_marketplace_crawl.releases.items():
        requirements.add_by_ref(
            RequirementType.RELEASE_SHOULD_BE_STABLE,
            vscode_rc.apio_vscode_release,
            [f"[Analyzer] Published as apio vscode {ver}."],
        )
        requirements.add_by_ref(
            RequirementType.RELEASE_SHOULD_BE_STABLE,
            vscode_rc.apio_cli_release,
            [f"[Analyzer] Used by published vscode {ver}."],
        )

    # -- All packages that are refereed by a remote config files
    # -- should be stable.
    for (
        ver,
        config_rc,
    ) in crawl_results.remote_configs_crawl.remote_configs.items():
        for package in config_rc.packages.values():
            requirements.add_by_ref(
                RequirementType.RELEASE_SHOULD_BE_STABLE,
                package.package_release,
                [f"[Analyzer] Used by remote config {ver}."],
            )

    # -- Generate RELEASE_SHOULD_BE_LATEST requirements.

    # -- The apio vscode release of the latest vscode market release should
    # -- be marked as latest.
    vscode_crawl = crawl_results.vscode_marketplace_crawl
    vscode_latest_release = vscode_crawl.releases[str(vscode_crawl.latest)]
    requirements.add_by_ref(
        RequirementType.RELEASE_SHOULD_BE_LATEST,
        vscode_latest_release.apio_vscode_release,
        notes=[
            "[Analyzer] Latest published apio-vscode "
            + f"({vscode_crawl.latest})."
        ],
    )

    # -- The cli release that is the latest on pypi should be latest in the
    # -- apio repository.
    pypi_crawl = crawl_results.pypi_crawl
    pypi_latest_release = pypi_crawl.releases[str(pypi_crawl.latest)]
    requirements.add_by_ref(
        RequirementType.RELEASE_SHOULD_BE_LATEST,
        pypi_latest_release.apio_cli_release,
        notes=[f"[Analyzer] Published as Pypi latest ({pypi_crawl.latest})."],
    )

    # -- The apio packages releases that are referred by the remote config
    # -- of the latest apio CLI should be marked latest.
    latest_remote_config_key = (
        str(pypi_crawl.latest.major) + "." + str(pypi_crawl.latest.minor)
    )
    latest_remote_config = crawl_results.remote_configs_crawl.remote_configs[
        latest_remote_config_key
    ]
    for package in latest_remote_config.packages.values():
        requirements.add_by_ref(
            RequirementType.RELEASE_SHOULD_BE_LATEST,
            package.package_release,
            notes=[
                "[Analyzer] Used by latest apio remote config "
                f"{latest_remote_config_key}."
            ],
        )

    # -- Now that we set the all the RELEASE_SHOULD_BE_STABLE requirements,
    # -- extract it as a set of releases in use.

    releases_in_use: set[GithubReleaseRef] = {
        req.release_ref()
        for req in requirements.members_of_type(
            RequirementType.RELEASE_SHOULD_BE_STABLE
        )
    }

    # -- Generate RELEASE_SHOULD_BE_CONSISTENT requirements

    # -- Generate RELEASE_SHOULD_BE_CONSISTENT requirement for each
    # -- RELEASE_SHOULD_BE_STABLE requirement in a repo that is checked
    # -- for consistency. As for Sep 2026, only the openxc7 repo is checked
    # -- for consistency.
    for release in releases_in_use:
        if consts.APIO_REPOS[release.repo].check_consistency:
            requirements.add_by_ref(
                req_type=RequirementType.RELEASE_SHOULD_BE_CONSISTENT,
                release_ref=release,
                notes=["[Analyzer] Consistency checks enabled for repo."],
            )

    # -- Generate DRAFT_SHOULD_BE_DELETED and PRERELEASE_SHOULD_BE_DELETED.

    today: date = date.today()
    for repo, repo_crawl in crawl_results.repos_crawl.repos.items():
        num_prereleases = 0
        # -- Iterate releases and process pre-releases. The order is
        # -- in decreasing published_date value.
        for release_tag, release_crawl in repo_crawl.releases.items():
            release = GithubReleaseRef(repo, release_tag)

            # -- Case 1: Release is in use.
            if release in releases_in_use:
                continue

            # -- Case 2: Release is a draft.
            if release_crawl.state == ReleaseState.DRAFT:
                draft_date = release_crawl.published_date
                draft_age_days = (today - draft_date).days
                # -- Mark for deletion if too old.
                if draft_age_days > consts.MAX_DRAFT_AGE_DAYS:
                    # requirements.draft_should_be_deleted.add(release)
                    requirements.add_by_ref(
                        req_type=RequirementType.DRAFT_SHOULD_BE_DELETED,
                        release_ref=release,
                        notes=[
                            f"[Analyzer] Draft is {draft_age_days} "
                            + "days old."
                        ],
                    )
                continue

            # -- Case 3: Release is a pre-release.
            if release_crawl.state == ReleaseState.PRERELEASE:
                # -- NOTE: We rely here on the fact that the releases are in
                # -- descending date (newest first)
                num_prereleases += 1
                if num_prereleases > consts.NUM_PRE_RELEASES_TO_KEEP:
                    # -- Mark the for deletion if too many.
                    # requirements.pre_release_should_be_deleted.add(release)
                    requirements.add_by_ref(
                        req_type=RequirementType.PRERELEASE_SHOULD_BE_DELETED,
                        release_ref=release,
                        notes=[f"[Analyzer] Prerelease #{num_prereleases}."],
                    )
                continue

            # -- Case 4: Any other release. Do nothing.
            continue

    # -- Generate REPO_SHOULD_HAVE_A_RECENT_BUILD requirements

    for repo, attributes in consts.APIO_REPOS.items():
        if attributes.daily_builds:
            requirements.add(
                Requirement(
                    req_type=RequirementType.REPO_SHOULD_HAVE_A_RECENT_BUILD,
                    repo=repo,
                    release_tag=None,
                    notes=["[Analyzer] Repo should have a daily build."],
                )
            )

    # -- All done.
    return AnalysisResults(requirements)


def main() -> None:
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
    analysis_results: AnalysisResults = analyze(crawl_results)
    assert isinstance(analysis_results, AnalysisResults)

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
