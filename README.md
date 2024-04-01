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


### A verilog circuit in VSCode

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Introduction/vscode-example.png)

## Documentation

Find all the information on this [WIKI PAGE](https://github.com/FPGAwars/apio/wiki)


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
[linux-logo]: https://github.com/FPGAwars/Apio-wiki/blob/main/wiki/Logos/linux.png
[macosx-logo]: https://github.com/FPGAwars/Apio-wiki/blob/main/wiki/Logos/macosx.png
[windows-logo]: https://github.com/FPGAwars/Apio-wiki/blob/main/wiki/Logos/windows.png
[ubuntu-logo]: https://github.com/FPGAwars/Apio-wiki/blob/main/wiki/Logos/ubuntu.png
[raspbian-logo]: https://github.com/FPGAwars/Apio-wiki/blob/main/wiki/Logos/raspbian.png

[wiki]: https://github.com/FPGAwars/apio/wiki
