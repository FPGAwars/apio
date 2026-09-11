"""
This step of the apio repos analyzer reads the unmet requirements from the
pre verifier and try to make them true.
"""

from dataclasses import asdict
import pickle
import argparse
from pathlib import Path
from scripts.janitor import models, util


def fix(
    verification_results: models.VerificationResults,
) -> models.FixingResults:
    """Fix unmet analyzer requirements."""

    _ = verification_results  # Ignored for now

    # TBD

    # -- All done.
    return models.FixingResults()


def main():
    """Program entry point."""

    parser = argparse.ArgumentParser(
        description="Apio Repos Janitor's fixing phase."
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

    # -- Load the analyzer results
    with open(janitor_data_dir / "pre-verification-results.pkl", "rb") as f:
        verification_results = pickle.load(f)

    # -- Verify
    fixing_results: models.FixingResults = fix(verification_results)

    # -- Write results as json, for human consumption.
    (janitor_data_dir / "fixing-results.json").write_text(
        util.to_json_text(asdict(fixing_results)),
        encoding="utf-8",
    )

    # -- Write results as pickle, for consumption by next step.
    with (janitor_data_dir / "fixing-results.pkl").open("wb") as f:
        pickle.dump(fixing_results, f)


if __name__ == "__main__":
    main()
