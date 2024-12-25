
<br><br>

### APIO

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

<br><br>

### APIO BOARDS

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

<br><br>

### APIO BUILD

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

<br><br>

### APIO CLEAN

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

<br><br>

### APIO CREATE

```
Usage: apio create [OPTIONS]

  The create command creates the project file apio.ini from scratch. The
  commands is typically used in the root directory of the project where the
  apio.ini file is created.

  Examples:
    apio create --board icezum
    apio create --board icezum --top-module MyModule
    apio create --board icezum --sayyes

  The flag --board is required. The flag --top-module is optional and has the
  default 'main'. If the file apio.ini already exists the command asks for
  permision to delete it. If --sayyes is specified, the file is deleted
  automatically.

  [Note] this command creates just the 'apio.ini' file rather than a full
  buildable project. Some users use instead the examples command to copy a
  working project for their board, and then modify it with with their design.

  [Hint] Use the command 'apio examples -l' to see a list of the supported
  boards.

Options:
  -b, --board board_id    Set the board.  [required]
  -t, --top-module name   Set the top level module name.
  -p, --project-dir path  Set the root directory for the project.
  -y, --sayyes            Automatically answer YES to all the questions.
  -h, --help              Show this message and exit.
```

<br><br>

### APIO DRIVERS

```
Usage: apio drivers [OPTIONS]

  The drivers command allows to install or uninstall operating system drivers
  that are used to program the FPGA boards. This command is global and affects
  all the projects on the local host.

  Examples:
    apio drivers --ftdi-install      # Install the FTDI driver.
    apio drivers --ftdi-uninstall    # Uninstall the FTDI driver.
    apio drivers --serial-install    # Install the serial driver.
    apio drivers --serial-uninstall  # Uninstall the serial driver.

    Do not specify more than flag per command invocation.

Options:
  --ftdi-install      Install the FTDI driver.
  --ftdi-uninstall    Uninstall the FTDI driver.
  --serial-install    Install the Serial driver.
  --serial-uninstall  Uninstall the Serial driver.
  -h, --help          Show this message and exit.
```

<br><br>

### APIO EXAMPLES

```
Usage: apio examples [OPTIONS]

  The examples command allows to list the project examples provided by api and
  to copy them to a local directory. Each examples is identified by board/name
  where board is the board id and name is the example name.

  Examples:
    apio examples --list               # List all examples
    apio examples -l | grep -i icezum  # Filter examples.
    apio examples -f icezum/leds       # Fetch example files
    apio examples -d icezum/leds       # Fetch example directory
    apio examples -d icezum            # Fetch all board examples

Options:
  -l, --list              List all available examples.
  -d, --fetch-dir name    Fetch the selected example directory.
  -f, --fetch-files name  Fetch the selected example files.
  -p, --project-dir path  Set the root directory for the project.
  -n, --sayno             Automatically answer NO to all the questions.
  -h, --help              Show this message and exit.

  The format of 'name' is <board>[/<example>], where <board> is a board name
  (e.g. 'icezum') and <example> is a name of an example of that board (e.g.
  'leds').
```

<br><br>

### APIO FORMAT

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

<br><br>

### APIO FPGAS

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

<br><br>

### APIO GRAPH

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

  [Hint] On windows, type 'explorer hardware.svg' to view the graph, and on
  Mac OS type 'open hardware.svg'.
```

<br><br>

### APIO LINT

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

<br><br>

### APIO PACKAGES

```
Usage: apio packages [OPTIONS] COMMAND [ARGS]...

  The 'apio packages' command groups provides commands to manage the the
  instllation of the apio packages These are not python packages but apio
  specific packages that contain various tools and data that are necessary for
  the operation of apio. These packages are installed after the installation
  of the apio python package using the command 'apio packages install'. Note
  that the list of available packages depends on the operatingsystem you use
  as some require more packages than others.

  The subcommands of this group are listed below.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio packages install    Install apio packages.
  apio packages uninstall  Uninstall apio packages.
  apio packages list       List apio packages.
  apio packages fix        Fix broken apio packages.

```

<br><br>

### APIO PACKAGES FIX

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

<br><br>

### APIO PACKAGES INSTALL

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

<br><br>

### APIO PACKAGES LIST

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

<br><br>

### APIO PACKAGES UNINSTALL

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

<br><br>

### APIO RAW

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

<br><br>

### APIO REPORT

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

<br><br>

### APIO SIM

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

<br><br>

### APIO SYSTEM

```
Usage: apio system [OPTIONS] COMMAND [ARGS]...

  The 'apio system' command group provides various commands that provides
  information about the system, including devices and python and apio
  installation.

  The subcommands of this group are listed below.

Options:
  -h, --help  Show this message and exit.

Subcommands:
  apio system lsftdi     List connected FTDI devices.
  apio system lsusb      List connected USB devices.
  apio system lsserial   List connected serial devices.
  apio system platforms  List supported platforms ids.
  apio system info       Show platform id and other info.

```

<br><br>

### APIO SYSTEM INFO

```
Usage: apio system info [OPTIONS]

  The 'apio system lsftdi' commands runs the lsftdi utility to list ftdi
  devices connector to your computer and is useful for diagnosing connectivity
  issues with FPGA boards.

  Examples:
    apio system  lsftdi      # List FTDI devices

  [Hint] Another way to run the lsftd utility is using the command 'apio raw
  -- lsftdi <flags>'

Options:
  -h, --help  Show this message and exit.
```

<br><br>

### APIO SYSTEM LSFTDI

```
Usage: apio system lsftdi [OPTIONS]

  The 'apio system lsftdi' commands runs the lsftdi utility to list ftdi
  devices connector to your computer and is useful for diagnosing connectivity
  issues with FPGA boards.

  Examples:
    apio system  lsftdi      # List FTDI devices

  [Hint] Another way to run the lsftd utility is using the command 'apio raw
  -- lsftdi <flags>'

Options:
  -h, --help  Show this message and exit.
```

<br><br>

### APIO SYSTEM LSSERIAL

```
Usage: apio system lsserial [OPTIONS]

  The system command provides system info that help diagnosing apio
  installation and connectivity issue.

  Examples:
    apio system lsserial   # List serial devices

Options:
  -h, --help  Show this message and exit.
```

<br><br>

### APIO SYSTEM LSUSB

```
Usage: apio system lsusb [OPTIONS]

  The 'apio system lsftdi' commands runs the lsftdi utility to list ftdi
  devices connector to your computer and is useful for diagnosing connectivity
  issues with FPGA boards.

  Examples:
    apio system  lsftdi      # List FTDI devices

  [Hint] Another way to run the lsftd utility is using the command 'apio raw
  -- lsftdi <flags>'

Options:
  -h, --help  Show this message and exit.
```

<br><br>

### APIO SYSTEM PLATFORMS

```
Usage: apio system platforms [OPTIONS]

  The 'apio system lsftdi' commands runs the lsftdi utility to list ftdi
  devices connector to your computer and is useful for diagnosing connectivity
  issues with FPGA boards.

  Examples:
    apio system  lsftdi      # List FTDI devices

  [Hint] Another way to run the lsftd utility is using the command 'apio raw
  -- lsftdi <flags>'

Options:
  -h, --help  Show this message and exit.
```

<br><br>

### APIO TEST

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

<br><br>

### APIO UPGRADE

```
Usage: apio upgrade [OPTIONS]

  The upgrade command checks the version of the latest apio release and
  provide upgrade directions if needed.

  Examples:
    apio upgrade

Options:
  -h, --help  Show this message and exit.
```

<br><br>

### APIO UPLOAD

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
