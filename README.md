![][apio-logo]

[![Build Status](https://travis-ci.org/FPGAwars/apio.svg?branch=master)](https://travis-ci.org/FPGAwars/apio)
[![Latest Version](https://img.shields.io/pypi/v/apio.svg)](https://pypi.python.org/pypi/apio/)
[![License](http://img.shields.io/:license-gpl-blue.svg)](http://opensource.org/licenses/GPL-2.0)
[![Documentation Status](https://readthedocs.org/projects/apiodoc/badge/?version=stable)](http://apiodoc.readthedocs.io/en/stable/)

![][linux-logo]
&nbsp;
![][macosx-logo]
&nbsp;
![][windows-logo]
&nbsp;
![][ubuntu-logo]
&nbsp;
![][raspbian-logo]

Open source **ecosystem for open FPGA boards**

Apio (pronounced [ˈa.pjo]) is a **multiplatform toolbox**, with static pre-built packages, project configuration tools and easy command interface to verify, synthesize, simulate and upload your **verilog** designs.

Apio is used by [Icestudio](https://github.com/FPGAwars/icestudio).

### Table of contents
* [Installation](#installation)
* [Apio packages](#apio-packages)
* [Supported boards](#supported-boards)
* [Documentation](#documentation)
* [Development](#development)
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
| [drivers](https://github.com/FPGAwars/tools-drivers) | apio install drivers | Drivers tools (only for Windows)
| [examples](https://github.com/FPGAwars/apio-examples) | apio install examples | Verilog basic examples, pinouts, etc
| [gtkwave](https://github.com/FPGAwars/tool-gtkwave) | apio install gtkwave | Simulation viewer. [GTKWave project](http://gtkwave.sourceforge.net) (only for Windows)
| [yosys](https://github.com/FPGAwars/toolchain-yosys) | apio install yosys | FPGA synthesis. [Yosys project](http://www.clifford.at/yosys)
| [ice40](https://github.com/FPGAwars/toolchain-ice40) | apio install ice40 | iCE40 place & route and configuration tools. [Icestorm project](http://www.clifford.at/icestorm)
| [ecp5](https://github.com/FPGAwars/toolchain-ecp5)   | apio install ecp5  | ECP5 tools including [Project Trellis](https://github.com/SymbiFlow/prjtrellis) and [nextpnr](https://github.com/YosysHQ/nextpnr)
| [iverilog](https://github.com/FPGAwars/toolchain-iverilog) | apio install iverilog | Verilog simulation and synthesis tool. [Icarus Verilog project](http://iverilog.icarus.com)
| [scons](https://github.com/FPGAwars/tool-scons) | apio install scons | A software construction tool. [Scons project](http://scons.org)
| [system](https://github.com/FPGAwars/tools-system) | apio install system | Tools for listing the USB devices and retrieving information from the FTDI chips
| [verilator](https://github.com/FPGAwars/toolchain-verilator) | apio install verilator | Verilog HDL simulator. [Verilator project](https://www.veripool.org/wiki/verilator)
| [icesprog](https://github.com/aalku/apio-toolchain-iCESugar) | apio install icesprog | iCESugar programmer. (Windows and Linux, x86 and x64)

**Supported platforms**

*linux_x86_64, linux_i686, linux_armv7l, linux_aarch64, windows_x86, windows_amd64, darwin*.

## Supported boards

#### HX1K

| Board name | Interface |
|:-|:-:|
| [IceZUM Alhambra](https://github.com/FPGAwars/icezum) | FTDI |
| [Nandland Go board](https://www.nandland.com/goboard/introduction.html) | FTDI |
| [iCEstick Evaluation Kit](http://www.latticesemi.com/icestick) | FTDI |
| [iCEblink40-HX1K](http://www.latticesemi.com/iCEblink40-HX1K) | Digilent Adept |

#### HX8K

| Board name | Interface |
|:-|:-:|
| [Alchitry-Cu](https://alchitry.com/products/alchitry-cu-fpga-development-board) | | FTDI |
| [Alhambra II](https://github.com/FPGAwars/Alhambra-II-FPGA) | FTDI |
| [BlackIce](https://hackaday.io/project/12930-blackice-low-cost-open-hardware-fpga-dev-board) | Serial |
| [BlackIce II](https://github.com/mystorm-org/BlackIce-II) | Serial |
| [Blackice-mx](https://www.tindie.com/products/Folknology/blackice-mx/) | Serial |
| [CAT Board](https://hackaday.io/project/7982-cat-board) | GPIO RPi |
| [icoBOARD 1.0](http://icoboard.org/about-icoboard.html) | GPIO RPi |
| [Kéfir I iCE40-HX4K](http://fpgalibre.sourceforge.net/Kefir/) | FTDI |
| [iCE40-HX8K Breakout Board](http://www.latticesemi.com/Products/DevelopmentBoardsAndKits/iCE40HX8KBreakoutBoard) | FTDI |
| [Alchitry Cu](https://alchitry.com/products/alchitry-cu-fpga-development-board) | FTDI |
| [iceFUN](https://www.robot-electronics.co.uk/icefun.html) | Serial |

#### LP8K

| Board name | Interface |
|:-|:-:|
| [TinyFPGA B2](https://tinyfpga.com/b-series-guide.html) | Serial |
| [TinyFPGA BX](https://tinyfpga.com/bx/guide.html) | Serial |

#### UP5K

| Board name | Interface |
|:-|:-:|
| arice1 | |
| [Fomu](https://github.com/im-tomu/fomu-hardware) | DFU |
| [FPGA 101 Workshop Badge Board](https://github.com/mmicko/workshop_badge) | FTDI |
| [iCEBreaker](https://github.com/icebreaker-fpga/icebreaker) | FTDI |
| [iCEBreaker bitsy](https://github.com/icebreaker-fpga/icebreaker) | FTDI |
| [iCE40 UltraPlus Breakout Board](http://www.latticesemi.com/en/Products/DevelopmentBoardsAndKits/iCE40UltraPlusBreakoutBoard) | FTDI |
| [UPDuino v1.0](http://gnarlygrey.atspace.cc/development-platform.html#upduino) | FTDI |
| [UPDuino v2.0](http://gnarlygrey.atspace.cc/development-platform.html#upduino_v2) | FTDI |
| [UPDuino v2.1](https://github.com/tinyvision-ai-inc/UPduino-v2.1) | FTDI |
| [UPDuino v3.0](https://github.com/tinyvision-ai-inc/UPduino-v3.0) | FTDI |
| [iCESugar v1.5](https://github.com/wuxx/icesugar/blob/master/README_en.md) (Windows and Linux, x86 and x64) | FTDI |


#### ECP5
| Board name | Interface |
|:-|:-:|
| [OrangeCrab r0.2](https://github.com/gregdavill/OrangeCrab) | FTDI |
| [TinyFPGA-EX-rev1](https://github.com/tinyfpga/TinyFPGA-EX) | Serial |
| [TinyFPGA-EX-rev2](https://www.crowdsupply.com/tinyfpga/tinyfpga-ex) | Serial |
| [ULX3S-12F](https://radiona.org/ulx3s/) | Ujprog |
| [ULX3S-25F](https://radiona.org/ulx3s/) | Ujprog |
| [ULX3S-45F](https://radiona.org/ulx3s/) | Ujprog |
| [ULX3S-85F](https://radiona.org/ulx3s/) | Ujprog |
| [Versa](https://www.mouser.es/new/lattice-semiconductor/lattice-lfe5um-45f-versa-evn/) | |


NOTE: all supported [Icestorm FPGAs](http://www.clifford.at/icestorm/) can be used with [--fpga or --size, --type and --pack options](http://apiodoc.readthedocs.io/en/develop/source/user_guide/project_commands/cmd_build.html#options).

## Documentation

The complete documentation of the project can be found in Read the Docs: http://apiodoc.readthedocs.io. There is also a list of frequently asked questions (FAQ) that you can check [here](./FAQ.md).

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

### Documentation

```bash
cd docs
make html
firefox _build/html/index.html
```

### Debian packaging

Also you can find the debian scripts to package the full application and all the packages here: https://github.com/set-soft/apio-debian.

Thanks Salvador E. Tropea!

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
* [Miodrag Milanovic](https://github.com/mmicko)
* [Carlos Venegas](https://github.com/cavearr)

## Credits

* APIO was inspired by [PlatformIO](https://github.com/platformio/platformio).

* [FPGAwars](http://fpgawars.github.io/) community has developed this project in a voluntary and altruistic way since 11/2016.

  <img src="https://avatars3.githubusercontent.com/u/18257418?s=100">

* [BQ](https://www.bq.com) sponsored this project from 02/2016 to 11/2016. Thanks.

## License

Licensed under [GPL 2.0](http://opensource.org/licenses/GPL-2.0) and [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

[apio-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/apio-logo-mini.png
[linux-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/linux.png
[macosx-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/macosx.png
[windows-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/windows.png
[ubuntu-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/ubuntu.png
[raspbian-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/raspbian.png
