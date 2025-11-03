"""Tasks definitions for the 'invoke' command."""

# To install 'invoke' run: pip install invoke
#
# For more information see the Apio development guide at
# https://fpgawars.github.io/apio/development-environment/
#
# A few useful Invoke tasks
#   invoke --list        # Show available tasks
#   invoke -l            # Show available tasks
#   invoke lint          # Lint the python code
#   invoke test-fast     # Run only the fast tests, skip the rest.
#   invoke test       .  # Run lint and all the tests (slow)
#   invoke install-apio  # Install to run 'apio' from the source code here.
#   invoke docs-viewer   # Run a local http server to view the Apio docs.
#   invoke test-coverage # Collect and show test coverage.

import sys
import webbrowser
from pathlib import Path
from glob import glob
import shutil
import platform
import subprocess
from subprocess import CompletedProcess
from typing import Optional, List
from importlib.metadata import version, PackageNotFoundError
from invoke import task
from invoke.context import Context


# ========================== Helper definitions ===============================


# -- NOTE: The first sentence of a task docstring is also its help string
# -- which is printed when running 'invoke --list'.

# -- Latest supported python version.
LATEST_PYTHON = "py314"

# -- The python interpreter that we currently use.
PYTHON = sys.executable

# -- This has to do with the preservation of color from shell commands.
# -- Not support on Windows. Need to be investigated mode.
PTY = platform.system() != "Windows"


def package_version(package_name: str) -> Optional[str]:
    """Get the version of installed package or None if not installed."""
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None


def install_package(package_name: str, required_version: str) -> None:
    """If the package/version is not installed then install it. Otherwise
    do nothing."""
    if package_version(package_name) != required_version:
        print(f"\n*** Auto installing {package_name}@{required_version} ***")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                f"{package_name}=={required_version}",
            ]
        )
    assert (
        package_version(package_name) == required_version
    ), f"Expected to find {package_name}=={required_version}"


DEPENDENCIES = [
    ("rich", "14.0.0"),
    ("tox", "4.27.0"),
    ("flit", "3.12.0"),
    ("mkdocs-material", "9.6.14"),
    ("pytest", "8.4.2"),
]


def install_dependencies():
    """Install any dependency that is missing or has a different version."""
    for package_name, required_version in DEPENDENCIES:
        install_package(package_name, required_version)


# -- Make sure required python dependencies are installed.
install_dependencies()


# -- Now that Rich is installed, we can import and use it.
# pylint: disable=wrong-import-position
from rich.console import Console  # noqa: E402

# -- For outputting via Rich. The regular rich.print() doesn't not allow to
# -- disable markup.
console = Console()


def cout(*args, markup=False, highlight=False, **kwargs):
    """A shortcut for Rich lib console.print()."""
    console.print(*args, markup=markup, highlight=highlight, **kwargs)


def announce_task(task_name: str) -> None:
    """Prints a message saying that the task is starting."""
    cout(f"Executing Apio task: {task_name}", style="magenta bold")


def get_repo_root() -> Path:
    """Return the root of the local apio github repository."""
    # -- Return the directory that contains this file.
    return Path(__file__).resolve().parent


def open_test_coverage_viewer() -> None:
    """Open a browser to view the test coverage results entry page."""
    file_path = get_repo_root() / "_pytest-coverage" / "index.html"
    file_uri = file_path.resolve().as_uri()

    # -- Open in default browser.
    default_browser = webbrowser.get()
    default_browser.open(file_uri)


def run(ctx: Context, cmd: List[str]) -> None:
    """Run a command. Abort if it returns an error code."""
    dry_run: bool = ctx.config.run.dry
    prefix = "DRY: " if dry_run else ""
    cout(f"{prefix}{' '.join(cmd)}", style="cyan")
    if not dry_run:
        result: CompletedProcess = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            cout("Command failed.", style="red bold")
            sys.exit(1)


# ===================== Tasks definitions start here ==========================


@task(name="lint", aliases=["l"])
def lint_task(ctx: Context):
    """Lint only."""
    announce_task("lint")
    # -- NOTE: This also creates the local dir _site which we ignore. We
    # -- don't know how to lint mkdocs without creating it.
    run(ctx, [PYTHON, "-m", "tox", "-e", "lint"])


