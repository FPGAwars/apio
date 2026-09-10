"""
The second step of the Apio Repos Janitor workflow. It it reads the crawler
results as a pickled CrawlResults and output requirements to check in a
form of a pickled AnalysisResults.
"""

from dataclasses import asdict
import pickle
import json
import argparse
from pathlib import Path
from typing import List, Dict
from scripts.janitor import models, consts

parser = argparse.ArgumentParser(
    description="Apio Repos Janitor's analysis phase."
)
parser.add_argument(
    "--work-dir",
    type=Path,
    default=Path("./_janitor"),
    help="Janitor's temp data dir (default = ./_janitor)",
)
args = parser.parse_args()


def analyze(crawl_results: models.CrawlResults) -> models.AnalysisResults:
    """Analyze crawling results and generate requirements report."""

    # pylint: disable=too-many-locals

    # -- TODO: Make the code clearer.

    should_be_stable_releases: Dict[str, List[str]] = {}

    def append_stable_release(r: models.GithubReleaseRef):
        tags = should_be_stable_releases.get(r.repo, [])
        if r.tag not in tags:
            tags.append(r.tag)
            tags.sort(reverse=True)
        should_be_stable_releases[r.repo] = tags

    for _, c in crawl_results.vscode_marketplace_crawl.releases.items():
        append_stable_release(c.apio_vscode_release)
        append_stable_release(c.apio_cli_release)

    for _, c in crawl_results.remote_configs_crawl.remote_configs.items():
        for _, p in c.packages.items():
            append_stable_release(p.package_release)

    should_be_stable_releases = dict(sorted(should_be_stable_releases.items()))

    should_be_latest_releases: Dict[str, str] = {}

    pypi_crawl = crawl_results.pypi_crawl
    pypi_latest_release = pypi_crawl.releases[str(pypi_crawl.latest)]
    should_be_latest_releases[pypi_latest_release.apio_cli_release.repo] = (
        pypi_latest_release.apio_cli_release.tag
    )

    vscode_crawl = crawl_results.vscode_marketplace_crawl
    vscode_latest_release = vscode_crawl.releases[str(vscode_crawl.latest)]
    should_be_latest_releases[
        vscode_latest_release.apio_vscode_release.repo
    ] = vscode_latest_release.apio_vscode_release.tag

    latest_remote_config_key = (
        str(pypi_crawl.latest.major) + "." + str(pypi_crawl.latest.minor)
    )
    latest_remote_config = crawl_results.remote_configs_crawl.remote_configs[
        latest_remote_config_key
    ]
    for _, package in latest_remote_config.packages.items():
        release = package.package_release
        assert release.repo not in should_be_latest_releases
        should_be_latest_releases[release.repo] = release.tag

    # -- Analyze pre-releases garbage collection.

    garbage_prereleases: Dict[str, List[str]] = {}
    for repo, repo_crawl in crawl_results.repos_crawl.repos.items():
        prereleases_kept = 0
        delete_list = []
        # -- Iterate releases and process pre-releases. The order is
        # -- in decreasing created_date value.
        for release, release_crawl in repo_crawl.releases.items():
            if release_crawl.state == models.ReleaseState.PRERELEASE:
                if prereleases_kept < consts.NUM_PRE_RELEASES_TO_KEEP:
                    # -- Keep this prerelease.
                    prereleases_kept += 1
                else:
                    delete_list.append(release)
        if delete_list:
            garbage_prereleases[repo] = delete_list

    # -- All done.
    return models.AnalysisResults(
        should_be_stable_releases,
        should_be_latest_releases,
        garbage_prereleases,
    )


def main():
    """Main for testing."""

    # -- Get the work dir path.
    work_dir_path = args.work_dir
    print(f"work_dir = {str(work_dir_path)}")

    # -- Load the crawler results
    with open(work_dir_path / "crawl_results.pkl", "rb") as f:
        crawl_results = pickle.load(f)

    # -- Analyze
    analysis_results: models.AnalysisResults = analyze(crawl_results)

    # -- Write results as json, for human consumption.
    (work_dir_path / "analysis_results.json").write_text(
        json.dumps(asdict(analysis_results), indent=2, default=str),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (work_dir_path / "analysis_results.pkl").open("wb") as f:
        pickle.dump(analysis_results, f)


if __name__ == "__main__":
    main()
