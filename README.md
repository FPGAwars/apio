[![][apio-logo]][wiki]

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![License][license-image]][license-url]

![][linux-logo]&nbsp;&nbsp;&nbsp;![][macosx-logo]&nbsp;&nbsp;&nbsp;![][windows-logo]&nbsp;&nbsp;&nbsp;![][ubuntu-logo]&nbsp;&nbsp;&nbsp;![][raspbian-logo]


**TL;DR, Apio is an extremly easy to install and use open-source toolbox for programming FPGA boards.**

## What is Apio?

* Apio is an **extremly easy to use** toolbox for FPGA programming.
* Apio is **easy to install**, no more dealing with 'toolcahins', licenses, scripts, and makefiles.
* Apio runs on a wide range of platforms, **Linux, Windows, Mac, and more**.
* Apio is **open source and free to use**.
* Apio supports **all aspects of FPGA developement cycles**, including building, simulation, testing, and uploading a design.
* **Apio commands are very simple,** for example, ``apio build`` to build, ``apio test`` to test end ``apio upload`` to upload.
* Apio can be used with **any text editor** and also **playes well with Visual Studio Code and github**.
* Apio supports out of the **more than 80 boards** and **custom boards can be easily added**.
* Apio provides out of the box tens of simple **project examples ready to build and upload**.
* Apio currently supports the ``ICE40`` and ``ECP5`` FPGA architecture with ``GOWIN`` architecture in the works.

## The Apio phylosophy

Apio makes **extremely easy** the process of working with **FPGAs**. Go from **scratch** to having a **blinky LED** in your FPGA board in minutes! This is because it is was designed for ease of use and uses only **Free/Libre Open Source Software** (FLOSS). Just install it and use it as you want.


In this animation you can see the whole process of testing the Blinky led circuit: Just type the command ``apio upload`` and the circuit will be synthesized, and uploaded into the FPGA

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Quick-start/apio-alhambra-II-01.gif)



As the user **gh02t** said in this post on [Hacker-news](https://news.ycombinator.com/item?id=17912510):
> Apio is a command line tool that automates installing the toolchain for your FPGA and running it. It just simplifies things, you don't have to use it if you'd rather call the individual tools for synthesis, P&R, simulation etc. It'd be reasonable to think of it as akin to a very smart Makefile combined with an automatic package manager, specialized to FPGAs (it's based on PlatformIO). It's nice when you're still kind of getting oriented, because you don't need to know how to set up and invoke the different tools... just call `apio build` or `apio simulate`

## Sample Apio Commands

Below are typical apio commands that are used during the project developement cycle. The commands
are simple and intuitive.

```
# Create a project
apio examples -f alhambra-ii/ledon   # Fetch the files of an example

# Build
apio build                           # Build the project
apio upload                          # Upload the design to the FPGA board

# Verification
apio lint                            # Inspect the source code for issues.
apio test                            # Run the testbench
apio sim ledon_tb.v                  # Simulate the testbench and open a graphical viewer.
```

## Apio and higher level tools

While many use Apio as a stand alone text based CLI toolbox, it can also be used with higher level graphical tools such as [Icestudio](https://icestudio.io/):


![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Introduction/icestudio-example.png)


## Apio in the media

[Shawn Hymel's](https://shawnhymel.com/) excellent series on FPGA programming is based on **Apio** and the the Icestick board

[![Introduction to FPGA YouTube Series](https://raw.githubusercontent.com/ShawnHymel/introduction-to-fpga/main/images/Intro%20to%20FPGA%20Part%201_Thumbnail.png)](https://www.youtube.com/watch?v=lLg1AgA2Xoo&list=PLEBQazB0HUyT1WmMONxRZn9NmQ_9CIKhb)


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
* [Zapta](https://github.com/zapta)

## Credits

* Apio is uses the [YosysHQ](https://www.yosyshq.com) open source toolchain.

* APIO was inspired by [PlatformIO](https://github.com/platformio/platformio).

* [FPGAwars](http://fpgawars.github.io/) community has developed this project in a voluntary and altruistic way since 11/2016.


* Apio is implemented in Python and using the packages [Click](https://pypi.org/project/click/), and [Scons](https://pypi.org/project/SCons/).

* [BQ](https://www.bq.com) sponsored this project from 02/2016 to 11/2016. Thanks.


## License

Licensed under [GPL 2.0](http://opensource.org/licenses/GPL-2.0) and [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

--------
[![](https://github.com/FPGAwars/icestudio-wiki/raw/main/Logos/fgpawars-banner.svg)](https://fpgawars.github.io/)


<!-- Badges and URLs -->

[apio-logo]: https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Logos/Apio-github.png

[pypi-image]: https://img.shields.io/pypi/v/apio
[pypi-url]: https://pypi.org/project/apio/

[build-image]: https://github.com/FPGAwars/apio/actions/workflows/build.yml/badge.svg
[build-url]: https://github.com/FPGAwars/apio/actions/workflows/build.yml

[license-image]: http://img.shields.io/:license-gpl-blue.svg
[license-url]: (http://opensource.org/licenses/GPL-2.0)


[linux-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/linux.png
[macosx-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/macosx.png
[windows-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/windows.png
[ubuntu-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/ubuntu.png
[raspbian-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/raspbian.png

[wiki]: https://github.com/FPGAwars/apio/wiki
