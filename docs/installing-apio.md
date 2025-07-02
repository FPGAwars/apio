Installing Apio
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

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `$PATH` if necessary.

### Install using an installer <a id="mac-arm64-installer"></a>

To install Apio on macOS Apple Silicon using an installer,
follow these steps:

1. Download the installer file **apio-darwin-arm64-[version]-[date]-installer.pkg** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Use the following command to allow the unsigned installer to run:

   ```
   xattr -d com.apple.quarantine apio-darwin-arm64-*-installer.pkg
   ```

3. Double-click the installer file and follow the instructions.

4. Open a **new shell** window and run:

   ```
   apio system info
   ```

   to verify your installation.

### Install using a file bundle <a id="mac-arm64-bundle"></a>

To install Apio on macOS Apple Silicon using a file bundle,
follow these steps:

1. Download the bundle file **apio-darwin-arm64-[version]-[date]-bundle.tgz** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file to create an `apio` directory with the application files.

3. Use the following command to activate the environment:

   ```
   source ./activate
   ```

4. [Optional] Move the `apio` directory to a location of your choosing.

5. [Optional] Add the `apio` directory to your `$PATH`.

6. Open a **new shell** and run:

   ```
   apio
   ```

   to test the installation.

---

## macOS Intel Silicon

### Install using a Pip package <a id="mac-x86-pip"></a>

To install Apio on macOS Intel Silicon using a Pip package, follow these steps:

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `$PATH` if necessary.

---

## Linux X86-64

To install Apio on Linux X86-64 using a Pip package, follow these steps:

### Install using a Pip package <a id="linux-x86-pip"></a>

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `$PATH` if necessary.

### Install a Debian package <a id="linux-x86-debian"></a>

To install Apio on Linux X86-64 using a Debian package, follow these steps:

1. Download the Debian package file **apio-linux-x86-64-[version]-[date]-debian.deb** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. In the directory where you downloaded the package, install it using:

   ```
   sudo apt install ./apio-linux-x86-64-[version]-[date]-debian.deb
   ```

3. Open a **new shell** and run:

   ```
   apio
   ```

   to verify the installation.

### Install using a file bundle <a id="linux-x86-bundle"></a>

To install Apio on Linux X86-64 using a file bundle, follow these steps:

1. Download the bundle file **apio-linux-x86-64-[version]-[date]-bundle.tgz** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file to create an `apio` directory with the application files.

3. [Optional] Move the `apio` directory to a location of your choosing.

4. [Optional] Add the `apio` directory to your `$PATH`.

5. Open a **new shell** and run:

   ```
   apio
   ```

   to test the installation.

---

## Linux ARM-64

To install Apio on Linux ARM-64 using a Pip package, follow these steps:

### Install using a Pip package <a id="linux-arm64-pip"></a>

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `$PATH` if necessary.

---

## Windows X86-64

To install Apio on Windows X86-64 using a Pip package, follow these steps:

### Install using a Pip package <a id="windows-pip"></a>

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `%PATH%` if necessary.

### Install using an installer <a id="windows-installer"></a>

To install Apio on Windows X86-64 using an installer, follow these steps:

1. Download the installer file **apio-windows-amd64-[version]-[date]-installer.exe** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Double-click the installer and follow the instructions. If your system warns that the installer is not signed, click **More Info** and then **Run Anyway**.

3. Open a new shell and run:

   ```
   apio
   ```

   to verify the installation.

### Install using a file bundle <a id="windows-bundle"></a>

To install Apio on Windows X86-64 using a file bundle, follow these steps:

1. Download the bundle file **apio-windows-amd64-[version]-[date]-bundle.zip** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file to create an `apio` directory with the application files.

3. [Optional] Move the `apio` directory to a location of your choosing.

4. [Optional] Add the `apio` directory to your `%PATH%`.

5. Open a **new command window** and run:

   ```
   apio
   ```

   to test the installation.
