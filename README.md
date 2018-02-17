![][apio-logo]

[![Build Status](https://travis-ci.org/FPGAwars/apio.svg?branch=develop)](https://travis-ci.org/FPGAwars/apio)
[![Latest Version](https://img.shields.io/pypi/v/apio.svg)](https://pypi.python.org/pypi/apio/)
[![License](http://img.shields.io/:license-gpl-blue.svg)](http://opensource.org/licenses/GPL-2.0)
[![Documentation Status](https://readthedocs.org/projects/apiodoc/badge/?version=latest)](http://apiodoc.readthedocs.io/en/latest/)

![][linux-logo]
&nbsp;
![][macosx-logo]
&nbsp;
![][windows-logo]
&nbsp;
![][ubuntu-logo]
&nbsp;
![][raspbian-logo]

Experimental open source micro-ecosystem for **open FPGAs**. Based on [platformio](https://github.com/platformio/platformio). Apio is a **multiplatform toolbox**, with static pre-built packages, project configuration tools and easy commands to verify, synthesize, simulate and upload your **verilog** designs.

Apio is used by [Icestudio](https://github.com/FPGAwars/icestudio).

### Table of contents
* [Installation](#installation)
* [Apio packages](#apio-packages)
* [Supported boards](#supported-boards)
* [Documentation](#documentation)
* [Development](#development)
* [FAQ](#faq)
* [Videos](#videos)
* [Authors](#authors)
* [Contributors](#contributors)
* [License](#license)

## Installation

1. Install [Python](https://www.python.org/downloads) and [pip](https://pip.pypa.io)

2. Install the latest apio: ```pip install -U apio```

## Apio packages

| Package | Installation   | Description
|---------|----------------|---------------
| [drivers](https://github.com/FPGAwars/tools-drivers)  | apio install drivers | Drivers tools (only for Windows)
| [examples](https://github.com/FPGAwars/apio-examples)  | apio install examples | Verilog basic examples, pinouts, etc
| [gtkwave](https://github.com/FPGAwars/tool-gtkwave)  | apio install gtkwave | Simulation viewer. [GTKWave project](http://gtkwave.sourceforge.net) (only for Windows)
| [icestorm](https://github.com/FPGAwars/toolchain-icestorm)  | apio install icestorm | iCE40 FPGA synthesis, place & route and configuration tools. [Icestorm project](http://www.clifford.at/icestorm)
| [iverilog](https://github.com/FPGAwars/toolchain-iverilog)  | apio install iverilog | Verilog simulation and synthesis tool. [Icarus Verilog project](http://iverilog.icarus.com)
| [system](https://github.com/FPGAwars/tools-system)  | apio install system | Tools for listing the USB devices and retrieving information from the FTDI chips

**Supported platforms**

*linux_x86_64, linux_i686, linux_armv7l, linux_aarch64, windows_x86, windows_amd64, darwin*.

## Supported boards

| Board name | GNU/Linux | Windows | Mac OS |
|:-|:-:|:-:|:-:|
| [IceZUM Alhambra](https://github.com/FPGAwars/icezum) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [Kéfir I iCE40-HX4K](http://fpgalibre.sourceforge.net/Kefir/) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [Nandland Go board](https://www.nandland.com/goboard/introduction.html) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [iCE40-HX8K Breakout Board](http://www.latticesemi.com/Products/DevelopmentBoardsAndKits/iCE40HX8KBreakoutBoard) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [iCEstick Evaluation Kit](http://www.latticesemi.com/icestick) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [icoBOARD 1.0](http://icoboard.org/about-icoboard.html) |  &nbsp;&nbsp;:white_check_mark:&nbsp;**\*** | - |  - |
| [CAT Board](https://hackaday.io/project/7982-cat-board) | &nbsp;&nbsp;:white_check_mark:&nbsp;**\*** | - |  - |
| [BlackIce](https://hackaday.io/project/12930-blackice-low-cost-open-hardware-fpga-dev-board) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [BlackIce II](https://github.com/mystorm-org/BlackIce-II) | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [TinyFPGA B2](http://tinyfpga.com/b-series-guide.html) | :white_check_mark: | :white_check_mark: | :white_check_mark: |

**\*** Use with Raspberry Pi

NOTE: all supported [Icestorm FPGAs](http://www.clifford.at/icestorm/) can be used with [--fpga or --size, --type and --pack options](http://apiodoc.readthedocs.io/en/develop/source/user_guide/code_commands/cmd_build.html#options).

## Documentation

The project full documentation is located in Read the Docs: http://apiodoc.readthedocs.io


## Development

```bash
git clone https://github.com/FPGAwars/apio.git
cd apio
```

### Testing

```bash
pip install tox
```

```bash
tox
```

```bash
tox -e offline
tox -e coverage
```

### Debian packaging

Also you can find the debian scripts to package the full application and all the packages here: https://github.com/set-soft/apio-debian.

Thanks Salvador E. Tropea!

## FAQ

### What is Apio?

Apio is an experimental micro-ecosystem for open FPGAs. Based on [platformio](https://github.com/platformio/platformio). Apio is a multiplatform toolbox, with static pre-built packages, project configuration tools and easy commands to verify, synthesize, simulate and upload your verilog designs.

Apio is a command line interface (CLI) made for open FPGA developers. It is also a flexible project, ready to be adapted to new experimental toolchains, boards and cores. It contains some extra utilities like cross-platform lsusb and lsftdi, examples, drivers' configuration, etc.

**Apio evolves with the growing open FPGA movement. It must be flexible, adaptative and hackable**

### Why did Apio appear?

Apio appeared as a need to unify and simplify the use of the main open source tools for open FPGAs [Icestorm](http://www.clifford.at/icestorm/) and [Icarus Verilog](http://iverilog.icarus.com/). This became very useful for the *verilog* developers as a CLI and for projects like [Icestudio](https://github.com/FPGAwars/icestudio) as a back-end.

We want to spread the open FPGA knowledge and tools to everyone (eg: [verilog tutorial](https://github.com/Obijuan/open-fpga-verilog-tutorial/wiki)). Simplifying the setup time would help to focus on the content, improve workshops performances, etc. In short, reduce the entry barrier to new users.

There were some drawbacks that we wanted to solve:

* Very long configuration time
* Compile the toolchains for each OS
* Multiple commands with low level parameters
* Different behavior in Linux, Windows and Mac

Then, we started building [lsusb](https://github.com/FPGAwars/libusb-cross-builder), [lsftdi](https://github.com/FPGAwars/libftdi-cross-builder) and [icestorm](https://github.com/FPGAwars/toolchain-icestorm) static pre-built packages for Linux (x86_64, i386, armv7l, aarch64), Windows and Mac OS, and learning about these *amazing emerging tools*.

The first integration step was to add FPGA tools in the [PlatformIO](https://github.com/platformio/platformio) project ([Platforio-FPGA](https://github.com/FPGAwars/Platformio-FPGA)), which has been always used for classic microcontroller ecosystems. But the slow integration and the lack of flexibility encouraged us to create a custom *fork* of PlatformIO (pio) called Apio to speed up our investigation and experiments with open FPGAs.

Note: also a [pio-fpga](https://github.com/FPGAwars/Platformio-FPGA/releases/tag/v0.1) Apio package was created to configure FPGA tools in PlatformIO through Apio in the early times.

Very interesting ideas like a nice Python click interface, a SCons build system and a user-level package installation were included in the project.

### What about PlatformIO Lattice FPGA support?

PlatformIO Lattice FPGA support was added in the [2.9.0](https://github.com/platformio/platformio/releases/tag/v2.9.0) release. An issue was created with a very primitive and experimental support of [iCEstick](http://www.pighixxx.com/test/portfolio-items/icestick/) and [Icezum](https://github.com/FPGAwars/icezum) boards ([#480](https://github.com/platformio/platformio/issues/480)).

It was an initial attempt to try to fit the new open FPGA project concept into a classic microcontroller ecosystem.

In Platformio 3.0 a more flexible contribution method was implemented. Then, more contributions were made to support [platform-lattice_iCE40](https://github.com/platformio/platform-lattice_ice40) using the work and knowledge generated in the Apio project.

![][apio-pio-development]

### Differences between Apio and PlatformIO?

Apio is a micro-ecosystem focused only on *open FPGAs* while PlatformIO is an ecosystem focused on *embedded platforms and microcontrollers*. Apio has also a different API from PlatformIO.

Apio contains direct commands to verify, simulate, analyze, build, upload *verilog code*. It also contains system utilities, drivers configuration, generic examples, package management and board detection.

```
$ apio
Usage: apio [OPTIONS] COMMAND [ARGS]...

  Experimental micro-ecosystem for open FPGAs

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Code commands:
  build      Synthesize the bitstream.
  clean      Clean the previous generated files.
  sim        Launch the verilog simulation.
  time       Bitstream timing analysis.
  upload     Upload the bitstream to the FPGA.
  verify     Verify the verilog code.

Environment commands:
  boards     Manage FPGA boards.
  config     Apio configuration.
  drivers    Manage FPGA drivers.
  examples   Manage verilog examples.
  init       Manage apio projects.
  install    Install packages.
  system     System tools.
  uninstall  Uninstall packages.
  upgrade    Check the latest Apio version.
```

PlatformIO is a bigger ecosystem than Apio. It integrates a lot of platforms, frameworks, boards and libraries for current *IoT development*. It also contains continuous integration, library examples, serial utilities and project testing.

```
$ pio
Usage: pio [OPTIONS] COMMAND [ARGS]...

Options:
  --version          Show the version and exit.
  -f, --force        Force to accept any confirmation prompts.
  -c, --caller TEXT  Caller ID (service).
  -h, --help         Show this message and exit.

Commands:
  boards    Pre-configured Embedded Boards
  ci        Continuous Integration
  device    Monitor device or list existing
  init      Initialize PlatformIO project or update existing
  lib       Library Manager
  platform  Platform Manager
  run       Process project environments
  settings  Manage PlatformIO settings
  test      Unit Testing
  update    Update installed Platforms, Packages and Libraries
  upgrade   Upgrade PlatformIO to the latest version
```

### Future development

![][apio-pio]

Apio will continue growing with new packages, commands, boards and more, improving from the community knowledge and contributions, and satisfying our FPGA needs.

PlatformIO may also increase its FPGA support using all the knowledge generated in the Apio project and the contribution of the community.

### Has Apio graphic front-ends?

Yes.

* **[Apio-IDE](https://github.com/FPGAwars/apio-ide)**: is an experimental IDE that integrates Atom and Apio.

 <img src="https://github.com/FPGAwars/apio-ide/raw/master/doc/apio-ide-screenshot-1.png" width="600">

* **[Icestudio](https://github.com/FPGAwars/icestudio)**: is an experimental visual hardware editor built with web technologies.

 <img src="https://github.com/FPGAwars/icestudio/raw/develop/doc/images/main.png" width="600">

## Videos

[![Apio in RPI2: iCEstick, Icezum and icoBOARD ](http://img.youtube.com/vi/xLb7T4pw9iY/0.jpg)](https://www.youtube.com/watch?v=xLb7T4pw9iY "Apio in RPI2: iCEstick, Icezum and icoBOARD ")

[![Apio: an easy multi-platform toolbox for open FPGAs](http://img.youtube.com/vi/UJ6-_42P5BE/0.jpg)](https://www.youtube.com/watch?v=UJ6-_42P5BE "Apio: an easy multi-platform toolbox for open FPGAs")

## Authors

* [Jesús Arroyo Torrens](https://github.com/Jesus89)
* [Juan González (Obijuan)](https://github.com/Obijuan)

## Contributors

* [Salvador E. Tropea](https://github.com/set-soft)
* [Miguel Sánchez de León Peque](https://github.com/peque)
* [devbisme](https://github.com/devbisme)

## Credits

* [BQ](https://www.bq.com) sponsored this project from 02/2016 to 11/2016. Thanks

  <img src="https://github.com/FPGAwars/icezum/raw/master/wiki/bq-logo.png" width="80">

## License

Licensed under [GPL 2.0](http://opensource.org/licenses/GPL-2.0) and [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

[apio-logo]: docs/resources/images/apio-logo-mini.png
[linux-logo]: docs/resources/images/linux.png
[macosx-logo]: docs/resources/images/macosx.png
[windows-logo]: docs/resources/images/windows.png
[ubuntu-logo]: docs/resources/images/ubuntu.png
[raspbian-logo]: docs/resources/images/raspbian.png
[apio-pio]: docs/resources/images/apio-pio-min.png
[apio-pio-development]: docs/resources/images/apio-pio-development-min.png
