<!--
This README page is optimized for its appearance in the github repo rather than for the PyPi listing.
-->

<!-- Page banner -->
![apio-cli-banner](media/apio-cli-banner.png)

<!-- Attributes badges -->
[![license](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://github.com/FPGAwars/apio/blob/main/LICENSE)
[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/apio)

<!-- Platforms badges -->
![linux](media/linux-logo.png)&nbsp;&nbsp;&nbsp;![macos](media/macosx-logo.png)&nbsp;&nbsp;&nbsp;![windows](media/windows-logo.png)&nbsp;&nbsp;&nbsp;![raspberry-pi](media/raspbian-logo.png)

<!-- Status badges -->
[![cli-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/test.yaml?label=cli-test)](https://github.com/fpgawars/apio/actions/workflows/test.yaml)
[![cli-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/build-pre-release.yaml?label=cli-build)](https://github.com/fpgawars/apio/actions/workflows/build-pre-release.yaml)
[![cli-docs](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/publish-docs.yaml?label=cli-docs)](https://github.com/fpgawars/apio/actions/workflows/publish-docs.yaml)
[![cli-pypi-monitor](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/monitor-apio-pypi.yaml?label=cli-pypi-monitor)](https://github.com/fpgawars/apio/actions/workflows/monitor-apio-pypi.yaml)
[![cli-latest-monitor](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/monitor-apio-latest.yaml?label=cli-latest-monitor)](https://github.com/fpgawars/apio/actions/workflows/monitor-apio-latest.yaml)
[![ide-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-vscode/test.yaml?label=ide-test)](https://github.com/fpgawars/apio-vscode/actions/workflows/test.yaml)
[![ide-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-vscode/build-pre-release.yaml?label=ide-build)](https://github.com/fpgawars/apio-vscode/actions/workflows/build-pre-release.yaml)
[![examples-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-examples/test.yaml?label=examples-test)](https://github.com/fpgawars/apio-examples/actions/workflows/test.yaml)
[![examples-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-examples/build-pre-release.yaml?label=examples-build)](https://github.com/fpgawars/apio-examples/actions/workflows/build-pre-release.yaml)
[![definitions-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-definitions/test.yaml?label=definitions-test)](https://github.com/fpgawars/apio-definitions/actions/workflows/test.yaml)
[![definitions-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-definitions/build-pre-release.yaml?label=definitions-build)](https://github.com/fpgawars/apio-definitions/actions/workflows/build-pre-release.yaml)
[![oss-cad-suite-build](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-oss-cad-suite/build-pre-release.yaml?label=oss-cad-suite-build)](https://github.com/fpgawars/tools-oss-cad-suite/actions/workflows/build-pre-release.yaml)
[![verible-build](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-verible/build-pre-release.yaml?label=verible-build)](https://github.com/fpgawars/tools-verible/actions/workflows/build-pre-release.yaml)
[![graphviz-build](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-graphviz/build-pre-release.yaml?label=graphviz-build)](https://github.com/fpgawars/tools-graphviz/actions/workflows/build-pre-release.yaml)
[![drivers-build](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-drivers/build-pre-release.yaml?label=drivers-build)](https://github.com/fpgawars/tools-drivers/actions/workflows/build-pre-release.yaml)
[![workflows-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-workflows/test.yaml?label=workflows-test)](https://github.com/fpgawars/apio-workflows/actions/workflows/test.yaml)
[![apio-backup](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-workflows/backup-apio-repos.yaml?label=apio-backup)](https://github.com/fpgawars/apio-workflows/actions/workflows/backup-apio-repos.yaml)

---

Apio CLI is an easy to install and use command-line tool for FPGA design from A to Z. For a quick start, visit the [Getting started with Apio](https://fpgawars.github.io/apio/docs/quick-start) guide.

<br>

Simulation example:

![GTKWave screenshot](media/sim-gtkwave.png)

## Description

Apio CLI is a powerful yet easy-to-use command line tool for FPGA development using Verilog and System Verilog. It’s simple to install, no toolchains, licenses, or makefiles required, and works across Linux, Windows, and macOS. Apio CLI is 100% open source, and free to use.

Apio CLI supports every stage of the FPGA workflow, from simulating and testing, to building and programming the FPGA, using simple commands such as `apio test`, `apio build`, and `apio upload` that do what you expect them to do.

Apio CLI currently supports over 80 FPGA boards, custom boards can be easily added, and it includes over 60 ready-to-use example projects. Apio CLI currently supports the ICE40, ECP5, and GOWIN FPGA architectures.

## Sample Apio CLI session

1. `apio examples fetch alhambra-ii/getting-started` - fetch an example.
2. `apio build` - build the project.
3. `apio report` - report utilization and max clock speed.
4. `apio sim` - simulate the design and show signals.
5. `apio upload` - program the FPGA board.

![apio-cli-animation](media/apio-cli-animation.gif)

## Apio CLI in the media

[Shawn Hymel's](https://shawnhymel.com/) excellent series on FPGA programming is based on and older version of **Apio CLI** and the the Icestick board

[![Introduction to FPGA YouTube Series](https://raw.githubusercontent.com/ShawnHymel/introduction-to-fpga/main/images/Intro%20to%20FPGA%20Part%201_Thumbnail.png)](https://www.youtube.com/watch?v=lLg1AgA2Xoo&list=PLEBQazB0HUyT1WmMONxRZn9NmQ_9CIKhb)

As the user **gh02t** said in this post on [Hacker-news](https://news.ycombinator.com/item?id=17912510):

> Apio is a command-line tool that automates installing the toolchain for your FPGA and running it. It just simplifies things, you don't have to use it if you'd rather call the individual tools for synthesis, P&R, simulation etc. It'd be reasonable to think of it as akin to a very smart Makefile combined with an automatic package manager, specialized to FPGAs (it's based on PlatformIO). It's nice when you're still kind of getting oriented, because you don't need to know how to set up and invoke the different tools... just call `apio build` or `apio sim`

## Resources

- [Apio CLI Documentation](https://fpgawars.github.io/apio/docs/)
- [Getting started with Apio](https://fpgawars.github.io/apio/docs/quick-start)
- [Apio CLI github repository](https://github.com/fpgawars/apio)
- [Apio CLI package on PyPi](https://pypi.org/project/apio/)
- [Apio CLI development environment](https://fpgawars.github.io/apio/docs/development-environment/) (for Apio CLI developers).
- [Apio CLI daily build](https://github.com/fpgawars/apio/releases)
- [Apio CLI Test Coverage Report](https://fpgawars.github.io/apio/coverage/)

## Credits

- Apio CLI was inspired by [PlatformIO](https://github.com/platformio/platformio) and was originally created by [Jesús Arroyo Torrens](https://github.com/Jesus89) in February 2016.
- Thanks to all the Apio CLI [contributors](https://github.com/FPGAwars/apio/graphs/contributors) over the years.
- Apio CLI uses open source tools including [Yosys](https://www.yosyshq.com), [Click](https://pypi.org/project/click), [Scons](https://pypi.org/project/SCons), [GTKWave](https://gtkwave.sourceforge.net), and [Python](https://www.python.org/downloads).
- [BQ](https://www.bq.com) sponsored this project from 02/2016 to 11/2016. Thanks.

## License

The Apio project itself is licensed under the GNU General Public License version 3.0 (GPL-3.0).
Pre-built packages may include third-party tools and components, which are subject to their
respective license terms.
