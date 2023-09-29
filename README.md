[![][apio-logo]][wiki]

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![License][license-image]][license-url]

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

## What is Apio?

Apio is a **multiplatform** toolbox with **static** pre-built packages to verify, synthesize, simulate and upload your verilog designs into the supported **FPGA boards**

## What??????

Apio makes **extremely easy** the process of working with **FPGAs**. Go from **scratch** to having a **blinky LED** in your FPGA board in minutes! This is because it is based only on **Free/Libre Open Source Software** (FLOSS). Just install it and use it as you want


In this animation you can see the whole process of testing the Blinky led circuit: Just type one command and the circuit will be synthesized, and uploaded into the FPGA

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Quick-start/apio-alhambra-II-01.gif)

Think of Apio as a small **FPGA distribution**, which **collects** and **packages** **FLOSS toolchains for FPGAs**. You can install packages in **Linux**, **Mac** and **Windows** for synthesizing hardware, verifying and simulating from verilog files

The goal is making it **very easy** to start with FPGAs

As the user **gh02t** said in this post on [Hacker-news](https://news.ycombinator.com/item?id=17912510):
> Apio is a command line tool that automates installing the toolchain for your FPGA and running it. It just simplifies things, you don't have to use it if you'd rather call the individual tools for synthesis, P&R, simulation etc. It'd be reasonable to think of it as akin to a very smart Makefile combined with an automatic package manager, specialized to FPGAs (it's based on PlatformIO). It's nice when you're still kind of getting oriented, because you don't need to know how to set up and invoke the different tools... just call `apio build` or `apio simulate`

## Apio and higher level tools

Apio has a **command line interface** (CLI). It is the **building block** for other **higher level tools**, like [Icestudio](https://icestudio.io/), [Apio-IDE](https://github.com/FPGAwars/apio-ide) or working with FPGAs from IDEs such as [Visual Studio Code](https://code.visualstudio.com/)


### A circuit in Icestdio

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Introduction/icestudio-example.png)

### A verilog circuit in Apio-IDE

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Introduction/apio-ide-example.jpg)

### A verilog circuit in VSCode

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Introduction/vscode-example.png)

## Documentation

