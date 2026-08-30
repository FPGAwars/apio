"""
Tests of proto_util.py
"""

import pytest
from tests.conftest import ApioRunner
from apio.common.proto.apio_testing_pb2 import MessageB
from apio.utils.proto_util import (
    proto_from_json_dict,
    proto_to_json_dict,
)


def test_proto_from_dict_full(apio_runner: ApioRunner):
    """Test parsing of a proto from a json dict with all required and
    optional fields included."""

    with apio_runner.in_sandbox():

        json_dict1 = {
            "field-b1": {
                "field-a1": "aaa",
                "field-a2": "bbb",
            },
            "field-b2": {
                "field-a1": "ccc",
                "field-a2": "ddd",
            },
        }

        # -- Parse proto from json dict and verify
        proto_msg = proto_from_json_dict(
            json_dict1, MessageB, "Fail to parse test proto"
        )

        assert proto_msg.field_b1.field_a1 == "aaa"
        assert proto_msg.field_b1.field_a2 == "bbb"
        assert proto_msg.field_b2.field_a1 == "ccc"
        assert proto_msg.field_b2.field_a2 == "ddd"

        # -- Convert back to json dict and compare.
        json_dict2 = proto_to_json_dict(proto_msg)

        assert json_dict2 == json_dict1


def test_proto_from_dict_minimal(apio_runner: ApioRunner):
    """Test parsing of a proto from a json dict with only required
    fields included."""

    with apio_runner.in_sandbox():

        json_dict1 = {
            "field-b1": {
                "field-a1": "aaa",
            },
        }

        # -- Parse proto from json dict and verify
        proto_msg = proto_from_json_dict(
            json_dict1, MessageB, "Fail to parse test proto"
        )

        assert proto_msg.field_b1.field_a1 == "aaa"

        assert not proto_msg.HasField("field_b2")
        assert not proto_msg.field_b1.HasField("field_a2")

        # -- Convert back to json dict and compare.
        json_dict2 = proto_to_json_dict(proto_msg)

        assert json_dict2 == json_dict1


def test_proto_from_dict_missing_field(apio_runner: ApioRunner):
    """Test parsing of a proto from a json dict with a required
    field missing."""

    with apio_runner.in_sandbox():

        json_dict1 = {
            "field-b1": {
                # -- Required field 'field-a1' is missing.
                "field-a2": "aaa",
            },
        }

        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                _ = proto_from_json_dict(
                    json_dict1, MessageB, "Fail to parse test proto"
                )

        assert e.value.code == 1
        assert "Missing required field 'field-b1.field-a1'" in log.out


def test_proto_from_dict_unknown_field(apio_runner: ApioRunner):
    """Test parsing of a proto from a json dict with a an unknown field."""

    with apio_runner.in_sandbox():

        json_dict1 = {
            "field-b1": {"field-a1": "aaa", "no-such-field": "bbb"},
        }

        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                _ = proto_from_json_dict(
                    json_dict1, MessageB, "Fail to parse test proto"
                )

        print(log.out)

        assert e.value.code == 1
        assert "Unknown field 'no-such-field'" in log.out
