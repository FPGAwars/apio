[![][apio-logo]][wiki]

[![PyPI Version][pypi-image]][pypi-url]
[![License][license-image]][license-url]




[![apio-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/test.yaml?label=apio-test)](https://github.com/fpgawars/apio/actions/workflows/test.yaml)
[![apio-dev-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-dev-builds/build-and-release.yaml?label=apio-dev-build)](https://github.com/fpgawars/apio-dev-builds/actions/workflows/build-and-release.yaml)
[![monitor-apio-prod](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/monitor-apio-prod.yaml?label=apio-prod-monitor)](https://github.com/fpgawars/apio/actions/workflows/monitor-apio-prod.yaml)
[![monitor-apio-latest](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/monitor-apio-latest.yaml?label=apio-latest-monitor)](https://github.com/fpgawars/apio/actions/workflows/monitor-apio-latest.yaml)
[![mkdocs-publishing](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/publish-mkdocs-docs.yaml?label=apio-mkdocs)](https://github.com/fpgawars/apio/actions/workflows/publish-mkdocs-docs.yaml)
[![examples-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-examples/test.yaml?label=apio-xamples)](https://github.com/fpgawars/apio-examples/actions/workflows/test.yaml)
[![oss-cad-suite-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-oss-cad-suite/build-and-release.yaml?label=apio-oss-cad-suite)](https://github.com/fpgawars/tools-oss-cad-suite/actions/workflows/build-and-release.yaml)
[![verible-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-verible/build-and-release.yaml?label=apio-verible)](https://github.com/fpgawars/tools-verible/actions/workflows/build-and-release.yaml)
[![graphviz-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-graphviz/build-and-release.yaml?label=apio-graphviz)](https://github.com/fpgawars/tools-graphviz/actions/workflows/build-and-release.yaml)
[![drivers-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-drivers/build-and-release.yaml?label=apio-drivers)](https://github.com/fpgawars/tools-drivers/actions/workflows/build-and-release.yaml)




![][linux-logo]&nbsp;&nbsp;&nbsp;![][macosx-logo]&nbsp;&nbsp;&nbsp;![][windows-logo]&nbsp;&nbsp;&nbsp;![][ubuntu-logo]&nbsp;&nbsp;&nbsp;![][raspbian-logo]


## What is Apio?

Apio is a powerful yet **easy-to-use toolbox for FPGA development using Verilog and System Verilog**. It’s simple to install, no toolchains, licenses, or makefiles required, and works across **Linux, Windows, and macOS**. Apio is **open source, free to use**, and supports every stage of the FPGA workflow, **from simulating and testing, to building and programming the FPGA**, using simple commands such as `apio test`, `apio build`, and `apio upload` that do what you expect them to do. Apio integrates smoothly with any text editor and works great with Visual Studio Code and GitHub. It currently supports over **80 FPGA boards**, custom boards can be easily added, and it includes over 60 **ready-to-use example projects**. Apio currently supports the **ICE40, ECP5, and GOWIN** FPGA architectures.

[Example] Simulation results using the command `apio sim`:
![](docs/assets/sim-gtkwave.png)

## The Apio philosophy

Apio was designed from the ground up to be **extremely easy to use** and use only **Free/Libre Open Source Software** (FLOSS). Just install it and use it as you like.


In this animation you can see the whole process of testing the Blinky led circuit: Just type the command ``apio upload`` and the circuit will be synthesized, and uploaded into the FPGA

![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Quick-start/apio-alhambra-II-01.gif)



As the user **gh02t** said in this post on [Hacker-news](https://news.ycombinator.com/item?id=17912510):
> Apio is a command line tool that automates installing the toolchain for your FPGA and running it. It just simplifies things, you don't have to use it if you'd rather call the individual tools for synthesis, P&R, simulation etc. It'd be reasonable to think of it as akin to a very smart Makefile combined with an automatic package manager, specialized to FPGAs (it's based on PlatformIO). It's nice when you're still kind of getting oriented, because you don't need to know how to set up and invoke the different tools... just call `apio build` or `apio simulate`

## Sample Apio Commands

Below are typical Apio commands used during the project development cycle. The commands are simple and intuitive.

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

While many use Apio as a stand alone text based CLI toolbox, it can also be used with higher level graphical tools such as its sister project [Icestudio](https://icestudio.io/):


![](https://github.com/FPGAwars/Apio-wiki/raw/main/wiki/Introduction/icestudio-example.png)


## Apio in the media

[Shawn Hymel's](https://shawnhymel.com/) excellent series on FPGA programming is based on **Apio** and the the Icestick board

[![Introduction to FPGA YouTube Series](https://raw.githubusercontent.com/ShawnHymel/introduction-to-fpga/main/images/Intro%20to%20FPGA%20Part%201_Thumbnail.png)](https://www.youtube.com/watch?v=lLg1AgA2Xoo&list=PLEBQazB0HUyT1WmMONxRZn9NmQ_9CIKhb)


## Resources

* [Apio Documentation](https://fpgawars.github.io/apio/)
* [Getting started with Apio](https://fpgawars.github.io/apio/quick-start)
* [Apio github repository](https://github.com/FPGAwars/apio)
* [Apio package on PyPi](https://pypi.org/project/apio/)
* [Apio daily builds](https://github.com/FPGAwars/apio-dev-builds)



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
