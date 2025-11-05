# Apio System Requirements

> The information on this page was last updated in October 2025.

## Operating System

Apio is tested on the following platforms (as of Nov 2025):

| Apio Platform Code | Description           | Tested Github Versions |
| :----------------- | :-------------------- | :--------------------- |
| darwin_arm64       | macOS (Apple Silicon) | Latest macOS           |
| darwin_x86_64      | macOS (Intel)         | macOS 15               |
| linux_x86_64       | Linux x86 64-bit      | Ubuntu 24.04 LTS       |
| linux_aarch64      | Linux ARM 64-bit      | Not tested             |
| windows_amd64      | Windows x86 64-bit    | Windows latest         |

> The tested version are set in the Apio github test workflow.

## Python

These requirements apply only when installing Apio as a Pip package (Python-based installation).

> Python is not required when installing Apio using an installer, Debian package, or a file bundle.

> To test the Python version, run `python --version`. To download Python, visit [python.org](https://www.python.org/downloads/).

| Python Version | Status      |
| :------------- | :---------- |
| 3.14.x         | Recommended |
| 3.13.x         | Supported   |
| 3.12.x         | Supported   |
| 3.11.x         | Supported   |
