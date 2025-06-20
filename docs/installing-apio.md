# Standalone Apio Installation

Apio can be installed in a few ways:

- **Pip Package** - Apio is installed as a Python pip package. This requires having Python installed on your system. Available for macOS, Linux, and Windows.

- **Installer** - This is a standalone installer that goes through a wizard and installs all the necessary files. Available for macOS (.pkg) and Windows (.exe).

- **Debian Package** - A standalone Linux Debian package that is installed using `apt` and contains all the necessary files. Available for Linux.

- **File Bundle** - This is a standalone file archive that, when uncompressed, contains all the necessary files. Available for macOS, Linux, and Windows.

To install Apio, select your platform and preferred installation method from the Table of Contents in the sidebar.
If the sidebar is not visible, scroll down to find the installation guide for your platform.

---

## macOS (Apple Silicon)

### Install using a Pip package <a id="mac-pip"></a>

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `$PATH` if necessary.

### Install using an installer <a id="mac-installer"></a>

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

### Install using a file bundle <a id="mac-bundle"></a>

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

## Linux (x86_64)

### Install using a Pip package <a id="linux-pip"></a>

1. Verify that you have Python installed by running:

   ```
   python --version
   ```

2. Install Apio using pip:

   ```
   pip install --force-reinstall apio
   ```

3. [Optional] Add the Apio binary to your `$PATH` if necessary.

### Install a Debian package <a id="linux-debian"></a>

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

### Install using a file bundle <a id="linux-bundle"></a>

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

## Windows (x86_64)

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

1. Download the installer file **apio-windows-amd64-[version]-[date]-installer.exe** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Double-click the installer and follow the instructions. If your system warns that the installer is not signed, click **More Info** and then **Run Anyway**.

3. Open a new shell and run:

   ```
   apio
   ```

   to verify the installation.

### Install using a file bundle <a id="windows-bundle"></a>

1. Download the bundle file **apio-windows-amd64-[version]-[date]-bundle.zip** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file to create an `apio` directory with the application files.

3. [Optional] Move the `apio` directory to a location of your choosing.

4. [Optional] Add the `apio` directory to your `%PATH%`.

5. Open a **new command window** and run:

   ```
   apio
   ```

   to test the installation.
