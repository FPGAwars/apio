## Background

Apio GitHub repositories utilize `build-and-release` workflows that automatically
generate daily pre-releases based on the current content of each repository.
This includes pre-releases for packages such as `oss-cad-suite` and end-user
applications such as the Apio CLI and Apio IDE.

These pre-releases are automatically deleted after a few days unless manually
designated as stable by disabling the "pre-release" checkbox.

The general process for promoting a pre-release to a stable release available
to end users consists of the following steps:

1. Disable the "pre-release" checkbox to prevent automatic deletion after a few days.
2. Thoroughly test the pre-release (testing procedures vary by repository).
3. Mark the release as "latest" to indicate it is the current stable version for the repository (this by itself does not changed the published version).
4. Publish the release to make it accessible to users (publishing procedures vary by repository).

## Apio Package

This section describes the release process for Apio packages, such as `definitions` and `oss-cad-suite`.

### Testing

To be defined (TBD).

### Publishing

Apio packages are published by updating the relevant remote configuration
files located at https://github.com/FPGAwars/apio/tree/main/remote-config.

If a package introduces changes incompatible with the current public Apio
version, increment the Apio minor version (e.g., from 1.1.9 to 1.2.0) and create a new remote configuration file.

## Apio CLI

### Testing

New Apio CLI releases must be tested using all supported installation methods available to users:

- Installation via the provided installers and bundled files.
- Installation via `pip install` from the specific commit associated with the release.

Additionally, confirm that the `test` workflow completes successfully.

### Publishing

As of January 2026, publishing is performed exclusively to PyPI using the `publish-to-pypi` workflow.

## Apio IDE

### Testing

Test the Apio IDE by installing the `.vsix` file from the release in VS Code.
Use the "Install from VSIX" command in the Extensions view.
Testing must be conducted on all supported platforms.

### Publishing

Publish the Apio IDE by incrementing the version number in its `package.json` file and executing the `publish-to-vscode-marketplace` workflow.
