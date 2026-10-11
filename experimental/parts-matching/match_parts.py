import subprocess
from dataclasses import dataclass
import json
import copy


@dataclass(frozen=True)
class MatchResult:
    id1: str
    id2: str
    params_match: bool
    part_num_match: bool
    id_match: bool

    def classify(self) -> tuple[int, str]:
        if self.params_match and self.part_num_match and self.id_match:
            return (3, "identical")

        if self.params_match and self.part_num_match:
            return (2, "same")

        if self.params_match:
            return (1, "similar")

        return (0, "")

    def is_identical(self) -> bool:
        return self.classify()[0] == 3


def compare_definitions(
    id1: str, def1: dict, id2: str, def2: dict
) -> MatchResult:

    id_match = id1 == id2

    part_num_match = def1["part-num"] == def2["part-num"]

    a = copy.deepcopy(def1)
    b = copy.deepcopy(def2)
    # Normalize
    a.pop("part-num")
    b.pop("part-num")

    params_match = a == b

    return MatchResult(id1, id2, params_match, part_num_match, id_match)


result = subprocess.run(
    ["apio", "api", "get-parts-index", "-o", "_get_parts_index.json", "-f"],
    capture_output=True,
    text=True,
    check=True,
)

with open("_get_parts_index.json", encoding="utf-8") as f:
    parts_json = json.load(f)

# print(json.dumps(parts_json, indent=2))

result = subprocess.run(
    ["apio", "api", "get-fpgas", "-o", "_get_fpgas.json", "-f"],
    capture_output=True,
    text=True,
    check=True,
)

with open("_get_fpgas.json", encoding="utf-8") as f:
    fpgas_json = json.load(f)

# print(json.dumps(fpgas_json, indent=2))

missing_identical = []
for fpga_id, fpga_def in fpgas_json["fpgas"].items():
    print(f"\nFpga def: {fpga_id}")
    matches: list[MatchResult] = []
    for part_id, part_entry in parts_json["parts-index"].items():
        match_result = compare_definitions(
            fpga_id,
            fpga_def,
            part_id,
            part_entry["definition"],
        )
        if match_result.params_match:
            matches.append(match_result)

    # Sort
    matches = sorted(
        matches,
        key=lambda m: (-m.classify()[0], m.id2),
    )

    for m in matches:
        _, tag = m.classify()
        print(f"- [{tag:9}] index part: {m.id2}")

    if not any(m.is_identical() for m in matches):
        missing_identical.append(fpga_id)


if missing_identical:
    print("\n\nMissing identical:")
    for id in missing_identical:
        print(f"- fpga def: {id}")
