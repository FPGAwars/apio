"""A python script to recompile the Apio .proto files."""

# -- DO NOT run this script directly, run 'invoke update-protos' (or 'inv up'
# -- in short) from anywhere within this repo.

import subprocess
import sys
import re
from pathlib import Path

# -- The version of the python module grpcio-tools to use.
PROTO_COMPILER_VERSION = "1.76.0"

# -- The dirs involved.
PROTO_DIR = Path("apio/common/proto")
SRC_DIR = PROTO_DIR / "src"
STUBS_DIR = PROTO_DIR / "stubs"

# -- A regex for apio imports.
APIO_IMPORT_RE = re.compile(r"import apio_\S+_pb2 as [_]?apio_\S+_pb2")


def main() -> None:
    """Program main function."""

    # -- Verify that we are run at the correct directory.
    if not Path("pyproject.toml").exists():
        print("update_protos.py expects to run it repo top dir.")
        print(Path.cwd())
        sys.exit(1)

    # -- Install the proto compiler if not installed.
    print(f"Installing the proto compiler {PROTO_COMPILER_VERSION}")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            f"grpcio-tools=={PROTO_COMPILER_VERSION}",
        ]
    )

    # pylint: disable=import-error
    # pylint: disable=import-outside-toplevel
    from grpc_tools import protoc

    # -- Remove old stubs
    for path in STUBS_DIR.glob("*_pb2.py"):
        path.unlink()

    for path in STUBS_DIR.glob("*_pb2.pyi"):
        path.unlink()

    # -- Compile the .proto files
    print("\nCompiling source:")

    proto_files = sorted(SRC_DIR.glob("*.proto"))

    for f in proto_files:
        print(f"- {str(f)}")
        args = [
            "grpc_tools.protoc",
            f"--proto_path={SRC_DIR}",
            f"--python_out={STUBS_DIR}",
            f"--pyi_out={STUBS_DIR}",
            str(f),
        ]
        exit_code = protoc.main(args)
        if exit_code != 0:
            print("Error.")
            sys.exit(1)

    # -- Patch the generated stubs.
    print("\nPatching stubs:")
    for f in sorted(STUBS_DIR.glob("*_pb2.py*")):
        print(f"- {str(f)}")
        in_lines = f.read_text().splitlines()
        # print("  Disable pylint patch")
        out_lines = [
            "# *** Apio patched line:",
            "# pylint: disable=all",
            "",
        ]
        for line in in_lines:
            if APIO_IMPORT_RE.search(line):
                out_lines.extend(
                    [
                        "# *** Apio patched line:",
                        "from . " + line,
                    ]
                )
                print("  * APIO_IMPORT_RE patch")
            else:
                out_lines.append(line)
        f.write_text("\n".join(out_lines) + "\n")

    # -- All done OK.
    print("\nDone OK")


if __name__ == "__main__":
    main()
