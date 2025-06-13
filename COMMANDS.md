## APIO COMMANDS
* [apio](#apio) - Work with FPGAs with ease
  * [apio api](#apio-api) - Apio programmatic interface.
    * [apio api get-boards](#apio-api-get-boards) - Retrieve boards information.
    * [apio api get-fpgas](#apio-api-get-fpgas) - Retrieve FPGAs information.
    * [apio api scan-devices](#apio-api-scan-devices) - Scan and report available devices.
  * [apio boards](#apio-boards) - List available board definitions.
  * [apio build](#apio-build) - Synthesize the bitstream.
  * [apio clean](#apio-clean) - Delete the apio generated files.
  * [apio create](#apio-create) - Create an apio.ini project file.
  * [apio devices](#apio-devices) - List attached devices.
    * [apio devices serial](#apio-devices-serial) - List serial devices.
    * [apio devices usb](#apio-devices-usb) - List USB devices.
  * [apio drivers](#apio-drivers) - Manage the operating system drivers.
    * [apio drivers install](#apio-drivers-install) - Install drivers.
      * [apio drivers install ftdi](#apio-drivers-install-ftdi) - Install the ftdi drivers.
      * [apio drivers install serial](#apio-drivers-install-serial) - Install the serial drivers.
    * [apio drivers uninstall](#apio-drivers-uninstall) - Uninstall drivers.
      * [apio drivers uninstall ftdi](#apio-drivers-uninstall-ftdi) - Uninstall the ftdi drivers.
      * [apio drivers uninstall serial](#apio-drivers-uninstall-serial) - Uninstall the serial drivers.
  * [apio examples](#apio-examples) - List and fetch apio examples.
    * [apio examples fetch](#apio-examples-fetch) - Fetch the files of an example.
    * [apio examples list](#apio-examples-list) - List the available apio examples.
  * [apio format](#apio-format) - Format verilog source files.
  * [apio fpgas](#apio-fpgas) - List available FPGA definitions.
  * [apio graph](#apio-graph) - Generate a visual graph of the code.
  * [apio info](#apio-info) - Apio's info and info.
    * [apio info cli](#apio-info-cli) - Command line conventions.
    * [apio info colors](#apio-info-colors) - Colors table.
    * [apio info files](#apio-info-files) - Apio project files types.
    * [apio info platforms](#apio-info-platforms) - Supported platforms.
    * [apio info resources](#apio-info-resources) - Additional resources.
    * [apio info system](#apio-info-system) - Show system information.
  * [apio lint](#apio-lint) - Lint the source code.
  * [apio packages](#apio-packages) - Manage the apio packages.
    * [apio packages list](#apio-packages-list) - List apio packages.
    * [apio packages update](#apio-packages-update) - Update apio packages.
  * [apio preferences](#apio-preferences) - Manage the apio user preferences.
  * [apio raw](#apio-raw) - Execute commands directly from the Apio packages.
  * [apio report](#apio-report) - Report design utilization and timing.
  * [apio sim](#apio-sim) - Simulate a testbench with graphic results.
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
  apio lint         Lint the source code.
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
  apio devices      List attached devices.

Utility commands:
  apio boards       List available board definitions.
  apio fpgas        List available FPGA definitions.
  apio examples     List and fetch apio examples.
  apio info         Apio's info and info.
  apio raw          Execute commands directly from the Apio packages.
  apio api          Apio programmatic interface.
  apio upgrade      Check the latest Apio version.

```

<br>

### apio api

```
Usage: apio api [OPTIONS] COMMAND [ARGS]...

  The command group 'apio apio' contains subcommands that that are
  intended to be used by tools and programs such as icestudio, rather
  than being used directly by users.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio api get-boards    Retrieve boards information.
  apio api get-fpgas     Retrieve FPGAs information.
  apio api scan-devices  Scan and report available devices.

```

<br>

### apio api get-boards

```
Usage: apio api get-boards [OPTIONS]

  The command 'apio api get-boards' exports apio boards information as a
  JSON document.

  The optional flag '--timestamp' allows the caller to embed in the JSON
  document a known timestamp that allows to verify that the JSON
  document was indeed was generated by the same invocation.

  Examples:
    apio api get-boards                # Write to stdout
    apio api get-boards  -o apio.json  # Write to a file

Options:
  -t, --timestamp text    Set a user provided timestamp.
  -o, --output file-name  Set output file.
  -f, --force             Overwrite output file.
  -h, --help              Show this message and exit.

```

<br>

### apio api get-fpgas

```
Usage: apio api get-fpgas [OPTIONS]

  The command 'apio api get-fpgas' exports apio FPGAss information as a
  JSON document.

  The optional flag '--timestamp' allows the caller to embed in the JSON
  document a known timestamp that allows to verify that the JSON
  document was indeed was generated by the same invocation.

  Examples:
    apio api get-fpgas                # Write to stdout
    apio api get-fpgas  -o apio.json  # Write to a file

Options:
  -t, --timestamp text    Set a user provided timestamp.
  -o, --output file-name  Set output file.
  -f, --force             Overwrite output file.
  -h, --help              Show this message and exit.

```

<br>

### apio api scan-devices

```
Usage: apio api scan-devices [OPTIONS]

  The command 'apio api scan-devices' scans and report the available usb
  and serial devices.

  The optional flag '--timestamp' allows the caller to embed in the JSON
  document a known timestamp that allows to verify that the JSON
  document was indeed was generated by the same invocation.

  Examples:
    apio api scan-devices                # Write to stdout
    apio api scan-devices  -o apio.json  # Write to a file

Options:
  -t, --timestamp text    Set a user provided timestamp.
  -o, --output file-name  Set output file.
  -f, --force             Overwrite output file.
  -h, --help              Show this message and exit.

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

  The command 'apio build' processes the project’s synthesis source
  files and generates a bitstream file, which can then be uploaded to
  your FPGA.

  Examples:
    apio build                   # Typical usage
    apio build -e debug          # Set the apio.ini env.
    apio build -v                # Verbose info (all)
    apio build --verbose-synth   # Verbose synthesis info
    apio build --verbose-pnr     # Verbose place and route info

  NOTES:
  * The files are sorted in a deterministic lexicographic order.
  * You can specify the name of the top module in apio.ini.
  * The build command ignores testbench files (*_tb.v, and *_tb.sv).
  * It is unnecessary to run 'apio build' before 'apio upload'.
  * To force a rebuild from scratch use the command 'apio clean' first.

Options:
  -e, --env name          Set the apio.ini env.
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

  The command 'apio clean' removes all the output files previously
  generated by apio commands.

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

  [NOTE] This command only creates a new 'apio.ini' file, rather than a
  complete and buildable project. To create complete projects, refer to
  the 'apio examples' command.

Options:
  -b, --board BOARD       Set the board.  [required]
  -t, --top-module name   Set the top level module name.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio devices

```
Usage: apio devices [OPTIONS] COMMAND [ARGS]...

  The command group 'apio devices' includes subcommands that lists
  devices
  that are attached to the computer. It's main usage is diagnostics or
  devices connectivity and drivers.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio devices usb     List USB devices.
  apio devices serial  List serial devices.

```

<br>

### apio devices serial

```
Usage: apio devices serial [OPTIONS]

  The command 'apio devices serial' displays the serial devices
  currently connected to your computer. It is useful for diagnosing FPGA
  board connectivity issues.

  Examples:
    apio devices serial    # List the serial devices.

  Note that devices such as FTDI FTDI2232 that have more than one
  channel are listed as multiple rows, one for each of their serial
  ports.

  On Windows, manufacturer and product strings of FTDI based devices may
  show their FTDI generic values rather than the custom values such such
  as 'Alhambra II' set by the device manufacturer.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio devices usb

```
Usage: apio devices usb [OPTIONS]

  The command 'apio devices usb' displays the USB devices currently
  connected to your computer. It is useful for diagnosing FPGA board
  connectivity issues.

  Examples:
    apio devices usb    # List the usb devices.

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
  apio examples list   List the available apio examples.
  apio examples fetch  Fetch the files of an example.

```

<br>

### apio examples fetch

```
Usage: apio examples fetch [OPTIONS] EXAMPLE

  The command 'apio examples fetch' fetches a single examples or all the
  examples of a board. The destination directory is either the current
  directory or the directory specified with '--dst' and it should be
  empty and non existing.

  Examples:
    apio examples fetch alhambra-ii/ledon    # Single example
    apio examples fetch alhambra-ii          # All board's examples
    apio examples fetch alhambra-ii -d work  # Explicit destination

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

  The command 'apio format' formats the project's source files to ensure
  consistency and style without altering their semantics. The command
  accepts the names of specific source files to format or formats all
  project source files by default.

  Examples:
    apio format                    # Format all source files.
    apio format -v                 # Same but with verbose output.
    apio format main.v main_tb.v   # Format the two files.

  [NOTE] The file arguments are relative to the project directory, even
  if the --project-dir option is used.

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
  -e, --env name          Set the apio.ini env.
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
  design.

  Examples:
    apio graph               # Generate a svg file.
    apio graph --svg         # Generate a svg file.
    apio graph --pdf         # Generate a pdf file.
    apio graph --png         # Generate a png file.
    apio graph -t my_module  # Graph my_module module.


  [Hint] On Windows, type 'explorer _build/default/hardware.svg' to view
  the graph, and on Mac OS type 'open _build/default/hardware.svg' (if
  your env is different than 'default' change the commands accordingly).

Options:
  --svg                   Generate a svg file (default).
  --png                   Generate a png file.
  --pdf                   Generate a pdf file.
  -e, --env name          Set the apio.ini env.
  -p, --project-dir path  Set the root directory for the project.
  -t, --top-module name   Set the name of the top module to graph.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.

```

<br>

### apio info

```
Usage: apio info [OPTIONS] COMMAND [ARGS]...

  The command group 'apio info' contains subcommands that provide
  various information about Apio usage, Apio's installation, and your
  system.

Options:
  -h, --help  Show this message and exit.

Documentation:
  apio info cli        Command line conventions.
  apio info files      Apio project files types.
  apio info resources  Additional resources.

Information:
  apio info platforms  Supported platforms.
  apio info system     Show system information.
  apio info colors     Colors table.

```

<br>

### apio info cli

```
Usage: apio info cli [OPTIONS]

  The command 'apio info cli' provides information the Apio's command
  line conventions and features.
  Examples:
    apio info cli        # Shoe the cli documentation text.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio info colors

```
Usage: apio info colors [OPTIONS]

  The command 'apio info colors' shows how ansi colors are rendered on
  the platform, and is typically used to diagnose color related issues.
  While the color name and styling is always handled by the Python Rich
  library, the output is done via three different libraries, based on
  the user's selection.


  Examples:
    apio info colors          # Rich library output (default)
    apio info colors --rich   # Same as above.
    apio info colors --click  # Click library output.
    apio info colors --print  # Python's print() output.
    apio sys col -p             # Using shortcuts.

Options:
  -r, --rich   Output using the rich lib.
  -c, --click  Output using the click lib.
  -p, --print  Output using python's print().
  -h, --help   Show this message and exit.

```

<br>

### apio info files

```
Usage: apio info files [OPTIONS]

  The command 'apio info files' provides information about the various
  files types used in an Apio project.

  Examples:
    apio info files

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio info platforms

```
Usage: apio info platforms [OPTIONS]

  The command 'apio info platforms' lists the platform IDs supported by Apio,
  with the effective platform ID of your system highlighted.

  [code]Examples:   apio info platforms   # List supported platform
  ids.[/code]

  [Advanced] The automatic platform ID detection of Apio can be overridden by
  defining a different platform ID using the APIO_PLATFORM environment
  variable.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio info resources

```
Usage: apio info resources [OPTIONS]

  The command 'apio info resources' provides information about apio
  related online resources.

  Examples:
    apio info resources   # Provides resources information

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio info system

```
Usage: apio info system [OPTIONS]

  The command 'apio info system' provides general information about your
  system and Apio installation, which is useful for diagnosing Apio
  installation issues.

  Examples:
    apio info system   # System info.

  [Advanced] The default location of the Apio home directory, where apio
  saves preferences and packages, is in the '.apio' directory under the
  user home directory but can be changed using the system environment
  variable 'APIO_HOME'.

Options:
  -h, --help  Show this message and exit.

```

<br>

### apio lint

```
Usage: apio lint [OPTIONS]

  The command 'apio lint' scans the project's source files and reports
  errors, inconsistencies, and style violations. The command uses the
  Verilator tool, which is included with the standard Apio installation.

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
  -e, --env name          Set the apio.ini env.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

```

<br>

### apio packages

```
Usage: apio packages [OPTIONS] COMMAND [ARGS]...

  The command group 'apio packages' provides commands to manage the
  installation of Apio packages. These are not Python packages but Apio
  packages containing various tools and data essential for the operation
  of Apio.

  The list of available packages depends on the operating system you are
  using and may vary between different operating systems.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio packages update  Update apio packages.
  apio packages list    List apio packages.

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
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.

```

<br>

### apio packages update

```
Usage: apio packages update [OPTIONS]

  The command 'apio packages update' updates the installed Apio packages
  to their latest requirements.

  Examples:
    apio packages update            # Update packages
    apio pack upd                   # Same, with shortcuts
    apio packages update --force    # Force reinstallation from scratch
    apio packages update --verbose  # Provide additional info

  Adding the '--force' option forces the reinstallation of existing
  packages; otherwise, packages that are already installed correctly
  remain unchanged.

  It is highly recommended to run the 'apio packages update' once in a
  while because it check the Apio remote server for the latest packages
  versions which may included fixes and enhancements such as new
  examples that were added to the examples package.

Options:
  -f, --force    Force reinstallation.
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
  -c, --colors                    List themes colors.
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
  -e, --env name          Set the apio.ini env.
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
  _tb, such as 'main_tb.v' or 'main_tb.sv'. The default testbench file
  can be specified using the apio.ini option 'default-testbench'. If
  'default-testbench' is not specified and the project has exactly one
  testbench file, that file will be used as the default testbench.

  Example:
    apio sim                   # Simulate the default testbench.
    apio sim my_module_tb.v    # Simulate the specified testbench.
    apio sim my_module_tb.sv   # Simulate the specified testbench.

  [NOTE] Testbench specification is always the testbench file path
  relative to the project directory, even if using the '--project-dir'
  option.

  [IMPORTANT] Avoid using the Verilog '$dumpfile()' function in your
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
  -e, --env name          Set the apio.ini env.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.

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

  [NOTE] Testbench specification is always the testbench file path
  relative to the project directory, even if using the '--project-dir'
  option.

  [IMPORTANT] Avoid using the Verilog '$dumpfile()' function in your
  testbenches, as this may override the default name and location Apio
  sets for the generated .vcd file.

  For a sample testbench compatible with Apio features, see:
  https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbe
  nch

  [Hint] To simulate a testbench with a graphical visualization of the
  signals, refer to the 'apio sim' command.

Options:
  -e, --env name          Set the apio.ini env.
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
    apio upload                            # Typical invocation
    apio upload -s /dev/cu.usbserial-1300  # Select serial port
    apio upload -n FTXYA34Z                # Select serial number

  Typically the simple form 'apio upload' is sufficient to locate and
  program the FPGA board. The optional flags '--serial-port' and
  '--serial-num' allows to select the desired board if more than one
  matching board is detected.

  [HINT] You can use the command 'apio devices' to list the connected
  USB and serial devices and the command 'apio drivers' to install and
  uninstall device drivers.

  [HINT] The default programmer command of your board can be overridden
  using the apio.ini option 'programmer-cmd'.

Options:
  -s, --serial-port serial-port  Set the serial port.
  -n, --serial-num serial-num    Select the device's USB serial number.
  -e, --env name                 Set the apio.ini env.
  -p, --project-dir path         Set the root directory for the project.
  -h, --help                     Show this message and exit.

```
