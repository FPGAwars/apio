## Apio Remote Configurations

This directory contains json files that are used to configure remotely apio clients.
As of Jan 2024, we use it only for controlling the versions of apio packages the apio
clients should load.

File files are keyed by the apio version, as shown by the command ``apio system info``
and the structure of each file should match the expectations of the respective apio
release.

This mechanism was introduced in apio 0.9.5. Prior versions of apio use VERSION
files in the respective package repositories are are not affected by the files
in this directory.

**IMPORTANT** [Dec 24th 2025] The main branch of this repository was changed from `master`
to a new branch called `main` and the old `master` branch is now frozen in read-only state. Please submit all future pull requests on the new branch `main`. The frozen branch should keep serving
URL such as https://github.com/fpgawars/apio/raw/develop/remote-config/apio-1.1.x.jsonc
to Apio versions before 1.2.0. Apio 1.2.0 and above fetching their remote config
from this `main` branch.