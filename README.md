![][apio-logo]

[![Build Status](https://travis-ci.org/FPGAwars/apio.svg?branch=develop)](https://travis-ci.org/FPGAwars/apio)
[![Latest Version](https://img.shields.io/pypi/v/apio.svg)](https://pypi.python.org/pypi/apio/)
[![License](http://img.shields.io/:license-gpl-blue.svg)](http://opensource.org/licenses/GPL-2.0)
[![Documentation Status](https://readthedocs.org/projects/apiodoc/badge/?version=latest)](http://apiodoc.readthedocs.io/en/latest/)
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


Experimental open source micro-ecosystem for **open FPGAs**. Based on [platformio](https://github.com/platformio/platformio). Apio is a **multiplatform toolbox**, with static pre-built packages, project configuration tools and easy commands to verify, synthesize, simulate and upload your **verilog** designs.

Apio is used by [Icestudio](https://github.com/FPGAwars/icestudio).

## Installation

1. Install [Python 2.7](https://www.python.org/downloads) and [pip](https://pip.pypa.io)

2. Install the latest apio: ```pip install -U apio```

## Apio packages

| Package | Installation   | Description
|---------|----------------|---------------
| [icestorm](https://github.com/FPGAwars/toolchain-icestorm)  | apio install icestorm | iCE40 FPGA synthesis, place & route and configuration tools. [Icestorm project](http://www.clifford.at/icestorm/)
| [iverilog](https://github.com/FPGAwars/toolchain-iverilog)  | apio install iverilog | Verilog simulation and synthesis tool. [Icarus Verilog project](http://iverilog.icarus.com/)
| [scons](https://github.com/FPGAwars/tool-scons)  | apio install scons | A software construction tool. [Scons project](http://scons.org/)
| [system](https://github.com/FPGAwars/tools-usb-ftdi)  | apio install system | Tools for listing the USB devices and retrieving information from the FTDI chips
| [examples](https://github.com/FPGAwars/apio-examples)  | apio install examples | Verilog basic examples, pinouts, etc
| [pio-fpga](https://github.com/FPGAwars/Platformio-FPGA)  | apio install pio-fpga | PlatformIO experimental configuration for supporting Lattice FPGA boards

Supported architectures: *linux_x86_64, linux_i686, linux_armv7l, linux_aarch64, darwin, windows*.

## Supported boards

| Board
|-------
| [Icezum Alhambra](https://github.com/FPGAwars/icezum)
| [Nandland Go board](https://www.nandland.com/goboard/introduction.html)
| [iCEstick Evaluation Kit ](http://www.pighixxx.com/test/portfolio-items/icestick/)
| [iCE40-HX8K Breakout Board](http://www.latticesemi.com/en/Products/DevelopmentBoardsAndKits/iCE40HX8KBreakoutBoard.aspx)
| [icoBOARD 1.0](http://icoboard.org/icoboard-1-0.html)
| [CAT Board](https://hackaday.io/project/7982-cat-board)

NOTE: all supported [Icestorm FPGAs](http://www.clifford.at/icestorm/) can be used with [--fpga, --size, --type and --pack options](http://apiodoc.readthedocs.io/en/develop/source/user_guide/code_commands/cmd_build.html#options).

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
tox -e flake8
tox -e coverage
```

## Videos

[![Apio in RPI2: iCEstick, Icezum and icoBOARD ](http://img.youtube.com/vi/xLb7T4pw9iY/0.jpg)](https://www.youtube.com/watch?v=xLb7T4pw9iY "Apio in RPI2: iCEstick, Icezum and icoBOARD ")

[![Apio: an easy multi-platform toolbox for open FPGAs](http://img.youtube.com/vi/UJ6-_42P5BE/0.jpg)](https://www.youtube.com/watch?v=UJ6-_42P5BE "Apio: an easy multi-platform toolbox for open FPGAs")

## Authors

* [Jesús Arroyo Torrens](https://github.com/Jesus89)
* [Juan González (Obijuan)](https://github.com/Obijuan)

## Contributors

* [Miguel Sánchez de León Peque](https://github.com/peque)
* [devbisme](https://github.com/devbisme)

## License
![](https://github.com/FPGAwars/apio/raw/master/docs/resources/images/bq-logo-cc-sa-small-150px.png)

Licensed under a [GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html) and [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/)

[apio-logo]: docs/resources/images/apio-logo-mini.png
[linux-logo]: docs/resources/images/linux.png
[macosx-logo]: docs/resources/images/macosx.png
[windows-logo]: docs/resources/images/windows.png
[ubuntu-logo]: docs/resources/images/ubuntu.png
[raspbian-logo]: docs/resources/images/raspbian.png
[bq-license]: docs/resources/images/bq-logo-cc-sa-small-150px.png
