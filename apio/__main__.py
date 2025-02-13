#!venv/bin/python
"""Apio starting point."""

# -- The apio top click command.
from apio.commands.apio import cli as apio


def main():
    """Apio starting point."""

    # -- Invoke the apio's top click command node.
    apio()


if __name__ == "__main__":
    main()
