## FAQ

### What is Apio?

Apio is an open source ecosystem for open FPGA boards. It was inspired by [PlatformIO](https://github.com/platformio/platformio).

Apio (pronounced [ˈa.pjo]) is a multiplatform toolbox, with static pre-built packages, project configuration tools and easy command interface to verify, synthesize, simulate and upload your verilog designs.

Apio is a command line interface (CLI) made for open FPGA developers. It is also a flexible project, ready to be adapted to new experimental toolchains, boards and cores. It contains some extra utilities like cross-platform lsusb and lsftdi, examples, drivers configuration, etc.

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

### Differences between Apio and PlatformIO

Apio is a micro-ecosystem focused only on *open FPGAs* while PlatformIO is an ecosystem focused on *embedded platforms and microcontrollers*. Apio has also a different API from PlatformIO.

Apio contains direct commands to verify, simulate, analyze, build, upload *verilog code*. It also contains system utilities, drivers configuration, generic examples, package management and board detection.

```
$ apio
Usage: apio [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Project commands:
  build      Synthesize the bitstream.
  clean      Clean the previous generated files.
  lint       Lint the verilog code.
  sim        Launch the verilog simulation.
  time       Bitstream timing analysis.
  upload     Upload the bitstream to the FPGA.
  verify     Verify the verilog code.

Setup commands:
  drivers    Manage FPGA boards drivers.
  init       Manage apio projects.
  install    Install packages.
  uninstall  Uninstall packages.

Utility commands:
  boards     Manage FPGA boards.
  config     Apio configuration.
  examples   Manage verilog examples.
  raw        Execute commands using Apio packages.
  system     System tools.
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

### Does Apio have graphical front-ends?

Yes. Apio IDE and Icestudio.

* **[Apio-IDE](https://github.com/FPGAwars/apio-ide)** is an IDE that integrates Atom and Apio.

 <img src="https://github.com/FPGAwars/apio-ide/raw/master/doc/apio-ide-screenshot-1.png" width="600">

* **[Icestudio](https://github.com/FPGAwars/icestudio)** is a visual editor for open FPGA boards built with web technologies.

 <img src="https://github.com/FPGAwars/icestudio/raw/develop/docs/resources/images/demo/main.png" width="600">

 [apio-pio]: docs/resources/images/apio-pio-min.png
 [apio-pio-development]: docs/resources/images/apio-pio-development-min.png
