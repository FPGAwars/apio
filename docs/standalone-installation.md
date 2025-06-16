# Standalone Apio Installation

Apio can be installed as a Pip package that relies on a Python installation, or standalone, using packages, installers, and file bundles that contain all the files that are required. This page describes the standalone installations which do not require installation of Python.

Following are standalone installation methods by platform:

| Method         | Mac OS X | Linux | Windows | Description                |
| :------------- | :------: | :---: | :-----: | :------------------------- |
| Installer      |    ✓     |       |    ✓    | Executable installer       |
| Debian package |          |   ✓   |         | For `apt` package manager. |
| File bundle    |    ✓     |   ✓   |    ✓    | Plain Zip archive          |

---

## Mac OS X (Apple Silicon)

### Install using an installer

1. Download the installer file **apio-darwin-arm64-[version]-[date]-installer.pkg** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Run the command below to allow the unsigned installer to run.

```
xattr -d com.apple.quarantine apio-darwin-arm64-*-installer.pkg
```

3. Double-click on the installer file and follow the instructions.

4. Open a **new shell** window and type `apio system info` to test your installation.

### Uninstall an installer

1. Delete the `apio` application from `Applications`.

2. Delete the Apio settings directory `.apio` under your home directory.

### Install using a file bundle

1. Download the bundle file **apio-darwin-arm64-[version]-[date]-bundle.tgz** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file. This will create an `apio` directory with the application files.

3. Run the command below to activate the environment.

```
source ./activate
```

4. [Optional] Move the `apio` directory to a location of your choosing.

5. Add the `apio` directory to your `$PATH`.

6. Open a new shell and run `apio` to test the installation.

### Uninstall a file bundle

1. Remove the `apio` directory from your `$PATH`.

2. Delete the `apio` directory.

3. Delete the Apio settings directory `.apio` under your home directory.

---

## Linux (X86 64 bit)

### Install a Debian package

1. Download the Debian package file **apio-linux-x86-64-[version]-[date]-debian.deb** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Run the following shell command in the directory where you downloaded the Debian package (replace `[version]` and `[date]` with the actual values):

```
sudo apt install ./apio-linux-x86-64-[version]-[date]-debian.deb
```

3. Open a **new shell** and run `apio` to test the installation.

### Uninstall a Debian package

1. Run the following command to uninstall the Debian package:

```
sudo apt remove apio
```

2. Delete the Apio settings directory `.apio` under your home directory.

### Install a file bundle

1. Download the bundle file **apio-linux-x86-64-[version]-[date]-bundle.tgz** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file. This will create an `apio` directory with the application files.

3. [Optional] Move the `apio` directory to a location of your choosing.

4. Add the `apio` directory to your `$PATH`.

5. Open a new shell and run `apio` to test the installation.

### Uninstall a file bundle

1. Remove the `apio` directory from your `$PATH`.

2. Delete the `apio` directory.

3. Delete the Apio settings directory `.apio` under your home directory.

---

## Windows (X86 64 bit)

### Install using an installer

1. Download the installer file **apio-windows-amd64-[version]-[date]-installer.exe** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Double-click on the installer and follow the instructions. If your system complains that the installer is not signed, click **More Info** and then **Run Anyway**.

3. Run `apio` in a new shell to test the installation.

### Uninstall an installer

1. Remove the `apio` application in Windows's `Add or remove programs` settings.

2. Delete the Apio settings directory `.apio` under your home directory.

### Install a file bundle

1. Download the bundle file **apio-windows-amd64-[version]-[date]-bundle.zip** from the [latest release](https://github.com/FPGAwars/apio-dev-builds/releases).

2. Uncompress the bundle file. This will create an `apio` directory with the application files.

3. [Optional] Move the `apio` directory to a location of your choosing.

4. Add the `apio` directory to your `%PATH%`.

5. Open a new command window and run `apio` to test the installation.

### Uninstall a file bundle

1. Remove the `apio` directory from your `%PATH%`.

2. Delete the `apio` directory.

3. Delete the Apio settings directory `.apio` under your home directory.
