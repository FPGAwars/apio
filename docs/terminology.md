- **APIO_DEBUG** - An environment variable that enables debug output during command execution.
  Accepts values from 1 to 10, where 10 is the most verbose.

- **Apio home** - The directory where Apio stores its profile file. Defaults to
  `~/.apio`, but can be changed using the `APIO_HOME` environment variable as done
  during the automated tests.

  - **Apio packages dir** - The directory where Apio stores its installed packages. Defaults to
  `~/.apio/packages`, but can be changed using the `APIO_PACKAGES` environment variable as done
  during the automated tests.

- **ApioContext** - A key Apio class instantiated at the start of each command. It provides
  access to Apio's resources and project and profile information.

- **Board** - Defines an FPGA board, either in the Apio definitions or 
  or a project-local `boards.jsonc` file.

- **Click** - A third-party Python library for building command-line applications with
  subcommands. It handles Apio's command tree, argument parsing, and help text.
  Click commands are functions named `cli` and are configured using decorators.

- **Drivers** - OS drivers that may be required for programming some FPGA boards.
  Missing drivers can prevent board detection by `apio upload` or
  `apio devices list`. Install them with `apio drivers install`.

- **FPGA** - Defines an FPGA device, either in
  the Apio standard definition or a project-local `fpgas.jsonc` file.

- **Invoke** - A third-party Python tool used to run development tasks defined in
  `tasks.py`. For example, `invoke check` runs comprehensive pre-submit
  tests.

- **MkDocs** - An open-source tool for publishing Apio's documentation to GitHub Pages.
  Content is stored in `mkdocs.yml` and the `docs` directory. It is published
  automatically via a GitHub workflow.

- **Packages** - Tools such as Yosys that Apio manages. Packages are downloaded and stored
  under `~/.apio/packages` and are managed using the `apio packages` command.
  Some packages are cross-platform, while others are platform-specific.

- **Platforms** - The operating systems that Apio supports. To list them, run
  `apio info platforms`.

- **Profile** - An Apio class that abstracts the Apio profile file, typically located at
  `~/.apio/profile.json`.

- **Programmer** - Defines an FPGA programming tool, either in
  the Apio standard definitions or a project-local `programmers.jsonc` file.

- **Project** - An Apio class that abstracts the project configuration defined in the
  `apio.ini` file.

- **Protocol Buffers** - A Google-developed open-source language/tool for serializing structured data.
  Apio uses it to communicate with the SCons subprocess. Definitions are in
  `apio/common/proto/apio.proto` and should be recompiled via
  `update-protos.sh` when modified.

- **Remote config** - A `.jsonc` configuration file stored in the Apio GitHub repository under
  `remote-config`. Apio occasionally fetches this file to check for updated
  package versions.

- **Rich** - A third-party Python library for managing Apio's terminal output, including
  colored text and data tables.

- **SCons** - A third-party Python 'make' like build tool used to run Apio project operations
  incrementally. SCons prevents redundant operations such as repeating Yosys
  synthesis or Nextpnr place-and-route. Apio invokes SCons as a subprocess
  only for tasks requiring incremental builds.

- **Workflows** - GitHub Actions workflows stored in the `.github/workflows` directory of Apio
  repositories.
