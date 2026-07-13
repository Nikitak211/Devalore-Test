#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 cad/fidget_tank.py
python3 - <<'PY'
import json
b = json.load(open("docs/bom/fidget_tank_bom.json"))
assert len(b["bom"]) == 13
assert b["quantity_totals"]["total_printed_parts"] == sum(x["quantity"] for x in b["bom"])
assert next(x for x in b["bom"] if x["component_id"] == "10")["material_override"] == "PETG"
s = json.load(open("docs/assembly/state_machine.json"))
assert len(s["steps"]) == 7
print("validate_all: PASS")
PY
