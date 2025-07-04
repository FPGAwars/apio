Apio can be installed in a few ways:

| Method             | Description                                                   | Platforms             |
| :----------------- | :------------------------------------------------------------ | :-------------------- |
| **Pip package**    | Installed using Python `pip` command. Requires Python.        | macOS, Linux, Windows |
| **Installer**      | A standalone installation using an installer wizard.          | macOS, Windows        |
| **Debian package** | A standalone installation using the `apt` package manager.    | Linux                 |
| **File bundle**    | A standalone file archive with executables and support files. | macOS, Linux, Windows |

To install Apio, select your platform and preferred installation method from the Table of Contents in the sidebar.
If the sidebar is not visible, scroll down to find the installation guide for your platform.

---

## macOS Apple Silicon

### Install using a Pip package <a id="mac-arm64-pip"></a>

To install Apio on macOS Apple Silicon using a Pip package,
follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall apio

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

### Install using an installer <a id="mac-arm64-installer"></a>

To install Apio on macOS Apple Silicon using an installer, follow these steps:

1.  From the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases) download the installer file:

        apio-darwin-arm64-[version]-[date]-installer.pkg

2.  Run the following command to allow the unsigned Apio installer to run:

        xattr -d com.apple.quarantine apio-darwin-arm64-*-installer.pkg 2>&1 | grep -v "No such xattr"

3.  Double-click on the installer file and follow the instructions.

4.  In a **new shell window**, run the following command to test your installation:

        apio

> NOTE: The installer creates the file `/etc/paths.d/Apio` to export
> automatically the path of the installed app.

### Install using a file bundle <a id="mac-arm64-bundle"></a>

To install Apio on macOS Apple Silicon using a file bundle,
follow these steps:

1.  From the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases) download the file bundle:

        apio-darwin-arm64-[version]-[date]-bundle.tgz

2.  Run the following command to allow the unsigned Apio app to run.

        xattr -d com.apple.quarantine apio-darwin-arm64-*-bundle.tgz 2>&1 | grep -v "No such xattr"

3.  **After you run the xattr command**, double click on the bundle file to uncompress it and reveal the `apio` directory with the application files.

4.  While in the `apio` directory, run the following command to test your installation:

        ./apio

5.  Move the `apio` directory to a location of your choosing and add it to your `$PATH`.

---

## macOS Intel Silicon

### Install using a Pip package <a id="mac-x86-pip"></a>

To install Apio on macOS Intel Silicon using a Pip package, follow these steps:

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall apio

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

---

## Linux X86-64

To install Apio on Linux X86-64 using a Pip package, follow these steps:

### Install using a Pip package <a id="linux-x86-pip"></a>

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall apio

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

### Install a Debian package <a id="linux-x86-debian"></a>

To install Apio on Linux X86-64 using a Debian package, follow these steps:

1.  From the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases) download the Debian package file:

        apio-linux-x86-64-[version]-[date]-debian.deb

2.  In the directory where you downloaded the package, install it using:

        sudo dpkg -i ./apio-linux-x86-64-[version]-[date]-debian.deb

3.  In a **new shell window**, run the following command to test your installation:

        apio

### Install using a file bundle <a id="linux-x86-bundle"></a>

To install Apio on Linux X86-64 using a file bundle, follow these steps:

1.  From the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases) download the file bundle:

        apio-linux-x86-64-[version]-[date]-bundle.tgz

2.  Uncompress the bundle file to reveal the `apio` directory with the application files.

        tar -xzf apio-linux-x86-64-*-bundle.tgz

3.  While in the `apio` directory, run the following command to test your installation:

        ./apio

4.  Move the `apio` directory to a location of your choosing and add it to your `$PATH`.

---

## Linux ARM-64

To install Apio on Linux ARM-64 using a Pip package, follow these steps:

### Install using a Pip package <a id="linux-arm64-pip"></a>

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall apio

3.  In a **new shell window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

---

## Windows X86-64

To install Apio on Windows X86-64 using a Pip package, follow these steps:

### Install using a Pip package <a id="windows-x86-64-pip"></a>

1.  Verify that you have Python installed by running:

        python --version

2.  Install Apio using pip:

        pip install --force-reinstall apio

3.  In a **new command window**, run the following command to test your installation:

        apio

> If necessary, add the directory of the installed `apio` binary to your `$PATH`.

### Install using an installer <a id="windows-x86-64-installer"></a>

To install Apio on Windows X86-64 using an installer, follow these steps:

1.  From the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases) download the installer file:

        apio-windows-amd64-[version]-[date]-installer.exe

2.  Right click on the installer file, select `properties`, check the `Unblock` checkbox and press OK. This will
    allow you to run the unsigned installer.

3.  **After enabling the installer for execution** in the previous step, double click on it and follow the installer wizard.

4.  In a **new command window**, run the following command to test your installation:

        apio

### Install using a file bundle <a id="windows-x86-64-bundle"></a>

To install Apio on Windows X86-64 using a file bundle, follow these steps:

1.  From the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases) download the file bundle:

        apio-windows-amd64-[version]-[date]-bundle.zip

2.  Right click on the bundle file , select `properties`, check the `Unblock` checkbox and press OK. This will
    allow you to run the the unsigned Apio app.

3.  Uncompress the bundle to reveal the `apio` directory with the application files.

4.  While in the `apio` directory, run the following command to test your installation (this will run `apio.exe`):

        .\apio

5.  Move the `apio` directory to a location of your choosing and add it to your `%PATH%`.
