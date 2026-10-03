"""A python script to recompile the Apio .proto files."""

import subprocess
import sys
from pathlib import Path

# -- The version of the python module grpcio-tools to use.
PROTO_COMPILER_VERSION = "1.76.0"

# -- The path to the Apio proto root dir.
PROTO_DIR = Path("apio/common/proto")


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
    for path in PROTO_DIR.glob("*_pb2.py"):
        path.unlink()

    for path in PROTO_DIR.glob("*_pb2.pyi"):
        path.unlink()

    # -- Compile the .proto files
    print("\nCompiling source:")

    for f in sorted(PROTO_DIR.glob("*.proto")):
        print(f"- {str(f)}")
        args = [
            "grpc_tools.protoc",
            "-I.",
            "--python_out=.",
            "--pyi_out=.",
            str(f),
        ]
        exit_code = protoc.main(args)
        if exit_code != 0:
            print("Error.")
            sys.exit(1)

    # -- Patch the generated stubs.
    print("\nPatching stubs:")
    for f in sorted(PROTO_DIR.glob("*_pb2.py*")):
        print(f"- {str(f)}")
        lines = f.read_text().splitlines()
        lines = [
            "# pylint: disable=all",
            "",
        ] + lines
        f.write_text("\n".join(lines) + "\n")

    # -- All done OK.
    print("\nDone OK")


if __name__ == "__main__":
    main()
