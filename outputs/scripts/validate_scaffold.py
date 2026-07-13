#!/usr/bin/env python3
"""Validate that the Sol 5.6 Max orchestrator scaffold is complete and consistent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    ROOT / ".cursorrules",
    ROOT / "agents" / "ingestion.md",
    ROOT / "agents" / "dfm-slicing.md",
    ROOT / "agents" / "kinematics-assembly.md",
    ROOT / "agents" / "GLOBAL_EXECUTION_PROMPT.md",
    ROOT / "specs" / "schemas" / "bom.schema.json",
    ROOT / "specs" / "schemas" / "slicing-profile.schema.json",
    ROOT / "specs" / "schemas" / "assembly-state-machine.schema.json",
    ROOT / "specs" / "schemas" / "dependency-graph.schema.json",
    ROOT / "specs" / "bom" / "_template_bom.json",
    ROOT / "specs" / "manifests" / "_template_manifest.json",
    ROOT / "specs" / "dependencies" / "_template_graph.json",
    ROOT / "specs" / "dfm" / "_template_stress_map.json",
    ROOT / "outputs" / "slicing" / "_template_profiles.json",
    ROOT / "outputs" / "assembly" / "_template_state_machine.json",
    ROOT / "outputs" / "tolerance" / "_template_hole_compensation.py",
    # Production Python orchestrator (3d_project)
    ROOT / "3d_project" / "orchestrator.py",
    ROOT / "3d_project" / "ingestion_engine.py",
    ROOT / "3d_project" / "dfm_slicing_engine.py",
    ROOT / "3d_project" / "dfm_engine.py",
    ROOT / "3d_project" / "kinematics_engine.py",
    ROOT / "3d_project" / "agents" / "ingestion.prompt",
    ROOT / "3d_project" / "agents" / "dfm_slicing.prompt",
    ROOT / "3d_project" / "agents" / "kinematics.prompt",
    ROOT / "3d_project" / "specs" / "bom.schema.json",
    ROOT / "3d_project" / "briefs" / "sample_brief.txt",
    ROOT / "3d_project" / "outputs" / "code" / "tolerance_test.py",
]

AGENT_MARKERS = {
    ROOT / "agents" / "ingestion.md": "Ingestion Sub-Agent",
    ROOT / "agents" / "dfm-slicing.md": "DFM Slicing Sub-Agent",
    ROOT / "agents" / "kinematics-assembly.md": "Kinematics & Assembly Sub-Agent",
}


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_PATHS:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")

    cursorrules = ROOT / ".cursorrules"
    if cursorrules.exists():
        text = cursorrules.read_text(encoding="utf-8")
        for needle in (
            "Multi-Agent Orchestrator",
            "DIRECTORY OPERATIONS CONSTRAINTS",
            "SUB-AGENT PIPELINE SEQUENCE",
            "/specs",
            "/agents",
            "/outputs",
            "3d_project",
            "CONSOLIDATION",
        ):
            if needle not in text:
                errors.append(f".cursorrules missing marker: {needle}")

    for path, marker in AGENT_MARKERS.items():
        if path.exists() and marker not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)} missing role marker: {marker}")

    for schema in (ROOT / "specs" / "schemas").glob("*.json"):
        try:
            data = json.loads(schema.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {schema.name}: {exc}")
            continue
        if "$schema" not in data and "title" not in data:
            errors.append(f"schema lacks title/$schema: {schema.name}")

    for template in [
        ROOT / "specs" / "bom" / "_template_bom.json",
        ROOT / "outputs" / "slicing" / "_template_profiles.json",
        ROOT / "outputs" / "assembly" / "_template_state_machine.json",
    ]:
        if template.exists():
            try:
                json.loads(template.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid template JSON {template.name}: {exc}")

    if errors:
        print("scaffold validation FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"scaffold OK ({len(REQUIRED_PATHS)} required paths present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
