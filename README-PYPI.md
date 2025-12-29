![][apio-cli-banner]

[![License][license-image]][license-url]

[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://github.com/FPGAwars/apio)

![][linux-logo]&nbsp;&nbsp;&nbsp;![][macosx-logo]&nbsp;&nbsp;&nbsp;![][windows-logo]&nbsp;&nbsp;&nbsp;![][ubuntu-logo]&nbsp;&nbsp;&nbsp;![][raspbian-logo]

**TL;DR**, Apio CLI is an easy to use command line tool for FPGA development. For q quick start, visit the [Getting started with Apio](https://fpgawars.github.io/apio/docs/quick-start) page.

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
> Apio is a command line tool that automates installing the toolchain for your FPGA and running it. It just simplifies things, you don't have to use it if you'd rather call the individual tools for synthesis, P&R, simulation etc. It'd be reasonable to think of it as akin to a very smart Makefile combined with an automatic package manager, specialized to FPGAs (it's based on PlatformIO). It's nice when you're still kind of getting oriented, because you don't need to know how to set up and invoke the different tools... just call `apio build` or `apio sim`

## Resources

- [Apio CLI Documentation](https://fpgawars.github.io/apio/docs/)
- [Getting started with Apio](https://fpgawars.github.io/apio/docs/quick-start)
- [Apio CLI github repository](https://github.com/fpgawars/apio)

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
