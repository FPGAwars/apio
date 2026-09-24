"""
This step of the apio repos janitor reads the requirements from the
analyzer step and classifies them as failures (not met) and success (met),
write the results to a file and generated a human readable markdown
report.
"""

from dataclasses import asdict, dataclass
from datetime import date
import pickle
import json
import argparse
from pathlib import Path
from scripts.janitor import crawler, util, consts
from scripts.janitor.models import (
    RequirementsSet,
    RepoCrawl,
    ReposCrawl,
    Requirement,
    RequirementType,
    ReleaseState,
    ReleaseCrawl,
    AnalysisResults,
    VerificationResults,
)


@dataclass(frozen=True)
class ReleaseStatus:
    """Release status lookup result. Note that is_latest requires a separate
    request to Github so not included here."""

    exists: bool
    is_draft: bool
    is_prerelease: bool
    is_stable: bool


@dataclass
class VerificationContext:
    """Contains verification values that are passed to the verification
    functions."""

    failures: RequirementsSet
    successes: RequirementsSet
    fresh_repos_crawl: ReposCrawl
    today: date

    def add_failure(self, requirement: Requirement, note: str):
        """Append the note to the requirement notes and add the requirement
        to the failure set.
        """
        requirement.append_note(note)
        self.failures.add(requirement)

    def add_success(self, requirement: Requirement, note: str):
        """Append the note to the requirement notes and add the requirement
        to the success set.
        """
        requirement.append_note(note)
        self.successes.add(requirement)


def _verify_release_should_be_stable(
    ctx: VerificationContext, requirement: Requirement
):
    """Verify a requirement that a release should be stable."""
    assert requirement.req_type == RequirementType.RELEASE_SHOULD_BE_STABLE

    # -- Get the release crawl information
    release = requirement.release_ref()
    release_crawl = ctx.fresh_repos_crawl.get_release_crawl(release, None)

    # -- Classify the requirement.
    if release_crawl is None:
        ctx.add_failure(requirement, "[Verifier] Release is missing.")
    elif not release_crawl.state.is_stable:
        ctx.add_failure(requirement, "[Verifier] Release is not stable.")
    else:
        ctx.add_success(requirement, "[Verifier] Release is stable.")


def _verify_release_should_be_latest(
    ctx: VerificationContext, requirement: Requirement
):
    """Verify a requirement that a release should be latest."""
    assert requirement.req_type == RequirementType.RELEASE_SHOULD_BE_LATEST

    # -- Get the release crawl information
    release = requirement.release_ref()
    release_crawl = ctx.fresh_repos_crawl.get_release_crawl(release, None)

    # -- Classify the requirement.
    if release_crawl is None:
        ctx.add_failure(requirement, "[Verifier] Release is missing.")
    elif not release_crawl.state.is_latest:
        ctx.add_failure(requirement, "[Verifier] Release is not latest.")
    else:
        ctx.add_success(requirement, "[Verifier] Release is latest.")


def _verify_release_should_be_consistent(
    ctx: VerificationContext, requirement: Requirement
):
    """Verify a requirement that a release should be consistent."""
    assert requirement.req_type == RequirementType.RELEASE_SHOULD_BE_CONSISTENT

    # -- For now we check consistency only of openxc7 releases.
    release = requirement.release_ref()
    assert release.repo == "fpgawars/tools-openxc7", requirement

    # -- Older version didn't have the parts index so we just
    # -- assume they are ok.
    if release.release_tag < "2026-09-10":
        ctx.add_success(requirement, "[Verifier] Old release, assuming OK.")
        return

    # -- Download the xilinx parts index.
    index_bytes = util.download_release_asset(
        requirement.release_ref(), "XILINX-PARTS-INDEX.json"
    )
    index = json.loads(index_bytes)

    # -- Construct a set of the chipdb asset names from the index.
    index_chipdbs: set[str] = {
        part["asset"] for part in index["parts"].values() if "asset" in part
    }
    print(f"index_chipdbs has {len(index_chipdbs)} members.")
    assert len(index_chipdbs) >= 10, index_chipdbs  # Sanity check

    # -- Download the release metadata.
    release_metadata = util.download_release_metadata(release)

    # -- Construct the set of chipdb assets names from the release
    # -- metadata.
    assets_chipdbs: set[str] = {
        name
        for name in release_metadata.assets.keys()
        if name.startswith("apio-xilinx-chipdb-")
    }
    print(f"assets_chipdbs has {len(assets_chipdbs)} members.")
    assert len(assets_chipdbs) >= 10, assets_chipdbs  # Sanity check

    # -- Classify the requirement
    if index_chipdbs != assets_chipdbs:
        print(f"Openxc7 release {release} is NOT consistent")
        only_in_index = sorted(index_chipdbs - assets_chipdbs)
        only_in_assets = sorted(assets_chipdbs - index_chipdbs)
        print(f"{only_in_index=}")
        print(f"{only_in_assets=}")
        ctx.add_failure(requirement, "[Verifier] Chipdb assets do not match.")
    else:
        ctx.add_success(requirement, "[Verifier] Chipdb assets match index.")


def _verify_draft_should_be_deleted(
    ctx: VerificationContext, requirement: Requirement
):
    """Verify a requirement that a draft release should be deleted."""
    assert requirement.req_type == RequirementType.DRAFT_SHOULD_BE_DELETED

    # -- Get the release crawl information
    release = requirement.release_ref()
    release_crawl = ctx.fresh_repos_crawl.get_release_crawl(release, None)

    # -- Classify the requirement
    if release_crawl is None:
        ctx.add_success(requirement, "[Verifier] Draft is deleted.")
    elif release_crawl.state != ReleaseState.DRAFT:
        ctx.add_failure(requirement, "[Verifier] Not a draft.")
    else:
        ctx.add_failure(requirement, "[Verifier] Draft exists.")


