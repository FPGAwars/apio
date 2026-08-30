"""
Tests of apio_definitions.py
"""

from pytest import raises
from google.protobuf.json_format import MessageToDict
from tests.conftest import ApioRunner
from apio.utils import proto_util
from apio.common.proto.apio_definitions_pb2 import FpgaDefinition
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


def test_default_loading_no_project(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with no project."""

    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        assert not apio_ctx.has_project
        assert "alhambra-ii" in apio_ctx.definitions.boards
        assert "ice40hx4k-tq144-8k" in apio_ctx.definitions.fpgas
        assert "openfpgaloader" in apio_ctx.definitions.programmers


def test_default_loading_with_project(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with a project and
    without project's custom definition."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        assert apio_ctx.has_project
        assert "alhambra-ii" in apio_ctx.definitions.boards
        assert "ice40hx4k-tq144-8k" in apio_ctx.definitions.fpgas
        assert "openfpgaloader" in apio_ctx.definitions.programmers


def test_loading_with_custom_boards(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with a with project's
    custom boards definitions.
    """

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write fake custom boards
        board_definition1 = {
            "description": "My Custom Alhambra II",
            "fpga-id": "ice40hx4k-tq144-8k",
            "programmer": {
                "id": "openfpgaloader",
            },
            "usb": {
                "vid": "0403",
                "pid": "6010",
            },
        }

        board_definition2 = {
            "description": "My new board",
            "fpga-id": "lfe5u-45f-6bg381c",
            "programmer": {
                "id": "openfpgaloader",
            },
        }

        sb.write_json_file(
            "boards.jsonc",
            {
                # -- Overrides a standard definition
                "alhambra-ii": board_definition1,
                # -- Adds a new definition
                "my-custom-board": board_definition2,
            },
        )

        # -- Load
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Verify
        definitions = apio_ctx.definitions

        assert apio_ctx.has_project
        assert "ice40hx4k-tq144-8k" in definitions.fpgas
        assert "openfpgaloader" in definitions.programmers

        assert (
            MessageToDict(definitions.boards["alhambra-ii"])
            == board_definition1
        )
        assert (
            MessageToDict(definitions.boards["my-custom-board"])
            == board_definition2
        )

        assert definitions.is_custom_board("alhambra-ii")
        assert definitions.is_custom_board("my-custom-board")
        assert not definitions.is_custom_board("sipeed-tang-nano-9k")


def test_loading_with_custom_fpgas(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with a with project's
    custom fpgas definitions.
    """

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write fake custom boards
        fpga_json1 = {
            "part-num": "ICE40HX4K-TQ144",
            "arch": "ice40",
            "size": "99k",  # Overriding 8k
            "ice40-params": {"type": "hx8k", "package": "tq144:4k"},
        }

        fpga_json2 = {
            "part-num": "MY-CUSTOM-FPGA",
            "arch": "ice40",
            "size": "4k",
            "ice40-params": {"type": "hx4k", "package": "bg121"},
        }

        sb.write_json_file(
            "fpgas.jsonc",
            {
                # -- Overrides a standard definition
                "ice40hx4k-tq144-8k": fpga_json1,
                # -- Adds a new definition
                "my-custom-fpga": fpga_json2,
            },
        )

        # -- Load
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Verify
        definitions = apio_ctx.definitions

        assert apio_ctx.has_project
        assert "alhambra-ii" in definitions.boards
        assert "openfpgaloader" in definitions.programmers

        # TODO: Use proto ascii literals instead of converting from json
        fpga_proto1 = proto_util.proto_from_json_dict(
            fpga_json1, FpgaDefinition, "Failed to parse fpga_json1"
        )
        fpga_proto2 = proto_util.proto_from_json_dict(
            fpga_json2, FpgaDefinition, "Failed to parse fpga_json2"
        )

        assert definitions.fpgas["ice40hx4k-tq144-8k"] == fpga_proto1
        assert definitions.fpgas["my-custom-fpga"] == fpga_proto2

        assert definitions.is_custom_fpga("ice40hx4k-tq144-8k")
        assert definitions.is_custom_fpga("my-custom-fpga")
        assert not definitions.is_custom_fpga("ice40lp1k-cm36")


def test_loading_with_custom_programmer(apio_runner: ApioRunner):
    """Tests loading of apio standard definitions with a with project's
    custom programmer definitions.
    """

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write fake custom programmers
        programmer_info1 = {
            "command": "custom-iceprog",
            "args": "-d d:${BUS}/${DEV}",
        }
        programmer_info2 = {"command": "iceprog", "args": "my custom args"}

        sb.write_json_file(
            "programmers.jsonc",
            {
                # -- Overrides a standard definition
                "iceprog": programmer_info1,
                # -- Adds a new definition
                "my-custom-programmer": programmer_info2,
            },
        )

        # -- Load
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Verify
        definitions = apio_ctx.definitions

        assert apio_ctx.has_project
        assert "alhambra-ii" in definitions.boards
        assert "ice40hx4k-tq144-8k" in definitions.fpgas

        assert definitions.programmers["iceprog"] == programmer_info1
        assert (
            definitions.programmers["my-custom-programmer"] == programmer_info2
        )

        assert definitions.is_custom_programmer("iceprog")
        assert definitions.is_custom_programmer("my-custom-programmer")
        assert not definitions.is_custom_programmer("openfpgaloader")


def test_loading_invalid_custom_board(apio_runner: ApioRunner):
    """Tests loading attempt of an invalid board custom definition."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write a custom definition file with an invalid definition
        # -- Missing description field.
        sb.write_json_file(
            "boards.jsonc",
            {
                "alhambra-ii": {
                    "fpga-id": "ice40hx4k-tq144-8k",
                    "programmer": {
                        "id": "openfpgaloader",
                    },
                    "usb": {
                        "vid": "0403",
                        "pid": "6010",
                    },
                }
            },
        )

        # -- Test
        with apio_runner.with_logger() as log:
            with raises(SystemExit) as e:
                _ = ApioContext(
                    project_policy=ProjectPolicy.PROJECT_REQUIRED,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )

        # -- Verify
        assert e.value.code == 1
        assert "Missing required field 'description'" in log.out


def test_loading_invalid_custom_fpga(apio_runner: ApioRunner):
    """Tests loading attempt of an invalid board custom definition."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write a custom definition file with an invalid definition
        # -- Missing part-num field.
        sb.write_json_file(
            "fpgas.jsonc",
            {
                "ice40lp384-cm36": {
                    "arch": "ice40",
                    "size": "384",
                    "ice40-params": {"type": "lp384", "package": "cm36"},
                }
            },
        )

        # -- Test
        with apio_runner.with_logger() as log:
            with raises(SystemExit) as e:
                _ = ApioContext(
                    project_policy=ProjectPolicy.PROJECT_REQUIRED,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )

        # -- Verify
        assert e.value.code == 1
        assert "Missing required field 'part-num'" in log.out


def test_loading_invalid_custom_programmer(apio_runner: ApioRunner):
    """Tests loading attempt of an invalid programmer custom definition."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write a custom definition file with an invalid definition
        # -- Missing command field.
        sb.write_json_file(
            "programmers.jsonc",
            {
                "openfpgaloader": {
                    "args": "--force-terminal-mode --verify",
                }
            },
        )

        # -- Test
        with apio_runner.with_logger() as log:
            with raises(SystemExit) as e:
                _ = ApioContext(
                    project_policy=ProjectPolicy.PROJECT_REQUIRED,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )

        # -- Verify
        assert e.value.code == 1
        assert "'command' is a required property" in log.out


def test_loading_invalid_custom_board_id(apio_runner: ApioRunner):
    """Tests loading attempt of an invalid board id."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write a custom definition file with an invalid definition
        # -- Missing description field.
        sb.write_json_file(
            "boards.jsonc",
            {
                "invalid-ID": {
                    "description": "BlackIce MX",
                    "fpga-id": "ice40hx4k-tq144-8k",
                    "programmer": {"id": "blackiceprog"},
                    "usb": {"vid": "0483", "pid": "5740"},
                }
            },
        )

        # -- Test
        with apio_runner.with_logger() as log:
            with raises(SystemExit) as e:
                _ = ApioContext(
                    project_policy=ProjectPolicy.PROJECT_REQUIRED,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )

        # -- Verify
        assert e.value.code == 1
        assert "Board id has an invalid format: invalid-ID" in log.out


def test_loading_invalid_custom_fpga_id(apio_runner: ApioRunner):
    """Tests loading attempt of an invalid fpga id."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write a custom definition file with an invalid definition
        # -- Missing description field.
        sb.write_json_file(
            "fpgas.jsonc",
            {
                "invalid-ID": {
                    "part-num": "ICE40LP1K-SWG16TR",
                    "arch": "ice40",
                    "size": "1k",
                    "ice40-params": {"type": "lp1k", "package": "swg16tr"},
                }
            },
        )

        # -- Test
        with apio_runner.with_logger() as log:

            with raises(SystemExit) as e:
                _ = ApioContext(
                    project_policy=ProjectPolicy.PROJECT_REQUIRED,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )

        # -- Verify
        assert e.value.code == 1
        assert "FPGA id has an invalid format: invalid-ID" in log.out


def test_loading_invalid_custom_programmer_id(apio_runner: ApioRunner):
    """Tests loading attempt of an invalid programmer id."""

    with apio_runner.in_sandbox() as sb:

        # -- Fake apio project file.
        sb.write_default_apio_ini()

        # -- Write a custom definition file with an invalid definition
        # -- Missing description field.
        sb.write_json_file(
            "programmers.jsonc",
            {
                "invalid-ID": {
                    "command": "openFPGALoader",
                    "args": "--force-terminal-mode --verify",
                }
            },
        )

        # -- Test
        with apio_runner.with_logger() as log:
            with raises(SystemExit) as e:
                _ = ApioContext(
                    project_policy=ProjectPolicy.PROJECT_REQUIRED,
                    remote_config_policy=RemoteConfigPolicy.CACHED_OK,
                    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
                )

        # -- Verify
        assert e.value.code == 1
        assert "Programmer id has an invalid format: invalid-ID" in log.out
