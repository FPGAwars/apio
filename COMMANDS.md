## APIO COMMANDS
* [apio](#apio) - Work with FPGAs with ease
  * [apio boards](#apio-boards) - List available board definitions.
  * [apio build](#apio-build) - Synthesize the bitstream.
  * [apio clean](#apio-clean) - Delete the apio generated files.
  * [apio create](#apio-create) - Create an apio.ini project file.
  * [apio docs](#apio-docs) - Read apio documentations.
    * [apio docs cli](#apio-docs-cli) - Apio's command line conventions.'
    * [apio docs options](#apio-docs-options) - Apio.ini options documentation.
    * [apio docs resources](#apio-docs-resources) - Information about online resources.
  * [apio drivers](#apio-drivers) - Manage the operating system drivers.
    * [apio drivers install](#apio-drivers-install) - Install drivers.
      * [apio drivers install ftdi](#apio-drivers-install-ftdi) - Install the ftdi drivers.
      * [apio drivers install serial](#apio-drivers-install-serial) - Install the serial drivers.
    * [apio drivers list](#apio-drivers-list) - List system drivers.
      * [apio drivers list ftdi](#apio-drivers-list-ftdi) - List the connected ftdi devices.
      * [apio drivers list serial](#apio-drivers-list-serial) - List the connected serial devices.
      * [apio drivers list usb](#apio-drivers-list-usb) - List connected USB devices.
    * [apio drivers uninstall](#apio-drivers-uninstall) - Uninstall drivers.
      * [apio drivers uninstall ftdi](#apio-drivers-uninstall-ftdi) - Uninstall the ftdi drivers.
      * [apio drivers uninstall serial](#apio-drivers-uninstall-serial) - Uninstall the serial drivers.
  * [apio examples](#apio-examples) - List and fetch apio examples.
    * [apio examples fetch](#apio-examples-fetch) - Fetch the files of an example.
    * [apio examples fetch-board](#apio-examples-fetch-board) - Fetch all examples of a board.
    * [apio examples list](#apio-examples-list) - List the available apio examples.
  * [apio format](#apio-format) - Format verilog source files.
  * [apio fpgas](#apio-fpgas) - List available FPGA definitions.
  * [apio graph](#apio-graph) - Generate a visual graph of the code.
  * [apio lint](#apio-lint) - Lint the verilog code.
  * [apio packages](#apio-packages) - Manage the apio packages.
    * [apio packages fix](#apio-packages-fix) - Fix broken apio packages.
    * [apio packages install](#apio-packages-install) - Install apio packages.
    * [apio packages list](#apio-packages-list) - List apio packages.
    * [apio packages uninstall](#apio-packages-uninstall) - Uninstall apio packages.
  * [apio preferences](#apio-preferences) - Manage the apio user preferences.
  * [apio raw](#apio-raw) - Execute commands directly from the Apio packages.
  * [apio report](#apio-report) - Report design utilization and timing.
  * [apio sim](#apio-sim) - Simulate a testbench with graphic results.
  * [apio system](#apio-system) - Provides system info.
    * [apio system colors](#apio-system-colors) - Show colors table.
    * [apio system info](#apio-system-info) - Show platform id and other info.
    * [apio system platforms](#apio-system-platforms) - List supported platforms ids.
  * [apio test](#apio-test) - Test all or a single verilog testbench module.
  * [apio upgrade](#apio-upgrade) - Check the latest Apio version.
  * [apio upload](#apio-upload) - Upload the bitstream to the FPGA.

<br>

### apio

```
Usage: apio [OPTIONS] COMMAND [ARGS]...

  WORK WITH FPGAs WITH EASE.

  Apio is an easy to use and open-source command-line suite designed to
  streamline FPGA programming. It supports a wide range of tasks,
  including linting, building, simulation, unit testing, and programming
  FPGA boards.

  An Apio project consists of a directory containing a configuration
  file named 'apio.ini', along with FPGA source files, testbenches, and
  pin definition files.

  Apio commands are intuitive and perform their intended functionalities
  right out of the box. For example, the command apio upload
  automatically compiles the design in the current directory and uploads
  it to the FPGA board.

  For detailed information about any Apio command, append the -h flag to
  view its help text. For example:

  apio build -h
  apio drivers ftdi install -h

  For more information about the Apio project, visit the official Apio
  Wiki https://github.com/FPGAwars/apio/wiki/Apio

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Build commands:
  apio build        Synthesize the bitstream.
  apio upload       Upload the bitstream to the FPGA.
  apio clean        Delete the apio generated files.

Verification commands:
  apio lint         Lint the verilog code.
  apio format       Format verilog source files.
  apio sim          Simulate a testbench with graphic results.
  apio test         Test all or a single verilog testbench module.
  apio report       Report design utilization and timing.
  apio graph        Generate a visual graph of the code.

Setup commands:
  apio create       Create an apio.ini project file.
  apio preferences  Manage the apio user preferences.
  apio packages     Manage the apio packages.
  apio drivers      Manage the operating system drivers.

Utility commands:
  apio docs         Read apio documentations.
  apio boards       List available board definitions.
  apio fpgas        List available FPGA definitions.
  apio examples     List and fetch apio examples.
  apio system       Provides system info.
  apio raw          Execute commands directly from the Apio packages.
  apio upgrade      Check the latest Apio version.

```

<br>

### apio boards

```
Usage: apio boards [OPTIONS]

  The command 'apio boards' lists the FPGA boards recognized by Apio.
  Custom boards can be defined by placing a custom 'boards.jsonc' file
  in the project directory, which will override Apio’s default
  'boards.jsonc' file.

  Examples:
    apio boards                   # List all boards.
    apio boards -v                # List with extra columns..
    apio boards | grep ecp5       # Filter boards results.

Options:
  -v, --verbose           Show detailed output.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio build

```
Usage: apio build [OPTIONS]

  The command 'apio build' processes the project’s source files and
  generates a bitstream file, which can then be uploaded to your FPGA.

  The 'apio build' command compiles all .v files (e.g., my_module.v) in
  the project directory, except those whose names end with '_tb' (e.g.,
  my_module_tb.v) which are assumed to be testbenches.

  Examples:
    apio build       # Build
    apio build -v    # Build with verbose info

Options:
  -p, --project-dir path  Set the root directory for the project.
  -v, --verbose           Show detailed output.
  --verbose-synth         Show detailed synth stage output.
  --verbose-pnr           Show detailed pnr stage output.
  -h, --help              Show this message and exit.

```

<br>

### apio clean

```
Usage: apio clean [OPTIONS]

  The command 'apio clean' removes temporary files generated in the
  project directory by previous Apio commands.

  Example:
    apio clean

Options:
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio create

```
Usage: apio create [OPTIONS]

  The command 'apio create' creates a new 'apio.ini' project file and is
  typically used when setting up a new Apio project.

  Examples:
    apio create --board alhambra-ii
    apio create --board alhambra-ii --top-module MyModule

  [Note] This command only creates a new 'apio.ini' file, rather than a
  complete and buildable project. To create complete projects, refer to
  the 'apio examples' command.

Options:
  -b, --board BOARD       Set the board.  [required]
  -t, --top-module name   Set the top level module name.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio docs

```
Usage: apio docs [OPTIONS] COMMAND [ARGS]...

  The command group 'apio docs' contains subcommands that provides
  various apio documentation and references information.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio docs cli        Apio's command line conventions.'
  apio docs options    Apio.ini options documentation.
  apio docs resources  Information about online resources.

```

<br>

### apio docs cli

```
Usage: apio docs cli [OPTIONS]

  The command 'apio docs cli' provides information the Apio's command
  line conventions and features.
  Examples:
    apio docs cli        # Shoe the cli documentation text.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio docs options

```
Usage: apio docs options [OPTIONS] [OPTION]

  The command 'apio docs options' provides information about the
  required project file 'apio.ini'.

  Examples:
    apio docs options              # List an overview and all options.
    apio docs options top-module   # List a single option.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio docs resources

```
Usage: apio docs resources [OPTIONS]

  The command 'apio docs resources' provides information about apio
  related online resources.

  Examples:
    apio docs resources   # Provides resources information

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers

```
Usage: apio drivers [OPTIONS] COMMAND [ARGS]...

  The command group 'apio drivers' contains subcommands to manage the
  drivers on your system.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers list       List system drivers.
  apio drivers install    Install drivers.
  apio drivers uninstall  Uninstall drivers.

```

<br>

### apio drivers install

```
Usage: apio drivers install [OPTIONS] COMMAND [ARGS]...

  The command group 'apio drivers install' includes subcommands that
  that install system drivers that are used to upload designs to FPGA
  boards.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers install ftdi    Install the ftdi drivers.
  apio drivers install serial  Install the serial drivers.

```

<br>

### apio drivers install ftdi

```
Usage: apio drivers install ftdi [OPTIONS]

  The command 'apio drivers install ftdi' installs on your system the
  FTDI drivers required by some FPGA boards.

  Examples:
    apio drivers install ftdi   # Install the ftdi drivers.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers install serial

```
Usage: apio drivers install serial [OPTIONS]

  The command 'apio drivers install serial' installs the necessary
  serial drivers on your system, as required by certain FPGA boards.

  Examples:
    apio drivers install serial  # Install the serial drivers.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers list

```
Usage: apio drivers list [OPTIONS] COMMAND [ARGS]...

  The command group 'apio drivers list' includes subcommands that that
  lists system drivers that are used with FPGA boards.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers list ftdi    List the connected ftdi devices.
  apio drivers list serial  List the connected serial devices.
  apio drivers list usb     List connected USB devices.

```

<br>

### apio drivers list ftdi

```
Usage: apio drivers list ftdi [OPTIONS]

  The command 'apio drivers list ftdi' displays the FTDI devices
  currently connected to your computer. It is useful for diagnosing FPGA
  board connectivity issues.

  Examples:
    apio drivers list ftdi    # List the ftdi devices.

  [Hint] This command uses the lsftdi utility, which can also be invoked
  directly with the 'apio raw -- lsftdi ...' command.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers list serial

```
Usage: apio drivers list serial [OPTIONS]

  The command 'apio drivers list serial' lists the serial devices
  connected to your computer. It is useful for diagnosing FPGA board
  connectivity issues.

  Examples:
    apio drivers list serial   # List the serial devices.

  [Hint] This command executes the utility lsserial, which can also be
  invoked using the command 'apio raw -- lsserial ...'.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers list usb

```
Usage: apio drivers list usb [OPTIONS]

  The command 'apio drivers list usb' runs the lsusb utility to list the
  USB devices connected to your computer. It is typically used for
  diagnosing  connectivity issues with FPGA boards.

  Examples:
    apio drivers list usb    # List the usb devices

  [Hint] You can also run the lsusb utility using the command 'apio raw
  -- lsusb ...'.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers uninstall

```
Usage: apio drivers uninstall [OPTIONS] COMMAND [ARGS]...

  The command group 'apio drivers uninstall' includes subcommands that
  that uninstall system drivers that are used to upload designs to FPGA
  boards.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers uninstall ftdi    Uninstall the ftdi drivers.
  apio drivers uninstall serial  Uninstall the serial drivers.

```

<br>

### apio drivers uninstall ftdi

```
Usage: apio drivers uninstall ftdi [OPTIONS]

  The command 'apio drivers uninstall ftdi' removes the FTDI drivers
  that may have been installed earlier.

  Examples:
    apio drivers uninstall ftdi   # Uninstall the ftdi drivers.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio drivers uninstall serial

```
Usage: apio drivers uninstall serial [OPTIONS]

  The command 'apio drivers uninstall serial' removes the serial drivers
  that you may have installed earlier.

  Examples:
    apio drivers uninstall serial    # Uninstall the serial drivers.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio examples

```
Usage: apio examples [OPTIONS] COMMAND [ARGS]...

  The command group 'apio examples' provides subcommands for listing and
  fetching Apio-provided examples. Each example is a self-contained
  mini-project that can be built and uploaded to an FPGA board.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio examples list         List the available apio examples.
  apio examples fetch        Fetch the files of an example.
  apio examples fetch-board  Fetch all examples of a board.

```

<br>

### apio examples fetch

```
Usage: apio examples fetch [OPTIONS] EXAMPLE

  The command 'apio examples fetch' fetches the files of the specified
  example to the current directory or to the directory specified by the
  '-dst' option. The destination directory does not need to exist, but
  if it does, it must be empty.

  Examples:
    apio examples fetch alhambra-ii/ledon
    apio examples fetch alhambra-ii/ledon -d foo/bar

Options:
  -d, --dst path  Set a different destination directory.
  -h, --help      Show this message and exit.

```

<br>

### apio examples fetch-board

```
Usage: apio examples fetch-board [OPTIONS] BOARD

  The command 'apio examples fetch-board' is used to fetch all the Apio
  examples for a specific board. The examples are copied to the current
  directory or to the specified destination directory if the '–-dst'
  option is provided.

  Examples:
    apio examples fetch-board alhambra-ii  # Fetch board examples.

Options:
  -d, --dst path  Set a different destination directory.
  -h, --help      Show this message and exit.

```

<br>

### apio examples list

```
Usage: apio examples list [OPTIONS]

  The command 'apio examples list' lists the available Apio project
  examples that you can use.

  Examples:
    apio examples list                     # List all examples
    apio examples list  -v                 # More verbose output.
    apio examples list | grep alhambra-ii  # Show alhambra-ii examples.
    apio examples list | grep -i blink     # Show blinking examples.

Options:
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.

```

<br>

### apio format

```
Usage: apio format [OPTIONS] [FILES]...

  The command 'apio format' formats Verilog source files to ensure
  consistency and style without altering their semantics. The command
  accepts the names of specific source files to format or formats all
  project source files by default.

  Examples:
    apio format                    # Format all source files.
    apio format -v                 # Same but with verbose output.
    apio format main.v main_tb.v   # Format the two files.

  The format command utilizes the format tool from the Verible project,
  which can be configured by setting its flags in the apio.ini project
  file For example:


  format-verible-options =
      --column_limit=80
      --indentation_spaces=4

  If needed, sections of source code can be protected from formatting
  using Verible formatter directives:

  // verilog_format: off
  ... untouched code ...
  // verilog_format: on

  For a full list of Verible formatter flags, refer to the documentation
  page online or use the command 'apio raw -- verible-verilog-format
  --helpful'.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.

```

<br>

### apio fpgas

```
Usage: apio fpgas [OPTIONS]

  The command 'apio fpgas' lists the FPGAs recognized by Apio. Custom
  FPGAs supported by the underlying Yosys toolchain can be defined by
  placing a custom 'fpgas.jsonc' file in the project directory,
  overriding Apio’s standard 'fpgas.jsonc' file.

  Examples:
    apio fpgas               # List all fpgas.
    apio fpgas -v            # List with extra columns.
    apio fpgas | grep gowin  # Filter FPGA results.

Options:
  -v, --verbose           Show detailed output.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio graph

```
Usage: apio graph [OPTIONS]

  The command 'apio graph' generates a graphical representation of the
  Verilog code in the project.

  Examples:
    apio graph               # Generate a svg file.
    apio graph --svg         # Generate a svg file.
    apio graph --pdf         # Generate a pdf file.
    apio graph --png         # Generate a png file.
    apio graph -t my_module  # Graph my_module module.


  [Hint] On Windows, type 'explorer _build/hardware.svg' to view the
  graph, and on Mac OS type 'open _build/hardware.svg'.

Options:
  --svg                   Generate a svg file (default).
  --png                   Generate a png file.
  --pdf                   Generate a pdf file.
  -p, --project-dir path  Set the root directory for the project.
  -t, --top-module name   Set the name of the top module to graph.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.

```

<br>

### apio lint

```
Usage: apio lint [OPTIONS]

  The command 'apio lint' scans the project's Verilog code and reports
  errors, inconsistencies, and style violations. The command uses the
  Verilator tool, which is included in the standard Apio installation.

  Examples:
    apio lint
    apio lint -t my_module
    apio lint --all

Options:
  --nostyle               Disable all style warnings.
  --nowarn nowarn         Disable specific warning(s).
  --warn warn             Enable specific warning(s).
  -a, --all               Enable all warnings, including code style warnings.
  -t, --top-module name   Restrict linting to this module and its
                          dependencies.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio packages

```
Usage: apio packages [OPTIONS] COMMAND [ARGS]...

  The command group 'apio packages' provides commands to manage the
  installation of Apio packages. These are not Python packages but
  Apio-specific packages containing various tools and data essential for
  the operation of Apio.

  The list of available packages depends on the operating system you are
  using and may vary between different operating systems.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio packages install    Install apio packages.
  apio packages uninstall  Uninstall apio packages.
  apio packages list       List apio packages.
  apio packages fix        Fix broken apio packages.

```

<br>

### apio packages fix

```
Usage: apio packages fix [OPTIONS]

  The command 'apio packages fix' removes broken or obsolete packages
  that are listed as broken by the command 'apio packages list'.

  Examples:
    apio packages fix     # Fix package errors, if any.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio packages install

```
Usage: apio packages install [OPTIONS] PACKAGE

  The command 'apio packages install' installs Apio packages that are
  required for the operation of Apio on your system.

  Examples:
    apio packages install                   # Install missing packages.
    apio pack inst                          # Same, with shortcuts
    apio packages install --force           # Reinstall all packages.
    apio packages install oss-cad-suite     # Install package.
    apio packages install examples@0.0.32   # Install a specific
  version.

  Adding the '--force' option forces the reinstallation of existing
  packages; otherwise, packages that are already installed correctly
  remain unchanged.

Options:
  -f, --force    Force installation.
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.

```

<br>

### apio packages list

```
Usage: apio packages list [OPTIONS]

  The command 'apio packages list' lists the available and installed
  Apio packages. The list of available packages depends on the operating
  system you are using and may vary between operating systems.

  Examples:
    apio packages list

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio packages uninstall

```
Usage: apio packages uninstall [OPTIONS] PACKAGE

  The command 'apio packages uninstall' removes installed Apio packages
  from your system. The command does not uninstall the Apio tool itself.

  Examples:
    apio packages uninstall                    # Uninstall all packages
    apio packages uninstall oss-cad-suite      # Uninstall a package
    apio packages uninstall verible examples   # Uninstall two packages

Options:
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.

```

<br>

### apio preferences

```
Usage: apio preferences [OPTIONS]

  The command 'apio preferences' allows to view and manage the setting
  of the apio's user's preferences. These settings are stored in the
  'profile.json' file in the apio home directory (e.g. '~/.apio') and
  apply to all apio projects.

  Examples:
    apio preferences -t light       # Colors for light backgrounds.
    apio preferences -t dark        # Colors for dark backgrounds.
    apio preferences -t no-colors   # No colors.
    apio preferences --list         # List current preferences.
    apio pref -t dark               # Using command shortcut.

Options:
  -t, --theme [light|dark|no-colors]
                                  Set colors theme name.
  -l, --list                      List the preferences.
  -h, --help                      Show this message and exit.

```

<br>

### apio raw

```
Usage: apio raw [OPTIONS] COMMAND

  The command 'apio raw' allows you to bypass Apio and run underlying
  tools directly. This is an advanced command that requires familiarity
  with the underlying tools.

  Before running the command, Apio temporarily modifies system
  environment variables such as '$PATH' to provide access to its
  packages. To view these environment changes, run the command with the
  '-v' option.

  Examples:
    apio raw    -- yosys --version      # Yosys version
    apio raw -v -- yosys --version      # Verbose apio info.
    apio raw    -- yosys                # Yosys interactive mode.
    apio raw    -- icepll -i 12 -o 30   # Calc ICE PLL.
    apio raw    -- which yosys          # Lookup a command.
    apio raw -v                         # Show apio env setting.
    apio raw -h                         # Show this help info.

  The '--' marker is used to separate between the arguments of the apio
  command itself and those of the executed command.

Options:
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.

```

<br>

### apio report

```
Usage: apio report [OPTIONS]

  The command 'apio report' provides information on the utilization and
  timing of the design. It is useful for analyzing utilization
  bottlenecks and verifying that the design can operate at the desired
  clock speed.

  Examples:
    apio report            # Print report.
    apio report --verbose  # Print extra information.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.

```

<br>

### apio sim

```
Usage: apio sim [OPTIONS] [TESTBENCH]

  The command 'apio sim' simulates the default or the specified
  testbench file and displays its simulation results in a graphical
  GTKWave window. The testbench is expected to have a name ending with
  _tb, such as main_tb.v or main_tb.sv. The default testbench file can
  be specified using the apio.ini option 'default-testbench'. If
  'default-testbench' is not specified and the project has exactly one
  testbench file, that file will be used as the default testbench.

  Example:
    apio sim                   # Simulate the default testbench.
    apio sim my_module_tb.v    # Simulate the specified testbench.

  [Important] Avoid using the Verilog '$dumpfile()' function in your
  testbenches, as this may override the default name and location Apio
  sets for the generated .vcd file.

  The sim command defines the INTERACTIVE_SIM macro, which can be used
  in the testbench to distinguish between 'apio test' and 'apio sim'.
  For example, you can use this macro to ignore certain errors when
  running with 'apio sim' and view the erroneous signals in GTKWave.

  For a sample testbench that utilizes this macro, see the example at:
  https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbe
  nch

  [Hint] When configuring the signals in GTKWave, save the configuration
  so you don’t need to repeat it each time you run the simulation.

Options:
  -f, --force             Force simulation.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio system

```
Usage: apio system [OPTIONS] COMMAND [ARGS]...

  The command group 'apio system' contains subcommands that provide
  information about the system and Apio’s installation.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio system platforms  List supported platforms ids.
  apio system info       Show platform id and other info.
  apio system colors     Show colors table.

```

<br>

### apio system colors

```
Usage: apio system colors [OPTIONS]

  The command 'apio system colors' shows how ansi colors are rendered on
  the platform, and is typically used to diagnose color related issues.
  While the color name and styling is always handled by the Python Rich
  library, the output is done via three different libraries, based on
  the user's selection.


  Examples:
    apio system colors          # Rich library output (default)
    apio system colors --rich   # Same as above.
    apio system colors --click  # Click library output.
    apio system colors --print  # Python's print() output.
    apio sys col -p             # Using shortcuts.

Options:
  -r, --rich   Output using the rich lib.
  -c, --click  Output using the click lib.
  -p, --print  Output using python's print().
  -h, --help   Show this message and exit.

```

<br>

### apio system info

```
Usage: apio system info [OPTIONS]

  The command 'apio system info' provides general information about your
  system and Apio installation, which is useful for diagnosing Apio
  installation issues.

  Examples:
    apio system info   # Show general info.

  [Advanced] The default location of the Apio home directory, where apio
  saves preferences and packages, is in the '.apio' directory under the
  user home directory but can be changed using the system environment
  variable 'APIO_HOME_DIR'.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio system platforms

```
Usage: apio system platforms [OPTIONS]

  The command 'apio system platforms' lists the platform IDs supported by
  Apio, with the effective platform ID of your system highlighted.

  [code]Examples:   apio system platforms   # List supported platform
  ids.[/code]

  [Advanced] The automatic platform ID detection of Apio can be overridden by
  defining a different platform ID using the APIO_PLATFORM environment
  variable.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio test

```
Usage: apio test [OPTIONS] [TESTBENCH_FILE]

  The command 'apio test' simulates one or all the testbenches in the
  project and is useful for automated testing of your design.
  Testbenches are expected to have names ending with _tb (e.g.,
  my_module_tb.v) and should exit with the '$fatal' directive if an
  error is detected.

  Examples:
    apio test                 # Run all *_tb.v testbenches.
    apio test my_module_tb.v  # Run a single testbench.

  [Important] Avoid using the Verilog '$dumpfile()' function in your
  testbenches, as this may override the default name and location Apio
  sets for the generated .vcd file.

  For a sample testbench compatible with Apio features, see:
  https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbe
  nch

  [Hint] To simulate a testbench with a graphical visualization of the
  signals, refer to the 'apio sim' command.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio upgrade

```
Usage: apio upgrade [OPTIONS]

  The command 'apio upgrade' checks for the version of the latest Apio
  release and provides upgrade directions if necessary.

  Examples:
    apio upgrade

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio upload

```
Usage: apio upload [OPTIONS]

  The command 'apio upload' builds the bitstream file (similar to the
  'apio build' command) and uploads it to the FPGA board.

  Examples:
    apio upload

Options:
  --serial-port serial-port  Set the serial port.
  --ftdi-id ftdi-id          Set the FTDI id.
  -s, --sram                 Perform SRAM programming.
  -f, --flash                Perform FLASH programming.
  -p, --project-dir path     Set the root directory for the project.
  -h, --help                 Show this message and exit.

```