def _verify_prerelease_should_be_deleted(
    ctx: VerificationContext, requirement: Requirement
):
    """Verify a requirement that a prerelease release should be deleted."""
    assert requirement.req_type == RequirementType.PRERELEASE_SHOULD_BE_DELETED

    # -- Get the release crawl information
    release = requirement.release_ref()
    release_crawl = ctx.fresh_repos_crawl.get_release_crawl(release, None)

    # -- Classify the requirement
    if release_crawl is None:
        ctx.add_success(requirement, "[Verifier] Prerelease is deleted.")
    elif release_crawl.state != ReleaseState.PRERELEASE:
        ctx.add_failure(requirement, "[Verifier] Not a prerelease.")
    else:
        ctx.add_failure(requirement, "[Verifier] Prerelease exists.")


def _verify_repo_should_have_a_recent_build(
    ctx: VerificationContext, requirement: Requirement
):
    """Verify a requirement that a repo should have a recent build.."""
    assert (
        requirement.req_type == RequirementType.REPO_SHOULD_HAVE_A_RECENT_BUILD
    )

    # -- Get the repo crawl information
    repo = requirement.repo
    repo_crawl: RepoCrawl = ctx.fresh_repos_crawl.repos[repo]

    # -- Find the date of the latest release
    latest: tuple[str, ReleaseCrawl] | None = max(
        repo_crawl.releases.items(),
        key=lambda item: item[1].published_date,
        default=None,
    )

    # -- Handle the case of no builds at all
    if latest is None:
        ctx.add_failure(requirement, "[Verifier] No builds.")
        return

    # -- We found the latest build, compute its age ind ays.
    days_since_last_build = (ctx.today - latest[1].published_date).days

    # -- Handle the case of latest build is too old.
    if days_since_last_build > consts.MAX_RECENT_RELEASE_DAYS:
        ctx.add_failure(
            requirement,
            f"[Verifier] {latest[0]} is {days_since_last_build} days old.",
        )
        return

    # -- Handle the case of OK
    ctx.add_success(
        requirement,
        f"[Verifier] {latest[0]} is {days_since_last_build} days old.",
    )


def verify(
    analysis_results: AnalysisResults,
) -> VerificationResults:
    """Verifies that the analyzer requirements where fixed."""

    # -- The requirement from the analyzer
    requirements: RequirementsSet = analysis_results.requirements

    # -- Create a verification context that will be passed around.
    ctx = VerificationContext(
        failures=RequirementsSet(),
        successes=RequirementsSet(),
        fresh_repos_crawl=crawler.crawl_apio_repos(),
        today=date.today(),
    )

    for requirement in requirements.members():
        # -- Analyzer should not set the verifier_note field.
        # assert requirement.notes is None, requirement

        # -- Dispatch requirement verification by type.
        match requirement.req_type:
            case RequirementType.RELEASE_SHOULD_BE_STABLE:
                _verify_release_should_be_stable(ctx, requirement)

            case RequirementType.RELEASE_SHOULD_BE_LATEST:
                _verify_release_should_be_latest(ctx, requirement)

            case RequirementType.RELEASE_SHOULD_BE_CONSISTENT:
                _verify_release_should_be_consistent(ctx, requirement)

            case RequirementType.DRAFT_SHOULD_BE_DELETED:
                _verify_draft_should_be_deleted(ctx, requirement)

            case RequirementType.PRERELEASE_SHOULD_BE_DELETED:
                _verify_prerelease_should_be_deleted(ctx, requirement)

            case RequirementType.REPO_SHOULD_HAVE_A_RECENT_BUILD:
                _verify_repo_should_have_a_recent_build(ctx, requirement)
            case _:
                raise ValueError(
                    f"unknown requirement type: {requirement.req_type}"
                )

    # -- Check that the requirements from the analyzer are properly
    # -- partitioned among the failures and successes. The added verifier notes
    # -- are ignore in this check because they are not used for
    # -- comparisons.
    requirements.check_partitioning(ctx.failures, ctx.successes)

    # -- All done.
    return VerificationResults(
        len(ctx.failures) == 0,
        ctx.failures,
        ctx.successes,
    )


def _generate_markdown_report(
    verification_results: VerificationResults,
) -> str:
    """Generates a markdown report for human consumption with the verification
    results."""
    lines = []
    # -- Get the failing requirements
    failures: RequirementsSet = verification_results.failures
    if len(failures) == 0:
        lines.append("No errors found.")
        return "\n".join(lines)

    lines.append("**Error founds**")

    # -- Generate a report section for each repo.
    for repo, requirement_types in failures.group_by_repo_and_type().items():
        lines.append("\n<br>\n")
        lines.append(f"**{repo}**")

        for requirement_type, requirements in requirement_types.items():
            type_title = requirement_type.value.replace("-", " ").capitalize()
            lines.append(f"- {type_title}")
            for requirement in requirements:
                if requirement.req_type.is_release_scope:
                    link = (
                        f"[{requirement.release_tag}]"
                        + f"(https://github.com/{repo}/releases/tag/"
                        + f"{requirement.release_tag})"
                    )
                else:
                    link = f"[releases](https://github.com/{repo}/releases)"
                lines.append(f"  - {link}")

    # -- All done.
    return "\n".join(lines)


def main() -> None:
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
    verification_results: VerificationResults = verify(analysis_results)

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
