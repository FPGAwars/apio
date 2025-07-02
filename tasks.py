"""Tasks definitions for the 'invoke' command."""

# To install 'invoke' run: pip install invoke
#
# For more information see the Apio development guide at
# https://fpgawars.github.io/apio/development-environment/
#
# A few useful Invoke tasks
#   invoke --list        # Show available tasks
#   invoke lint          # Lint the python code
#   invoke test          # Run the offline tests (fast)
#   invoke check         # Run lint and all the tests (slow)
#   invoke install-apio  # Install to run 'apio' from the source code here.
#   invoke docs-viewer   # Run a local http server to view the Apio docs.

import sys
from typing import Optional
from importlib.metadata import version, PackageNotFoundError
import subprocess
from invoke import task
from invoke.context import Context

# ========================== Helper definitions ===============================


# -- NOTE: The first sentence of a task docstring is also its help string
# -- which is printed when running 'invoke --list'.

# -- Latest supported python version.
LATEST_PYTHON = "py313"

# -- The python interpreter that we currently use.
PYTHON = sys.executable


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


def msg(*args, markup=False, highlight=False, **kwargs):
    """A shortcut for Rich lib console.print()."""
    console.print(*args, markup=markup, highlight=highlight, **kwargs)


def announce_task(task_name: str) -> None:
    """Prints a message saying that the task is starting."""
    msg(f"Executing Apio task: {task_name}", style="magenta bold")


# ===================== Tasks definitions start here ==========================


@task(
    name="lint",
    aliases=["l"],
)
def lint_task(ctx: Context):
    """Lint only."""
    announce_task("lint")
    # -- NOTE: This also creates the local dir _site which we ignore. We
    # -- don't know how to lint mkdocs without creating it.
    cmd = f"{PYTHON} -m tox -e lint"
    ctx.run(cmd, pty=True)


@task(
    name="test",
    aliases=["t"],
)
def test_task(ctx: Context):
    """Offline tests with the latest Python."""
    announce_task("test")
    cmd = (
        f"{PYTHON} -m tox "
        "--skip-missing-interpreters false "
        f"-e {LATEST_PYTHON} "
        "-- --offline"
    )
    ctx.run(cmd, pty=True)


@task(
    name="check",
    aliases=["c"],
)
def check_task(ctx: Context):
    """Lint and all tests using the latest Python."""
    announce_task("check")
    cmd = (
        f"{PYTHON} -m tox "
        "--skip-missing-interpreters false "
        f"-e lint,{LATEST_PYTHON}"
    )
    ctx.run(cmd, pty=True)


@task(
    name="check-all",
    aliases=["ca"],
)
def check_all_task(ctx: Context):
    """Lint and all tests using all Python versions."""
    announce_task("check-all")
    cmd = f"{PYTHON} -m tox " "--skip-missing-interpreters false "
    ctx.run(cmd, pty=True)


@task(
    name="test-coverage",
    aliases=["tc"],
)
def test_coverage_task(ctx: Context):
    """Generate test coverage report."""
    announce_task("test-coverage")
    cmd = (
        f"{PYTHON} -m tox --skip-missing-interpreters false "
        f"-e {LATEST_PYTHON} "
        "-- --cov --cov-report=html:_pytest-coverage"
    )
    ctx.run(cmd, pty=True)


@task(name="publish-test")
def publish_test_task(ctx: Context):
    """Publish to Pypi test instance."""
    announce_task("publish-test")
    cmd = f"{PYTHON} -m flit publish --repository testpypi"
    ctx.run(cmd, pty=True)


@task(name="publish-prod")
def publish_task(ctx: Context):
    """Publish to Pypi production instance."""
    announce_task("publish-prod")
    cmd = f"{PYTHON} -m flit publish"
    ctx.run(cmd, pty=True)


@task(name="install-apio", aliases=["ia"])
def install_apio_task(ctx: Context):
    """Install apio package from source code."""
    announce_task("install-apio")
    cmd = f"{PYTHON} -m pip install -e ."
    ctx.run(cmd, pty=True)
    ctx.run("apio --version", pty=True)
    msg(
        "The source code of this repo is now "
        "installed as the 'apio' pip package.\n"
        "Run 'apio' to test it.",
        style="green",
    )


@task(name="uninstall-apio", aliases=["ua"])
def uninstall_apio_task(ctx: Context):
    """Uninstall the apio package."""
    announce_task("uninstall-apio")
    cmd = f"{PYTHON} -m pip uninstall -y apio"
    ctx.run(cmd, pty=True)
    msg("The'apio' pip package is uninstalled.", style="green bold")


@task(name="install-deps", aliases=["deps"])
def install_deps_task(ctx: Context):
    """Install development tools. Since we do at at the top of this file
    for every task, there is nothing to do here."""
    _ = ctx
    announce_task("install-deps")
    msg("       required  installed")
    for name, ver in DEPENDENCIES:
        msg(f"{name:7s} {ver:9s} {version(name)}")


@task(name="docs-viewer", aliases=["dv"])
def install_docs_viewer_task(ctx: Context):
    """Run a local http server to view the Apio docs."""
    print(f"{type(ctx)=}")
    announce_task("docs-viewer")
    ctx.run("mkdocs serve", pty=True)
