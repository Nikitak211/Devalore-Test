#!/usr/bin/env python3
"""Kinematics & Assembly Sub-Agent — sequential validation graphs + tolerances."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


class KinematicsAssemblySubAgent:
    """Build ordered assembly dependency graphs and tolerance test scripts."""

    def build_validation_tree(
        self, bom: dict[str, Any], brief: str
    ) -> dict[str, Any]:
        components = bom.get("components", [])
        steps = bom.get("assembly_steps", [])

        nodes = [
            {
                "node_id": c["component_id"],
                "name": c["name"],
                "quantity": c["quantity"],
                "tolerance_critical": c.get("manufacturing", {}).get(
                    "requires_tolerance_tuning", False
                ),
            }
            for c in components
        ]

        edges: list[dict[str, str]] = []
        for step in steps:
            prereqs = step.get("prerequisite_components", [])
            for i in range(len(prereqs) - 1):
                edges.append(
                    {
                        "from": prereqs[i],
                        "to": prereqs[i + 1],
                        "via_step": str(step.get("step_number")),
                    }
                )

        return {
            "assembly_validation_tree": "sequential_dependency_graph",
            "generated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "orchestrator_version": "Sol-5.6-Max-PyOrch",
            "nodes": nodes,
            "edges": edges,
            "steps": steps,
            "brief_fingerprint_chars": len(brief),
        }

    def link_prerequisites(self, bom: dict[str, Any]) -> dict[str, Any]:
        """Populate assembly_steps[].prerequisite_components via name mentions."""
        name_to_id = {
            c["name"].lower(): c["component_id"] for c in bom.get("components", [])
        }
        for step in bom.get("assembly_steps", []):
            instruction = step.get("instruction", "").lower()
            found: list[str] = []
            for name, cid in sorted(name_to_id.items(), key=lambda x: -len(x[0])):
                # Soft match: allow plural/singular drift by stripping trailing s
                variants = {name, name.rstrip("s"), name + "s"}
                direct_hit = any(v and v in instruction for v in variants)
                tokens = [t for t in re.split(r"\W+", name) if len(t) > 3]
                token_hit = bool(tokens) and sum(
                    1 for t in tokens if t in instruction
                ) >= max(1, len(tokens) // 2)
                if direct_hit or token_hit:
                    if cid not in found:
                        found.append(cid)
            step["prerequisite_components"] = found
        return bom

    def generate_tolerance_script(self, bom: dict[str, Any]) -> str:
        critical = [
            c
            for c in bom.get("components", [])
            if c.get("manufacturing", {}).get("requires_tolerance_tuning")
        ]
        lines = [
            "#!/usr/bin/env python3",
            '"""Generated CadQuery/parameter tolerance evaluation scaffold.',
            "",
            "Produced by Kinematics & Assembly Sub-Agent (Sol 5.6 Max).",
            "Evaluates hole compensation for tolerance-critical BOM parts.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "# Nominal FDM hole compensation (mm) — tune per printer family",
            "HOLE_COMPENSATION_MM = 0.15",
            "",
            "TOLERANCE_CRITICAL_PARTS = [",
        ]
        for part in critical:
            lines.append(
                "    {"
                f'"component_id": "{part["component_id"]}", '
                f'"name": "{part["name"]}", '
                f'"qty": {part["quantity"]}, '
                f'"material": "{part["manufacturing"]["material_hint"]}", '
                f'"profile": "{part["manufacturing"]["mechanical_profile"]}"'
                "},"
            )
        lines.extend(
            [
                "]",
                "",
                "",
                "def evaluate_pin_hole_pair(pin_od_mm: float, hole_id_mm: float) -> dict:",
                '    """Return clearance after applying hole compensation."""',
                "    compensated_hole = hole_id_mm + HOLE_COMPENSATION_MM",
                "    clearance = compensated_hole - pin_od_mm",
                "    return {",
                '        "pin_od_mm": pin_od_mm,',
                '        "hole_id_mm": hole_id_mm,',
                '        "compensated_hole_mm": compensated_hole,',
                '        "clearance_mm": round(clearance, 4),',
                '        "fit": (',
                '            "press" if clearance < 0.05 else',
                '            "slip" if clearance < 0.25 else',
                '            "loose"',
                "        ),",
                "    }",
                "",
                "",
                "def report() -> None:",
                '    print(f"Tolerance-critical parts: {len(TOLERANCE_CRITICAL_PARTS)}")',
                "    for part in TOLERANCE_CRITICAL_PARTS:",
                '        print(f"  - {part[\'component_id\']}: {part[\'name\']} "',
                "              f\"({part['profile']}, {part['material']})\")",
                "    sample = evaluate_pin_hole_pair(pin_od_mm=5.0, hole_id_mm=5.0)",
                '    print(f"Sample pin/hole evaluation: {sample}")',
                "",
                "",
                'if __name__ == "__main__":',
                "    report()",
                "",
            ]
        )
        return "\n".join(lines)
