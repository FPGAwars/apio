# Creating an Apio version

!!! warning "Page under construction"
    The details of the release process is not finalized yet.

## Cutting a release candidate

TBD

## Testing a release candidate

TBD

## Releasing a release candidate as an official release

TBD

<br>

Things to pay attention to:

- Determine the increment level, patch, minor, or major.
- Setting the new apio version in `apio/__init__`.
- Creating a `.jsonc` remote config file at https://github.com/FPGAwars/apio/tree/develop/remote-config with the desired package versions.
- Waiting for the next daily apio build and make sure the build is green (use its apio commit as the cutoff commit)
- Making sure that the apio test workflows are green for the cutoff commit.
- Creating a new release in the apio repo and adding to it the build files from the build repo.
- Somewhere along these steps, test the release candidate.

<br>
