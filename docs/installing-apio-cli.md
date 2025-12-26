# Installing Apio CLI

!!! warning "Important – December 2025"

    **Do not** run `pip install apio` because this currently installs the **old and unsupported** Apio **0.9.5**.
    Please follow the instructions below to install the current, supported **Apio 1.x.x** series instead.

To install Apio CLI, select your desired method from the table below and click on your platform type in the instructions column. Note that not all methods are available to all platform.

| Method        | Description                                                                                                                                     | Instructions                                                                                                                                                                                           |
| :------------ | :---------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Installer** | Installation using an installer wizard.                                                                                                         | [macOS&nbsp;Apple&nbsp;Silicon](#mac-arm64-installer) <br>[Windows](#windows-x86-64-installer)                                                                                                         |
| **Debian**    | Installation using a Debian package and the `dpkg` package manager.                                                                             | [Linux X86-64](#linux-x86-debian)                                                                                                                                                                      |
| **Bundle**    | Installation using a file archive that contains all the necessary files to run Apio.                                                            | [macOS Apple Silicon](#mac-arm64-bundle) <br> [Linux X86-64](#linux-x86-bundle) <br> [Windows](#windows-x86-64-bundle)                                                                                 |
| **Pip**       | Installation using the Python `pip` command. This method requires [Python](https://www.python.org/downloads) to be preinstalled on your system. | [macOS&nbsp;Apple&nbsp;Silicon](#mac-arm64-pip) <br> [macOS Intel Silicon](#mac-x86-pip) <br> [Linux X86-64](#linux-x86-pip) <br> [Linux ARM-64](#linux-arm64-pip) <br> [Windows](#windows-x86-64-pip) |

---

## macOS Apple Silicon

### Install using an installer <a id="mac-arm64-installer"></a>

To install Apio CLI on macOS Apple Silicon using an installer, follow these steps:

1.  From the [latest release](https://github.com/fpgawars/apio/releases) download the installer file:

        apio-darwin-arm64-[date]-installer.pkg

2.  Run the following command to allow the unsigned Apio installer to run:

        xattr -c apio-darwin-arm64-*-installer.pkg

3.  Double-click on the installer file and follow the instructions.

4.  In a **new shell window**, run the following command to test your installation:

        apio

> NOTE: The installer creates the file `/etc/paths.d/Apio` to export
> automatically the path of the installed app.

<br>

### Install using a file bundle <a id="mac-arm64-bundle"></a>

To install Apio CLI on macOS Apple Silicon using a file bundle,
follow these steps:

1.  From the [latest release](https://github.com/fpgawars/apio/releases) download the file bundle:

        apio-darwin-arm64-[date]-bundle.tgz

2.  Run the following command to allow the unsigned Apio app to run.

        xattr -c apio-darwin-arm64-*-bundle.tgz

3.  **After you run the xattr command**, double click on the bundle file to uncompress it and reveal the `apio` directory with the application files.

4.  While in the `apio` directory, run the following command to test your installation:

        ./apio

5.  Move the `apio` directory to a location of your choosing and add it to your `$PATH`.

<br>

### Install using a Pip package <a id="mac-arm64-pip"></a>

To install Apio CLI on macOS Apple Silicon using a Pip package,
follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall -U git+https://github.com/fpgawars/apio.git@main

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

---

## macOS Intel Silicon

### Install using a Pip package <a id="mac-x86-pip"></a>

To install Apio CLI on macOS Intel Silicon using a Pip package, follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall -U git+https://github.com/fpgawars/apio.git@main

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

---

## Linux X86-64

### Install a Debian package <a id="linux-x86-debian"></a>

To install Apio CLI on Linux X86-64 using a Debian package, follow these steps:

1.  From the [latest release](https://github.com/fpgawars/apio/releases) download the Debian package file:

        apio-linux-x86-64-[date]-debian.deb

2.  In the directory where you downloaded the package, install it using:

        sudo dpkg -i ./apio-linux-x86-64-[date]-debian.deb

3.  In a **new shell window**, run the following command to test your installation:

        apio

<br>

### Install using a file bundle <a id="linux-x86-bundle"></a>

To install Apio CLI on Linux X86-64 using a file bundle, follow these steps:

1.  From the [latest release](https://github.com/fpgawars/apio/releases) download the file bundle:

        apio-linux-x86-64-[date]-bundle.tgz

2.  Uncompress the bundle file to reveal the `apio` directory with the application files.

        tar -xzf apio-linux-x86-64-*-bundle.tgz

3.  While in the `apio` directory, run the following command to test your installation:

        ./apio

4.  Move the `apio` directory to a location of your choosing and add it to your `$PATH`.

<br>

### Install using a Pip package <a id="linux-x86-pip"></a>

To install Apio CLI on Linux X86-64 using a Pip package, follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall -U git+https://github.com/fpgawars/apio.git@main

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

---

## Linux ARM-64

### Install using a Pip package <a id="linux-arm64-pip"></a>

To install Apio CLI on Linux ARM-64 using a Pip package, follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall -U git+https://github.com/fpgawars/apio.git@main

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

---

## Windows X86-64

### Install using an installer <a id="windows-x86-64-installer"></a>

To install Apio CLI on Windows X86-64 using an installer, follow these steps:

1.  From the [latest release](https://github.com/fpgawars/apio/releases) download the installer file:

        apio-windows-amd64-[date]-installer.exe

2.  Right click on the installer file, select `properties`, check the `Unblock` checkbox and press OK. This will
    allow you to run the unsigned installer.

3.  **After enabling the installer for execution** in the previous step, double click on it and follow the installer wizard.

4.  In a **new command window**, run the following command to test your installation:

        apio

<br>

### Install using a file bundle <a id="windows-x86-64-bundle"></a>

To install Apio CLI on Windows X86-64 using a file bundle, follow these steps:

1.  From the [latest release](https://github.com/fpgawars/apio/releases) download the file bundle:

        apio-windows-amd64-[date]-bundle.zip

2.  Right click on the bundle file , select `properties`, check the `Unblock` checkbox and press OK. This will
    allow you to run the the unsigned Apio app.

3.  Uncompress the bundle to reveal the `apio` directory with the application files.

4.  While in the `apio` directory, run the following command to test your installation (this will run `apio.exe`):

        .\apio

5.  Move the `apio` directory to a location of your choosing and add it to your `%PATH%`.

<br>

### Install using a Pip package <a id="windows-x86-64-pip"></a>

To install Apio CLI on Windows X86-64 using a Pip package, follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall -U git+https://github.com/fpgawars/apio.git@main

3.  In a **new command window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.
