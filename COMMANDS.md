## APIO COMMANDS
* [apio](#apio) - Work with FPGAs with ease
  * [apio boards](#apio-boards) - List available board definitions.
  * [apio build](#apio-build) - Synthesize the bitstream.
  * [apio clean](#apio-clean) - Delete the apio generated files.
  * [apio create](#apio-create) - Create an apio.ini project file.
  * [apio drivers](#apio-drivers) - Manage the operating system drivers.
    * [apio drivers ftdi](#apio-drivers-ftdi) - Manage the ftdi drivers.
      * [apio drivers ftdi install](#apio-drivers-ftdi-install) - Install the ftdi drivers.
      * [apio drivers ftdi list](#apio-drivers-ftdi-list) - List the connected ftdi devices.
      * [apio drivers ftdi uninstall](#apio-drivers-ftdi-uninstall) - Uninstall the ftdi drivers.
    * [apio drivers lsusb](#apio-drivers-lsusb) - List connected USB devices.
    * [apio drivers serial](#apio-drivers-serial) - Manage the serial drivers.
      * [apio drivers serial install](#apio-drivers-serial-install) - Install the serial drivers.
      * [apio drivers serial list](#apio-drivers-serial-list) - List the connected serial devices.
      * [apio drivers serial uninstall](#apio-drivers-serial-uninstall) - Uninstall the serial drivers.
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
  * [apio raw](#apio-raw) - Execute commands directly from the Apio packages.
  * [apio report](#apio-report) - Report design utilization and timing.
  * [apio sim](#apio-sim) - Simulate a testbench with graphic results.
  * [apio system](#apio-system) - Provides system info.
    * [apio system info](#apio-system-info) - Show platform id and other info.
    * [apio system platforms](#apio-system-platforms) - List supported platforms ids.
  * [apio test](#apio-test) - Test all or a single verilog testbench module.
  * [apio upgrade](#apio-upgrade) - Check the latest Apio version.
  * [apio upload](#apio-upload) - Upload the bitstream to the FPGA.

<br>

### apio

```
Usage: apio [OPTIONS] COMMAND [ARGS]...

  Work with FPGAs with ease.

  Apio is a user friendly command-line suite that supports all the aspect of
  FPGA firmware developement from linting, building and simulating to unit
  testing, to progreamming the FPGA board.

  Apio commands are typically invoked in the root directory of the FPGA
  project where the project configuration file apio.ini and the project source
  files are stored. For help on specific commands use the -h flag (e.g. 'apio
  build -h').

  For more information on the apio project see
  https://github.com/FPGAwars/apio/wiki/Apio

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Build commands:
  apio build     Synthesize the bitstream.
  apio upload    Upload the bitstream to the FPGA.
  apio clean     Delete the apio generated files.

Verification commands:
  apio lint      Lint the verilog code.
  apio format    Format verilog source files.
  apio sim       Simulate a testbench with graphic results.
  apio test      Test all or a single verilog testbench module.
  apio report    Report design utilization and timing.
  apio graph     Generate a visual graph of the code.

Setup commands:
  apio create    Create an apio.ini project file.
  apio packages  Manage the apio packages.
  apio drivers   Manage the operating system drivers.

Utility commands:
  apio boards    List available board definitions.
  apio fpgas     List available FPGA definitions.
  apio examples  List and fetch apio examples.
  apio system    Provides system info.
  apio raw       Execute commands directly from the Apio packages.
  apio upgrade   Check the latest Apio version.

```

<br>

### apio boards

```
Usage: apio boards [OPTIONS]

  The boards commands lists the FPGA boards that are recongnized by apio.
  Custom boards can be defined by placing a custom boards.json file in the
  project directory. If such a case, the command lists the boards from that
  custom file.

  The commands is typically used in the root directory of the project that
  contains the apio.ini file.

  Examples:
    apio boards                # List all boards
    apio boards | grep ecp5    # Filter boards results
    apio boards --project-dir foo/bar  # Use a different

Options:
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio build

```
Usage: apio build [OPTIONS]

  The build command reads the project source files and generates a bitstream
  file that you can uploaded to your FPGA. The commands is typically used in
  the root directory of the project that contains the apio.ini file.

  Examples:
    apio build       # Build
    apio build -v    # Build with verbose info

  The build command builds all the .v files (e.g. my_module.v) in the project
  directory except for those whose name ends with _tb (e.g. my_module_tb.v) to
  indicate that they are testbenches.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -v, --verbose           Show detailed output.
  --verbose-yosys         Show detailed yosys output.
  --verbose-pnr           Show detailed pnr output.
  -h, --help              Show this message and exit.
```

<br>

### apio clean

```
Usage: apio clean [OPTIONS]

  The clean command deletes the temporary files that were generated in the
  project directory by previous apio commands. The commands is typically used
  in the root directory of the project that contains the apio.ini file.

  Example:
    apio clean

  [Hint] If you are using a git repository, add a .gitignore file with the
  temporary apio file names.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio create

```
Usage: apio create [OPTIONS]

  The 'apio create' command creates a new apio.ini project file and may be use
  when creating a new apio project.

  Examples:
    apio create --board icezum
    apio create --board icezum --top-module MyModule

  The flag --board is required. The flag --top-module is optional and has the
  default 'main'. If the file apio.ini already exists the command exists with
  an error message.

  [Note] this command creates just the 'apio.ini' file rather than a complete
  and buildable project. Some users use instead the'apio examples' command to
  copy a working project for their board, and then modify it with with their
  design.

Options:
  -b, --board board_id    Set the board.  [required]
  -t, --top-module name   Set the top level module name.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio drivers

```
Usage: apio drivers [OPTIONS] COMMAND [ARGS]...

  The 'apio drivers' commands group contains subcommands that are used to
  manage the drivers on your system.

  The subcommands are listed below.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers ftdi    Manage the ftdi drivers.
  apio drivers serial  Manage the serial drivers.
  apio drivers lsusb   List connected USB devices.

```

<br>

### apio drivers ftdi

```
Usage: apio drivers ftdi [OPTIONS] COMMAND [ARGS]...

  The 'apio drivers ftdi' commands group contains subcommands that are used to
  manage the ftdi drivers on your system.

  The subcommands are listed below.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers ftdi install    Install the ftdi drivers.
  apio drivers ftdi uninstall  Uninstall the ftdi drivers.
  apio drivers ftdi list       List the connected ftdi devices.

```

<br>

### apio drivers ftdi install

```
Usage: apio drivers ftdi install [OPTIONS]

  The command 'apio drivers ftdi install' installs the ftdi drivers on your
  system as required by some FPGA boards.

  Examples:
    apio drivers fdri install      # Install the ftdi drivers.
    apio drivers fdri uinstall     # Uinstall the ftdi drivers.

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio drivers ftdi list

```
Usage: apio drivers ftdi list [OPTIONS]

  The command 'apio drivers ftdi list' lists the ftdi devices connected to
  your computer. It is useful for diagnosing FPGA board connectivity issues.

  Examples:
    apio drivers ftdi list     # List the ftdi devices.

  [Hint] This command executes the utility `lsftdi` which can also be invoked
  using the command `apio raw -- lsftdi <flags>`

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio drivers ftdi uninstall

```
Usage: apio drivers ftdi uninstall [OPTIONS]

  The command 'apio drivers ftdi uninstall' uninstalled the ftdi drivers that
  you may installed eariler. .

  Examples:
    apio drivers ftdi install      # Install the ftdi drivers.
    apio drivers ftdi uinstall     # Uinstall the ftdi drivers.

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio drivers lsusb

```
Usage: apio drivers lsusb [OPTIONS]

  The 'apio drivers lsusb' commands runs the lsusb utility to list the usb
  devices connected to your computer.  It is typically used  for diagnosing
  connectivity issues with FPGA boards.

  Examples:
    apio drivers lsusb      # List the usb devices

  [Hint] You can also run the lsusb utility using the command 'apio raw --
  lsusb <flags>'

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio drivers serial

```
Usage: apio drivers serial [OPTIONS] COMMAND [ARGS]...

  The 'apio drivers serial' commands group contains subcommands that are used
  to manage the serial drivers on your system.

  The subcommands are listed below.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio drivers serial install    Install the serial drivers.
  apio drivers serial uninstall  Uninstall the serial drivers.
  apio drivers serial list       List the connected serial devices.

```

<br>

### apio drivers serial install

```
Usage: apio drivers serial install [OPTIONS]

  The command 'apio drivers serial install' installs the serial drivers on
  your system as required by some FPGA boards.

  Examples:
    apio drivers serial install      # Install the ftdi drivers.
    apio drivers serial uinstall     # Uinstall the ftdi drivers.

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio drivers serial list

```
Usage: apio drivers serial list [OPTIONS]

  The command 'apio drivers serial list' lists the serial devices connected to
  your computer. It is useful for diagnosing FPGA board connectivity issues.

  Examples:
    apio drivers serial list     # List the serial devices.

  [Hint] This command executes the utility `lsserial` which can also be
  invoked using the command `apio raw -- lsserial <flags>`

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio drivers serial uninstall

```
Usage: apio drivers serial uninstall [OPTIONS]

  The command 'apio drivers serial uninstall' uninstalled the serial drivers
  that you may installed eariler. .

  Examples:
    apio drivers serial install      # Install the serial drivers.
    apio drivers serial uinstall     # Uinstall the serial drivers.

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio examples

```
Usage: apio examples [OPTIONS] COMMAND [ARGS]...

  The 'apio examples' group provides subcommands for listing and fetching apio
  provided examples, each is a self contain mini project that can be built and
  uploaded to a FPGA.

  The subcommands are listed below.

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

  The 'apio examples fetch' command fetchs the files of the specified example
  to the current directory rot to the directory specified by the --dst option.
  The destination directory does not have to exist but if it does it must be
  empty.

  Examples:
    apio examples fetch alhambra-ii/ledon
    apio examples fetch alhambra-ii/ledon -d foo/bar

  For a list of available examples type 'apio examples list'.

Options:
  -d, --dst path  Set a different destination directory.
  -h, --help      Show this message and exit.
```

<br>

### apio examples fetch-board

```
Usage: apio examples fetch-board [OPTIONS] BOARD

  The 'apio examples fetch-board` is used to fetch all the apio examples of a
  given board. The examples are copied under the current directory or the
  destination directory if --dst is given.

  Examples:
    apio examples fetch-board alhambra-ii             # Fetch to local directory
    apio examples fetch-board alhambra-ii -d foo/bar  # Fetch to foo/bar

Options:
  -d, --dst path  Set a different destination directory.
  -h, --help      Show this message and exit.
```

<br>

### apio examples list

```
Usage: apio examples list [OPTIONS]

  The 'apio examples list' lists the apio project examples that are available
  for fetching.

  Examples:
    apio examples list                     # List all examples
    apio examples list | grep alhambra-ii  # Show examples of a specific board.
    apio examples list | grep -i blink     # Show all blinking examples.



Options:
  -h, --help  Show this message and exit.
```

<br>

### apio format

```
Usage: apio format [OPTIONS] [FILES]...

  The format command formats verilog source files for consistency and style
  but without changing their semantic.  The command accepts the names of the
  source files to format or formats all the project source files by default.
  The commands is typically used in the root directory of the project that
  contains the apio.ini file.

  Examples:
    apio format                    # Format all source files.
    apio format -v                 # Same as above but with verbose output.
    apio format main.v main_tb.v   # Format the two tiven files.

  The format command uses the format tool of the Verible project which can be
  configured by setting its flags in the apio.ini project file. For example:

  format-verible-options =
      --column_limit=80
      --indentation_spaces=4

  If you want to protect a group of source code lines from formatting, you can
  use the following verible formatter's directives:

  // verilog_format: off
  ... untouched code ...
  // verilog_format: on

  For the ull list of the verible formatter flags, see its documentation page
  online or type 'apio raw -- verible-verilog-format --helpfull'.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.
```

<br>

### apio fpgas

```
Usage: apio fpgas [OPTIONS]

  The fpgas commands lists the FPGA that are recongnized by apio. Custom FPGAS
  that are supported by the underlying Yosys tools chain can be defined by
  placing a custom fpgas.json file in the project directory. If such a case,
  the command lists the fpgas from that custom file. The commands is typically
  used in the root directory of the project that contains the apio.ini file.

  Examples:
    apio fpgas               # List all fpgas
    apio fpgas | grep gowin  # Filter FPGA results.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio graph

```
Usage: apio graph [OPTIONS]

  The graph command generates a graphical representation of the verilog code
  of the project. The commands is typically used in the root directory of the
  project that contains the apio.ini file.

  Examples:
    apio graph               # Generate a svg file.
    apio graph --pdf         # Generate a pdf file.
    apio graph --png         # Generate a png file.
    apio graph -t my_module  # Graph my_module module.

Options:
  --pdf                   Generate a pdf file.
  --png                   Generate a png file.
  -p, --project-dir path  Set the root directory for the project.
  -t, --top-module name   Set the name of the top module to graph.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.

  [Hint] On windows, type 'explorer _build/hardware.svg' to view the graph,
  and on Mac OS type 'open _build/hardware.svg'.
```

<br>

### apio lint

```
Usage: apio lint [OPTIONS]

  The lint command scans the project's verilog code and flags errors,
  inconsistencies, and style violations, and is a useful tool for improving
  the code quality. The command uses the verilator tool which is installed as
  park of the apio installation. The commands is typically used in the root
  directory of the project that contains the apio.ini file.

  Examples:
    apio lint
    apio lint -t my_module
    apio lint --all

Options:
  -t, --top-module name   Restrict linting to this module and its depedencies.
  -a, --all               Enable all warnings, including code style warnings.
  --nostyle               Disable all style warnings.
  --nowarn nowarn         Disable specific warning(s).
  --warn warn             Enable specific warning(s).
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio packages

```
Usage: apio packages [OPTIONS] COMMAND [ARGS]...

  The 'apio packages' command groups provides commands to manage the the
  instllation of the apio packages These are not python packages but apio
  specific packages that contain various tools and data that are necessary for
  the operation of apio. These packages are installed after the installation
  of the apio python package using the command 'apio packages install'. Note
  that the list of available packages depends on the operatingsystem you use
  as some require more packages than others.

  The subcommands are listed below.

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

  The 'apio packages fix' command fixes partially installed or left over apio
  packages that are shown by the command 'apio packages list' as broken. If
  there are no broken packages, the program does nothing and exits.

  Examples:
    apio packages fix           # Fix package errors.
    apio packages fix  -v       # Same but with verbose output.

Options:
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.
```

<br>

### apio packages install

```
Usage: apio packages install [OPTIONS] [PACKAGES]...

  The command 'apio packages install' installs apio packages which are require
  for the operation of apio on your system.

  Examples:
    apio packages install                   # Install all missing packages.
    apio packages install --force           # Re/install all missing packages.
    apio packages install oss-cad-suite     # Install just this package.
    apio packages install examples@0.0.32   # Install a specific version.

  Adding the option --force to forces the reinstallation of existing packages,
  otherwise, packages that are already installed correctly are left with no
  change.

Options:
  -f, --force    Force installation.
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.
```

<br>

### apio packages list

```
Usage: apio packages list [OPTIONS]

  The 'apio packages list' command lists the available and installed apio
  packages. Note that the list of available packages depends on the
  operatingsystem you use as some require more packages than others.

  Examples:
    apio packages list

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio packages uninstall

```
Usage: apio packages uninstall [OPTIONS] [PACKAGES]...

  The command 'apio packages uninstall' installs apio packages from your
  system.

  Examples:
    apio packages uninstall                 # Uninstall all packages.
    apio packages uninstall --sayyes        # Same but does not ask yes/no.
    apio packages uninstall oss-cad-suite   # Uninstall only given package(s).

Options:
  -y, --sayyes   Automatically answer YES to all the questions.
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.
```

<br>

### apio raw

```
Usage: apio raw [OPTIONS] COMMAND

  The raw command allows to bypass  apio and run underlying tools directly.
  This is an advanced command that requires familiarity with the underlying
  tools.

  Before running the command, apio changes temporarly system env vars such as
  $PATH to provide access to its packages. To view those env changes, run
  `apio raw --env'.

  Examples:
    apio raw -- yosys --version           # Yosys version
    apio raw -v -- yosys --version        # Same but with verbose apio info.
    apio raw -- yosys                     # Run Yosys in interactive mode.
    apio raw -- icepll -i 12 -o 30        # Calc ICE PLL
    apio raw --env                        # Show apio env setting.
    apio raw -h                           # Print this help info.

  The '--' token is used  to seperate between apio commands and its argument
  and the executed command and its arguments. It can be ommited in some cases
  but it's a good paractice to always use it. As a rule of thumb, prepend the
  command you want to run with 'apio raw -- ' and it should work.

Options:
  -e, --env      Show the apio env changes.
  -v, --verbose  Show detailed output.
  -h, --help     Show this message and exit.
```

<br>

### apio report

```
Usage: apio report [OPTIONS]

  The report command reports the utilization and timing of the design. It is
  useful to analyzer utilization bottle neck and to verify that the design can
  run at a desired clock speed. The commands is typically used in the root
  directory of the project that contains the apio.ini file.

  Examples:
    apio report
    epio report --verbose

Options:
  -p, --project-dir path  Set the root directory for the project.
  -v, --verbose           Show detailed output.
  -h, --help              Show this message and exit.
```

<br>

### apio sim

```
Usage: apio sim [OPTIONS] TESTBENCH

  The sim command simulates a testbench file and shows the simulation results
  a GTKWave graphical window. The testbench is expected to have a name ending
  with _tb (e.g. my_module_tb.v) and the commands is typically used in the
  root directory of the project that contains the apio.ini file and it accepts
  the testbench file name as an argument. For example:

  Example:
    apio sim my_module_tb.v
    apio sim my_module_tb.v --force

  It is recommanded NOT to use the `$dumpfile()` function in your testbenchs
  as this may override the default name and location of the generated .vcd
  file.

  The sim command defines the INTERACTIVE_SIM that can be used in the
  testbench to distinguise between 'apio test' and 'apio sim', for example to
  ignore error with 'apio sim' and view the erronous signals gtkwave. For a
  sample testbench that uses those macro see the example at
  https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

  [Hint] when you configure the signals in GTKWave, you can save the
  configuration for future invocations.

Options:
  -f, --force             Force simulation.
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio system

```
Usage: apio system [OPTIONS] COMMAND [ARGS]...

  The command group 'apio system' contains subcommans that provides
  information about the system and apio's installation.

  The subcommands are listed below.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio system platforms  List supported platforms ids.
  apio system info       Show platform id and other info.

```

<br>

### apio system info

```
Usage: apio system info [OPTIONS]

  The 'apio system info' command provides general informaion about your system
  and apio installation and is useful for diagnosing apio installation issues.

  Examples:
    apio system info       # Show platform id and info.

  [Advanced] The default location of the apio home directory, where
  preferences and packages are stored, is in the .apio directory under the
  user home directory, but can be changed using the APIO_HOME environment
  variable.

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio system platforms

```
Usage: apio system platforms [OPTIONS]

  The 'apio system platforms' command lists the platforms ids supported by
  apio, with the effective platform id of your system highlightd.

  Examples:
    apio system platforms   # List supported platform ids.

  [Advanced] The automatic platform id detection of apio can be overriden by
  defining a different platform id using the env variable APIO_PLATFORM.

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio test

```
Usage: apio test [OPTIONS] [TESTBENCH_FILE]

  The sim command simulates one or all the testbenches in the project and is
  useful for automatic unit testing of the code. Testbenches are expected have
  a name ending with _tb (e.g my_module_tb.v) and to exit with the $fatal
  directive if any error is detected. The commands is typically used in the
  root directory of the project that contains the apio.ini.

  Examples
    apio test                 # Run all *_tb.v testbenches.
    apio test my_module_tb.v  # Run a single testbench

  It is recommanded NOT to use the `$dumpfile()` function in your testbenchs
  as this may override the default name and location of the generated .vcd
  file.

  For a sample testbench that is compatible with apio see the example at
  https://github.com/FPGAwars/apio-examples/tree/master/upduino31/testbench

  [Hint] To simulate the testbench with a graphical visualizaiton of the
  signals see the 'apio sim' command.

Options:
  -p, --project-dir path  Set the root directory for the project.
  -h, --help              Show this message and exit.
```

<br>

### apio upgrade

```
Usage: apio upgrade [OPTIONS]

  The upgrade command checks the version of the latest apio release and
  provide upgrade directions if needed.

  Examples:
    apio upgrade

Options:
  -h, --help  Show this message and exit.
```

<br>

### apio upload

```
Usage: apio upload [OPTIONS]

  The uploade command builds the bitstream file (similar to the build command)
  and uploaded it to the FPGA board. The commands is typically used in the
  root directory of the project that contains the apio.ini file.

  Examples:
    apio upload

Options:
  --serial-port serial-port  Set the serial port.
  --ftdi-id ftdi-id          Set the FTDI id.
  -s, --sram                 Perform SRAM programming.
  -f, --flash                Perform FLASH programming.
  -v, --verbose              Show detailed output.
  --verbose-yosys            Show detailed yosys output.
  --verbose-pnr              Show detailed pnr output.
  -p, --project-dir path     Set the root directory for the project.
  -h, --help                 Show this message and exit.
```
