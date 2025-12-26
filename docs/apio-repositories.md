# Apio Repositories

Apio uses GitHub repositories under the `FPGAwars` organization for its source code, documentation, daily builds, and runtime packages.

**Apio applications**

| Repository                                                      | Application | Comments          |
| :-------------------------------------------------------------- | :---------- | :---------------- |
| [fpgawars/apio](https://github.com/fpgawars/apio)               | Apio CLI    | Command line tool |
| [fpgawars/apio-vscode](https://github.com/fpgawars/apio-vscode) | Apio IDE    | Vs Code extension |

**Apio packages**

| Repository                                                                      | Package name    | Comments     |
| :------------------------------------------------------------------------------ | :-------------- | :----------- |
| [fpgawars/apio-definitions](https://github.com/fpgawars/apio-definitions)       | `definitions`   |              |
| [fpgawars/tools-drivers](https://github.com/fpgawars/tools-drivers)             | `drivers`       | Windows only |
| [fpgawars/apio-examples](https://github.com/fpgawars/apio-examples)             | `examples`      |              |
| [fpgawars/tools-graphviz](https://github.com/fpgawars/tools-graphviz)           | `graphviz`      | Windows only |
| [fpgawars/tools-oss-cad-suite](https://github.com/fpgawars/tools-oss-cad-suite) | `oss-cad-suite` |              |
| [fpgawars/tools-verible](https://github.com/fpgawars/tools-verible)             | `verible`       |              |

**Utilities**

| Repository                                                            | Description                                           |
| :-------------------------------------------------------------------- | :---------------------------------------------------- |
| [fpgawars/apio-workflows](https://github.com/fpgawars/apio-workflows) | Provides common functionalities for Apio's workflows. |

For easier tracking and maintenance, all bug reports and discussions are consolidated in the main Apio repository: [fpgawars/apio](https://github.com/fpgawars/apio), which also serves as the project’s homepage.

## Daily build workflows

The Apio repositories contain build workflows, typically at `.github/workflows/build-and-release.yaml` which builds the content of the repo and publish it as a temporary **pre-release** that is deleted after a few days.

- To make a release permanent, edit it in the Github dashboard and turn off the **Set as a pre-release** checkbox.

- To make an permanent release the official latest release, edit it in the Github dashboard and check the **Set as the latest release** checkbox.

Note that declaring a release permanent and the latest doesn't necessary make it used, and in most cases it needs to be 'published' as outlined in the table

| Build type                                          | Publishing                                                                                                                                                                                                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Apio packages such as 'examples' or 'oss-cad-suite' | • Update the packages versions in the relevant [apio remote config files](https://github.com/fpgawars/apio/tree/main/remote-config) for the new packages to be picked up.                                                                                        |
| Apio                                                | • Publish in the various 'markets' such as PyPi. <br> <br> • Update the Apio build version in the Apio VS Code [constants.js](https://github.com/fpgawars/apio-vscode/blob/main/constants.js) file to have the new apio version picked up by the VS Code extension. |
| Apio VS Code extension                              | • Publish in the VS Code market.                                                                                                                                                                                                                                    |

# Guidelines for daily build workflows

1. Each repo should build it's own stuff.
2. The build workflow should not be triggered by a push but only daily on cron, and manually from the github dashboard.
3. An automatic daily build should create a new **pre-release** with name and tag `yyyy-mm-dd` (based on current UTC time).
4. The daily build should run on cron at midnight UTC (`cron: "0 0 * * *"`) to reduce the chance of overwriting a manual build with same date.
5. Only a few N pre-releases should be kept (use automatic cleanup in the build daily workflow).
6. If the build workflow deals with binaries (e.g. verible or oss-cad-suite packages), it should run virus scan (e.g. ClamAV).
7. The builds should be from the latest commit of the repo (down the road we can add manual sha overrides).
