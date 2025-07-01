"""Tasks definitions for the 'invoke' command."""

# The 'invoke' pip packages is installed with apio.
# To print available tasks:
#   invoke -l

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

# -- Auto install the package 'tox' if not already installed.
if importlib.util.find_spec("tox") is None:
    out("[magenta]Auto installing the 'tox' package.[/]")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tox"])
assert importlib.util.find_spec("tox") is not None, "'tox' is not installed."

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
