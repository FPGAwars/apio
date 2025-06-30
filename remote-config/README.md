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
