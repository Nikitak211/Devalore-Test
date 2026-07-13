#!/usr/bin/env python3
"""Production Ingestion Sub-Agent parsing engine (Sol 5.6 Max).

Robust regex extraction of quantities, component names, materials, and
mechanical notes from unstructured engineering text briefs into the
universal BOM schema written under specs/bom.json.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any


class IngestionSubAgent:
    """Parse unstructured engineering briefs into structured BOM JSON."""

    def __init__(self) -> None:
        # Captures patterns like: "4x drive pins", "12 structural clips", "1 main chassis"
        self.part_pattern = re.compile(
            r"(?P<qty>\d+)\s*(?:x|[-_ ]?pcs)?\s+(?P<name>[\w\s\-]+?)"
            r"(?:\s*[-–—,:]\s*|\s*\(|$|\n)",
            re.IGNORECASE,
        )
        self.materials = ["pla", "petg", "abs", "tpu", "nylon", "asa", "resin"]
        self.stress_keywords = {
            "load-bearing": [
                "axle",
                "gear",
                "pin",
                "shaft",
                "joint",
                "bearing",
                "mount",
            ],
            "compliant": [
                "clip",
                "latch",
                "spring",
                "snap",
                "leaf",
                "flex",
            ],
            "structural": [
                "chassis",
                "frame",
                "casing",
                "shell",
                "body",
                "housing",
            ],
        }
        self.step_pattern = re.compile(
            r"^(?:step|diy|phase)\s*\d+\s*[:.\-]?\s*(.+)$",
            re.IGNORECASE,
        )
        self.numbered_step_pattern = re.compile(r"^(\d+)[.)]\s+(.+)$")

    def parse_text_brief(
        self,
        raw_text: str,
        project_name: str = "Extracted Project Profile",
    ) -> dict[str, Any]:
        bom: dict[str, Any] = {
            "project_metadata": {
                "project_name": project_name,
                "timestamp": datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "orchestrator_version": "Sol-5.6-Max-PyOrch",
                "parser_version": "Sol-5.6-Max",
            },
            "components": [],
            "assembly_steps": [],
        }

        step_counter = 1
        seen_names: set[str] = set()

        for line in raw_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Skip section headers
            if re.match(
                r"^(print\s+requirements|assembly\s+index|parts|bom|"
                r"components|notes)\s*:?\s*$",
                line,
                re.IGNORECASE,
            ):
                continue

            step_match = self.step_pattern.match(line)
            numbered_match = self.numbered_step_pattern.match(line)
            if step_match or numbered_match:
                instruction = (
                    step_match.group(1).strip()
                    if step_match
                    else numbered_match.group(2).strip()  # type: ignore[union-attr]
                )
                # Prefer full original line when already phrased as Step N
                instruction_text = (
                    line if step_match else f"{numbered_match.group(1)}. {instruction}"  # type: ignore[union-attr]
                )
                bom["assembly_steps"].append(
                    {
                        "step_number": step_counter,
                        "instruction": instruction_text,
                        "prerequisite_components": [],
                    }
                )
                step_counter += 1
                continue

            match = self.part_pattern.search(line)
            if not match:
                continue

            extracted = match.groupdict()
            qty = int(extracted["qty"])
            name = extracted["name"].strip().lower()
            name = re.sub(r"\s+", " ", name).strip(" -_,")

            # Avoid duplicate component rows from repeated mentions
            if name in seen_names:
                continue
            seen_names.add(name)

            material = "PLA"
            profile = "cosmetic"
            line_lower = line.lower()

            for mat in self.materials:
                if mat in line_lower:
                    material = mat.upper()
                    break

            for prof, keywords in self.stress_keywords.items():
                if any(kw in name for kw in keywords):
                    profile = prof
                    break

            bom["components"].append(
                {
                    "component_id": f"COMP-{uuid.uuid4().hex[:6].upper()}",
                    "name": name,
                    "quantity": qty,
                    "raw_text_context": line,
                    "manufacturing": {
                        "material_hint": material,
                        "mechanical_profile": profile,
                        "requires_tolerance_tuning": profile
                        in ("load-bearing", "compliant"),
                    },
                }
            )

        return bom

    def write_bom(self, bom: dict[str, Any], output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(bom, handle, indent=2)
            handle.write("\n")


if __name__ == "__main__":
    sample_brief = """
    PRINT REQUIREMENTS:
    4x drive axle pins - print in high strength PETG
    1 main outer chassis casing - PLA standard
    12 snap clips (flexible tpu material)

    ASSEMBLY INDEX:
    Step 1: Press fit drive axle pins into the outer chassis casing.
    Step 2: Snap locking clips along outer body track lines.
    """

    parser = IngestionSubAgent()
    structured_json = parser.parse_text_brief(
        sample_brief,
        project_name="Dynamic 3D Mechanical Assembly",
    )
    print(json.dumps(structured_json, indent=2))