Find all the information on this [WIKI PAGE](https://github.com/FPGAwars/apio/wiki)

## Apio packages

| Package | Installation   | Description
|---------|----------------|---------------
| [tools-oss-cad-suite](https://github.com/FPGAwars/tools-oss-cad-suite) | apio install oss-cad-suite| Selected binaries from the [YosysHQ/oss-cad-suite project](https://github.com/YosysHQ/oss-cad-suite-build) 
| [examples](https://github.com/FPGAwars/apio-examples) | apio install examples | Verilog basic examples, pinouts, etc
| [drivers](https://github.com/FPGAwars/tools-drivers) | apio install drivers | Drivers tools (only for Windows)
| [gtkwave](https://github.com/FPGAwars/tool-gtkwave) | apio install gtkwave | Simulation viewer. [GTKWave project](http://gtkwave.sourceforge.net) (only for Windows) 



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
| [Alhambra II](https://github.com/FPGAwars/Alhambra-II-FPGA) | FTDI |
| [BlackIce](https://hackaday.io/project/12930-blackice-low-cost-open-hardware-fpga-dev-board) | Serial |
| [BlackIce II](https://github.com/mystorm-org/BlackIce-II) | Serial |
| [Blackice-mx](https://www.tindie.com/products/Folknology/blackice-mx/) | Serial |
| [CAT Board](https://hackaday.io/project/7982-cat-board) | GPIO RPi |
| [icoBOARD 1.0](http://icoboard.org/about-icoboard.html) | GPIO RPi |
| [Kéfir I iCE40-HX4K](http://fpgalibre.sourceforge.net/Kefir/) | FTDI |
| [iCE40-HX8K Breakout Board](http://www.latticesemi.com/Products/DevelopmentBoardsAndKits/iCE40HX8KBreakoutBoard) | FTDI |
| [Alchitry Cu](https://alchitry.com/boards/cu) | FTDI |
| [iceFUN](https://www.robot-electronics.co.uk/icefun.html) | Serial |
| [iceWerx](https://www.robot-electronics.co.uk/icewerx.html) | Serial |

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
| [iCEBreaker bitsy](https://github.com/icebreaker-fpga/icebreaker#icebreaker-bitsy) | DFU |
| [iCE40 UltraPlus Breakout Board](http://www.latticesemi.com/en/Products/DevelopmentBoardsAndKits/iCE40UltraPlusBreakoutBoard) | FTDI |
| [UPDuino v1.0](http://gnarlygrey.atspace.cc/development-platform.html#upduino) | FTDI |
| [UPDuino v2.0](http://gnarlygrey.atspace.cc/development-platform.html#upduino_v2) | FTDI |
| [UPDuino v2.1](https://github.com/tinyvision-ai-inc/UPduino-v2.1) | FTDI |
| [UPDuino v3.0](https://github.com/tinyvision-ai-inc/UPduino-v3.0) | FTDI |
| [iCESugar v1.5](https://github.com/wuxx/icesugar/blob/master/README_en.md)  | FTDI |
| [OK-iCE40Pro](https://github.com/WiFiBoy/OK-iCE40Pro)  | FTDI |
| [Pico-Ice](https://github.com/tinyvision-ai-inc/pico-ice)  | DFU |

#### ECP5
| Board name | Interface |
|:-|:-:|
| [OrangeCrab r0.2](https://github.com/orangecrab-fpga/orangecrab-hardware) | DFU |
| [ButterStick r1.0](https://github.com/butterstick-fpga/butterstick-hardware) | DFU |
| [TinyFPGA-EX-rev1](https://github.com/tinyfpga/TinyFPGA-EX) | Serial |
| [TinyFPGA-EX-rev2](https://www.crowdsupply.com/tinyfpga/tinyfpga-ex) | Serial |
| [ULX3S-12F](https://radiona.org/ulx3s/) | Ujprog |
| [ULX3S-25F](https://radiona.org/ulx3s/) | Ujprog |
| [ULX3S-45F](https://radiona.org/ulx3s/) | Ujprog |
| [ULX3S-85F](https://radiona.org/ulx3s/) | Ujprog |
| [Versa](https://www.mouser.es/new/lattice-semiconductor/lattice-lfe5um-45f-versa-evn/) | |
| [ColorLight-5A-75B-V61](https://github.com/q3k/chubby75/blob/master/5a-75b/hardware_V6.1.md)| FT2232H |
| [ColorLight-5A-75B-V7](https://github.com/q3k/chubby75/blob/master/5a-75b/hardware_V7.0.md)| FT2232H |
| [ColorLight-5A-75B-V8](https://github.com/q3k/chubby75/blob/master/5a-75b/hardware_V8.0.md)| FT2232H |
| [ColorLight-5A-75E-V6](https://github.com/q3k/chubby75/blob/master/5a-75e/hardware_V6.0.md)| FT2232H |
| [ColorLight-5A-75E-V71](https://github.com/q3k/chubby75/blob/master/5a-75e/hardware_V7.1.md)| FT2232H, FT232H or USB-Blaster |
| [ColorLight-i5-v7.0](https://github.com/wuxx/Colorlight-FPGA-Projects)| FT2232H, FT232H or USB-Blaster |
| [iCESugar-Pro](https://github.com/wuxx/icesugar-pro)| FT2232H, FT232H or USB-Blaster |
| [FleaFPGA-Ohm](https://github.com/Basman74/FleaFPGA-Ohm)| FT2232H, FT232H or USB-Blaster |
| [ECP5-Evaluation-Board](https://www.latticesemi.com/products/developmentboardsandkits/ecp5evaluationboard)| FT2232H |

#### LP1K

| Board name | Interface |
|:-|:-:|
| [iCESugar-nano](https://github.com/wuxx/icesugar-nano/blob/main/README.md)  | FTDI |


NOTE: all supported [Icestorm FPGAs](http://www.clifford.at/icestorm/) can be used with [--fpga or --size, --type and --pack options](http://apiodoc.readthedocs.io/en/develop/source/user_guide/project_commands/cmd_build.html#options).


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

* [BQ](https://www.bq.com) sponsored this project from 02/2016 to 11/2016. Thanks.

## License

Licensed under [GPL 2.0](http://opensource.org/licenses/GPL-2.0) and [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

--------
[![](https://github.com/FPGAwars/icestudio-wiki/raw/main/Logos/fgpawars-banner.svg)](https://fpgawars.github.io/)


<!-- Badges and URLs -->

[pypi-image]: https://img.shields.io/pypi/v/apio
[pypi-url]: https://pypi.org/project/apio/

[build-image]: https://github.com/FPGAwars/apio/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/FPGAwars/apio/actions/workflows/build.yml

[license-image]: http://img.shields.io/:license-gpl-blue.svg
[license-url]: (http://opensource.org/licenses/GPL-2.0)

[apio-logo]: https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Logos/Apio-github.png
[linux-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/linux.png
[macosx-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/macosx.png
[windows-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/windows.png
[ubuntu-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/ubuntu.png
[raspbian-logo]: https://github.com/FPGAwars/apio/raw/master/docs/resources/images/raspbian.png

[wiki]: https://github.com/FPGAwars/apio/wiki
