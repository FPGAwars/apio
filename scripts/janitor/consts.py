"""
Janitor consts
"""

# -- Set of apio repos. This set should match the repo list in apio docs
# -- https://fpgawars.github.io/apio/docs/apio-repositories
# --
# -- The repo fpgawars/apio-workflows is not included since it's is not part
# -- of the Apio releases.
APIO_REPOS = [
    # -- Publishing roots.
    "fpgawars/apio",
    "fpgawars/apio-vscode",
    # -- packages
    "fpgawars/apio-definitions",
    "fpgawars/tools-drivers",
    "fpgawars/tools-graphviz",
    "fpgawars/tools-openxc7",
    "fpgawars/tools-oss-cad-suite",
    "fpgawars/tools-verible",
    "fpgawars/apio-examples",  # Frozen
]


# -- The number of latest prereleases to keep in each repo.
NUM_PRE_RELEASES_TO_KEEP = 7