@task(name="test-fast", aliases=["tf"])
def test_fast_task(ctx: Context):
    """Run fast tests only, using the latest Python."""
    announce_task("test-fast")
    run(
        ctx,
        [
            PYTHON,
            "-m",
            "tox",
            "--skip-missing-interpreters",
            "false",
            "-e",
            LATEST_PYTHON,
            "--",
            "--fast-only",
        ],
    )


@task(name="test", aliases=["t"])
def check_task(ctx: Context):
    """Lint and run all tests using the latest Python."""
    announce_task("test")
    run(
        ctx,
        [
            PYTHON,
            "-m",
            "tox",
            "--skip-missing-interpreters",
            "false",
            "-e",
            f"lint,{LATEST_PYTHON}",
        ],
    )


@task(name="test-all", aliases=["ta"])
def check_all_task(ctx: Context):
    """Lint and run all tests using all Python versions."""
    announce_task("test-all")
    run(ctx, [PYTHON, "-m", "tox", "--skip-missing-interpreters", "false"])


@task(name="test-coverage", aliases=["tc"])
def test_coverage_task(ctx: Context):
    """Generate test coverage report."""
    announce_task("test-coverage")
    run(
        ctx,
        [
            PYTHON,
            "-m",
            "tox",
            "--skip-missing-interpreters",
            "false",
            "-e",
            LATEST_PYTHON,
            "--",
            "--cov=apio",
            "--cov=test",
            "--cov-config=.coveragerc",
            "--cov-append",
            "--cov-report=html:_pytest-coverage",
        ],
    )

    # -- Open a browser to show the results.
    open_test_coverage_viewer()


@task(name="view-coverage", aliases=["vc"])
def view_coverage_task(_: Context):
    """View test coverage from a previous run of 'test-coverage'."""
    announce_task("view-coverage")

    open_test_coverage_viewer()


@task(name="clear-cache", aliases=["cc"])
def clear_cache_task(_: Context):
    """Clear the pytest cache."""
    announce_task("clear-pytest-cache")
    repo_root = get_repo_root()
    assert isinstance(repo_root, Path)

    pytest_caches = glob(str(repo_root / ".pytest_cache"))
    pytest_caches = pytest_caches + glob(
        str(repo_root / ".tox/*/.pytest_cache")
    )

    if not pytest_caches:
        print("Pytest cache is cleared.")
        return

    for cache_dir in pytest_caches:
        print(f"Deleting {cache_dir}")
        shutil.rmtree(cache_dir)


# -- This task has not been tested.
@task(name="publish-test", aliases=["pt"])
def publish_test_task(ctx: Context):
    """Publish to Pypi test instance."""
    announce_task("publish-test")
    run(ctx, [PYTHON, "-m", "flit", "publish", "--repository", "testpypi"])


# -- This task has not been tested.
@task(name="publish-prod", aliases=["pd"])
def publish_task(ctx: Context):
    """Publish to Pypi production instance."""
    announce_task("publish-prod")
    run(ctx, [PYTHON, "-m", "flit", "publish"])


@task(name="install-apio", aliases=["ia"])
def install_apio_task(ctx: Context):
    """Install apio package from source code."""
    announce_task("install-apio")
    run(ctx, [PYTHON, "-m", "pip", "install", "-e", "."])
    run(ctx, ["apio", "--version"])
    cout(
        "The source code of this repo is now "
        "installed as the 'apio' pip package.\n"
        "Run 'apio' to test it.",
        style="green",
    )


@task(name="uninstall-apio", aliases=["ua"])
def uninstall_apio_task(ctx: Context):
    """Uninstall the apio package."""
    announce_task("uninstall-apio")
    run(ctx, [PYTHON, "-m", "pip", "uninstall", "-y", "apio"])
    cout("The'apio' pip package is uninstalled.", style="green bold")


@task(name="install-deps", aliases=["id"])
def install_deps_task(_: Context):
    """Install development tools. Since we do at at the top of this file
    for every task, there is nothing to do here."""
    announce_task("install-deps")
    cout("       required  installed")
    for name, ver in DEPENDENCIES:
        cout(f"{name:17} {ver:9s} {version(name)}")


@task(name="docs-viewer", aliases=["dv"])
def install_docs_viewer_task(ctx: Context):
    """Run a local http server to view the Apio docs."""
    announce_task("docs-viewer")
    run(ctx, ["mkdocs", "serve"])
