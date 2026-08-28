"""A manager class for  to dispatch the Apio SCONS targets."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

from pathlib import Path
import json5
import json
from google.protobuf import text_format
from apio_definitions_pb2 import  BoardProgrammer, BoardUsb, BoardDefinition, Definitions
from google.protobuf import text_format
from google.protobuf.json_format import ParseDict

from google.protobuf.json_format import MessageToJson, MessageToDict

# --- Read apio boards.jsonc
boards_file_path = Path.home() / ".apio/packages/definitions/boards.jsonc"
boards_text = boards_file_path.read_text(encoding="utf-8")
boards_dict = json5.loads(boards_text)


# -- Parse individual boards
# for board_id, board_info in boards_dict.items():
#     print
#     print(board_id)
#     board_info = ParseDict(board_info, BoardInfo())

#     print(text_format.MessageToString(board_info))

#     print(
#         MessageToJson(
#             board_info,
#             indent=2,
#             ensure_ascii=False,
#             preserving_proto_field_name=True,
#         )
#     )

boards_proto = {}
for board_id, board_info_dict in boards_dict.items():
    board_info_msg = ParseDict(board_info_dict, BoardDefinition())
    boards_proto[board_id] = board_info_msg

# print(boards)

# ParseDict(boards_dict, Definitions())
# definitions = ParseDict({"boards": boards_dict}, Definitions())

definitions = Definitions(boards=boards_proto)

# print(text_format.MessageToString(definitions))

# print(
#         MessageToJson(
#             definitions,
#             indent=2,
#             ensure_ascii=False,
#             preserving_proto_field_name=False,
#         )
#     )

boards_json = MessageToDict(definitions)["boards"]

print(json.dumps(boards_json, indent=2))

assert boards_json == boards_dict





