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
import importlib.util
from importlib.metadata import version
import subprocess
from invoke import task


# -- NOTE: The first sentence of a task docstring is also its help string
# -- which is printed when running 'invoke --list'.

# -- Latest supported python version.
LATEST_PYTHON = "py313"

# -- The python interpreter that we currently use.
PYTHON = sys.executable

# -- Auto install packages that are not Apio dependencies but required here.

deps = [
    ("rich", "14.0.0"),
    ("tox", "4.27.0"),
    ("flit", "3.12.0"),
    ("mkdocs", "1.6.1"),
]

for module, required_version in deps:
    if (
        importlib.util.find_spec(module) is None
        or version(module) != required_version
    ):
        print(f"\n*** Auto installing {module}@{required_version} ***")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                f"{module}=={required_version}",
            ]
        )
    assert (importlib.util.find_spec(module) is not None) and (
        version(module) == required_version
    ), f"'{module}@{required_version}' is not installed."

# -- Now that Rich is installed, we can import and use it.
# pylint: disable=wrong-import-position
from rich.console import Console  # noqa: E402

console = Console()


def out(*args, markup=False, highlight=False, **kwargs):
    """A shortcut for Rich lib console.print()."""
    console.print(*args, markup=markup, highlight=highlight, **kwargs)


# ---------- Task 'lint' ----------


@task(
    name="lint",
    aliases=["l"],
)
def lint_task(ctx):
    """Lint only."""
    cmd = f"{PYTHON} -m tox -e lint"
    ctx.run(cmd, pty=True)


# ---------- Task 'test' ----------


@task(
    name="test",
    aliases=["t"],
)
def test_task(ctx):
    """Offline tests with the latest Python."""
    cmd = (
        f"{PYTHON} -m tox "
        "--skip-missing-interpreters false "
        f"-e {LATEST_PYTHON} "
        "-- --offline"
    )
    ctx.run(cmd, pty=True)


# ---------- Task 'check' ----------


@task(
    name="check",
    aliases=["c"],
)
def check_task(ctx):
    """Lint and all tests using the latest Python."""
    cmd = (
        f"{PYTHON} -m tox "
        "--skip-missing-interpreters false "
        f"-e lint,{LATEST_PYTHON}"
    )
    ctx.run(cmd, pty=True)


# ---------- Task 'check-all' ----------


@task(
    name="check-all",
    aliases=["ca"],
)
def check_all_task(ctx):
    """Lint and all tests using all Python versions."""
    cmd = f"{PYTHON} -m tox " "--skip-missing-interpreters false "
    ctx.run(cmd, pty=True)


# ---------- Task 'test-coverage' ----------


@task(
    name="test-coverage",
    aliases=["tc"],
)
def test_coverage_task(ctx):
    """Generate test coverage report."""
    cmd = (
        f"{PYTHON} -m tox --skip-missing-interpreters false "
        f"-e {LATEST_PYTHON} "
        "-- --cov --cov-report=html:_pytest-coverage"
    )
    ctx.run(cmd, pty=True)


# ---------- Task 'publish-test' ----------


@task(name="publish-test")
def publish_test_task(ctx):
    """Publish to test test Pypi."""
    cmd = f"{PYTHON} -m flit publish --repository testpypi"
    ctx.run(cmd, pty=True)


# ---------- Task 'publish' ----------


@task(name="publish")
def publish_task(ctx):
    """Publish to ptod Pypi."""
    cmd = f"{PYTHON} -m flit publish"
    ctx.run(cmd, pty=True)


# ---------- Task 'install-apio' ----------


@task(name="install-apio", aliases=["ia"])
def install_apio_task(ctx):
    """Install apio package from source code."""
    cmd = f"{PYTHON} -m pip install -e ."
    ctx.run(cmd, pty=True)
    ctx.run("apio --version", pty=True)
    out(
        "The source code here is now "
        "installed as the 'apio' pip package.\n"
        "Run 'apio' to test it.",
        style="green bold",
    )


# ---------- Task 'uninstall-apio' ----------


@task(name="uninstall-apio", aliases=["ua"])
def uninstall_apio_task(ctx):
    """Uninstall the apio package."""
    cmd = f"{PYTHON} -m pip uninstall -y apio"
    ctx.run(cmd, pty=True)
    out("The'apio' pip package is uninstalled.", style="green bold")


# ---------- Task 'install-deps' ----------


@task(name="install-deps", aliases=["deps"])
def install_deps_task(ctx):
    """Install development tools. Since we do at at the top of this file
    for every task, there is nothing to do here."""
    _ = ctx
    out("       required  installed")
    for name, ver in deps:
        out(f"{name:7s} {ver:9s} {version(name)}")


# ---------- Task 'docs-viewer' ----------


@task(name="docs-viewer", aliases=["dv"])
def install_docs_viewer_task(ctx):
    """Run a local http server to view the Apio docs."""
    ctx.run("mkdocs serve", pty=True)
