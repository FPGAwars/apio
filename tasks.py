"""Tasks definitions for the 'invoke' command."""

# The 'invoke' pip packages is installed with apio.
# A few useful commands
#   invoke --list        # Show available tasks
#   invoke lint          # Lint the python code
#   invoke test          # Run the offline tests (fast)
#   invoke check         # Run lint and all the tests (slow)
#   invoke install-apio  # Install to run 'apio' from the source code here.

import sys
import importlib.util
import subprocess
from invoke import task
from rich import print as out


# -- NOTE: The first sentence of a task docstring is also its help string
# -- which is printed when running 'invoke --list'.

LATEST_PYTHON = "py313"

# -- The python interpreter that we currently use.
PYTHON = sys.executable

# -- Auto install packages that are not Apio dependencies but required here.
modules = ["tox", "flit"]
for module in modules:
    if importlib.util.find_spec(module) is None:
        out(f"[magenta]Auto installing package '{module}'.[/]")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
    assert (
        importlib.util.find_spec(module) is not None
    ), f"'{module}' is not installed."


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


# ---------- Task 'uninstall-apio' ----------


@task(name="uninstall-apio", aliases=["ua"])
def uninstall_apio_task(ctx):
    """Uninstall the apio package."""
    cmd = f"{PYTHON} -m pip uninstall apio"
    ctx.run(cmd, pty=True)
