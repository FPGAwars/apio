![][apio-cli-banner]

[![License][license-image]][license-url]
[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://github.com/FPGAwars/apio)

![][linux-logo]&nbsp;&nbsp;&nbsp;![][macosx-logo]&nbsp;&nbsp;&nbsp;![][windows-logo]&nbsp;&nbsp;&nbsp;![][ubuntu-logo]&nbsp;&nbsp;&nbsp;![][raspbian-logo]


<details>
<summary>Additional badges</summary>

[![apio-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/test.yaml?label=apio-test)](https://github.com/fpgawars/apio/actions/workflows/test.yaml)
[![apio-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/build-and-release.yaml?label=apio-build)](https://github.com/fpgawars/apio/actions/workflows/build-and-release.yaml)
[![docs-publishing](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/publish-docs.yaml?label=apio-docs)](https://github.com/fpgawars/apio/actions/workflows/publish-docs.yaml)
[![monitor-apio-pypi](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/monitor-apio-pypi.yaml?label=apio-pypi-monitor)](https://github.com/fpgawars/apio/actions/workflows/monitor-apio-pypi.yaml)
[![monitor-apio-latest](https://img.shields.io/github/actions/workflow/status/fpgawars/apio/monitor-apio-latest.yaml?label=apio-latest-monitor)](https://github.com/fpgawars/apio/actions/workflows/monitor-apio-latest.yaml)
[![vscode-build](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-vscode/build-and-release.yaml?label=vscode-build)](https://github.com/fpgawars/apio-vscode/actions/workflows/build-and-release.yaml)
[![vscode-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-vscode/test.yaml?label=vscode-test)](https://github.com/fpgawars/apio-vscode/actions/workflows/test.yaml)
[![examples-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-examples/test.yaml?label=apio-examples-test)](https://github.com/fpgawars/apio-examples/actions/workflows/test.yaml)
[![examples-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-examples/build-and-release.yaml?label=apio-examples-build)](https://github.com/fpgawars/apio-examples/actions/workflows/build-and-release.yaml)
[![definitions-test](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-definitions/test.yaml?label=apio-definitions-test)](https://github.com/fpgawars/apio-definitions/actions/workflows/test.yaml)
[![definitions-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/apio-definitions/build-and-release.yaml?label=apio-definitions-build)](https://github.com/fpgawars/apio-definitions/actions/workflows/build-and-release.yaml)
[![oss-cad-suite-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-oss-cad-suite/build-and-release.yaml?label=apio-cad-suite-build)](https://github.com/fpgawars/tools-oss-cad-suite/actions/workflows/build-and-release.yaml)
[![verible-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-verible/build-and-release.yaml?label=apio-verible-build)](https://github.com/fpgawars/tools-verible/actions/workflows/build-and-release.yaml)
[![graphviz-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-graphviz/build-and-release.yaml?label=apio-graphviz-build)](https://github.com/fpgawars/tools-graphviz/actions/workflows/build-and-release.yaml)
[![drivers-build-and-release](https://img.shields.io/github/actions/workflow/status/fpgawars/tools-drivers/build-and-release.yaml?label=apio-drivers-build)](https://github.com/fpgawars/tools-drivers/actions/workflows/build-and-release.yaml)

</details>

---


**TL;DR**, Apio CLI is an easy to use command-line tool for FPGA design. For q quick start, visit the [Getting started with Apio](https://fpgawars.github.io/apio/docs/quick-start) page.

## Description

Apio CLI is a powerful yet easy-to-use command line tool for FPGA development using Verilog and System Verilog. It’s simple to install, no toolchains, licenses, or makefiles required, and works across Linux, Windows, and macOS. Apio CLI is 100% open source, free to use, and supports every stage of the FPGA workflow, from simulating and testing, to building and programming the FPGA, using simple commands such as `apio test`, `apio build`, and `apio upload` that do what you expect them to do. Apio CLI currently supports over 80 FPGA boards, custom boards can be easily added, and it includes over 60 ready-to-use example projects. Apio CLI currently supports the ICE40, ECP5, and GOWIN FPGA architectures.

## Sample Apio session

1. `apio examples fetch alhambra-ii/getting-started` - fetch an example.
2. `apio build` - build the project.
3. `apio report` - report utilization and max clock speed.
4. `apio sim` - simulate the design and show signals.
5. `apio upload` - program the FPGA board.

![][apio-cli-animation]

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

Licensed under [GPL 2.0](http://opensource.org/licenses/GPL-2.0) and [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

<!-- Badges and URLs -->

[apio-cli-banner]: https://raw.githubusercontent.com/FPGAwars/apio/refs/heads/main/media/apio-cli-banner.png
[apio-cli-animation]: https://raw.githubusercontent.com/FPGAwars/apio/refs/heads/main/media/apio-cli-animation.gif
[license-image]: http://img.shields.io/:license-gpl-blue.svg
[license-url]: (http://opensource.org/licenses/GPL-2.0)
[linux-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/linux.png
[macosx-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/macosx.png
[windows-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/windows.png
[ubuntu-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/ubuntu.png
[raspbian-logo]: https://raw.githubusercontent.com/FPGAwars/Apio-wiki/refs/heads/main/wiki/Logos/raspbian.png
