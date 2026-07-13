#!/usr/bin/env python3
"""Master Router / Orchestrator for Sol 5.6 Max multi-agent pipeline.

Programmatically routes text-based engineering briefs through specialized
sub-agent execution loops and consolidates outputs into the decoupled
3d_project file-system architecture.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ingestion_engine import IngestionSubAgent
from dfm_engine import DFMSlicingSubAgent
from kinematics_engine import KinematicsAssemblySubAgent


class MasterOrchestrator:
    """Decoupled multi-agent manufacturing router."""

    def __init__(self, workspace_dir: str | None = None) -> None:
        self.workspace = Path(
            workspace_dir
            if workspace_dir is not None
            else Path(__file__).resolve().parent
        )
        self.dirs = [
            "specs",
            "agents",
            "outputs/code",
            "outputs/config",
            "briefs",
        ]
        self._init_workspace()
        self.ingestion = IngestionSubAgent()
        self.dfm = DFMSlicingSubAgent()
        self.kinematics = KinematicsAssemblySubAgent()

    def _init_workspace(self) -> None:
        for folder in self.dirs:
            os.makedirs(self.workspace / folder, exist_ok=True)

    def route_to_sub_agents(
        self,
        engineering_brief_path: str | Path,
        project_name: str = "Dynamic 3D Mechanical Assembly",
    ) -> dict[str, Any]:
        brief_path = Path(engineering_brief_path)
        with open(brief_path, "r", encoding="utf-8") as handle:
            brief_content = handle.read()

        print("[Orchestrator] Ingesting text brief...")
        print(f"[Orchestrator] Source: {brief_path}")

        # Step 1: Ingestion & BOM Agent
        bom = self._run_ingestion_agent(brief_content, project_name)

        # Step 2: DFM Slicing Agent
        slicing_profiles = self._run_dfm_agent(bom)

        # Step 3: Kinematics & Assembly Agent
        assembly_logic = self._run_kinematics_agent(bom, brief_content)

        # Link prerequisite component IDs onto assembly steps
        bom = self.kinematics.link_prerequisites(bom)

        self._consolidate_outputs(bom, slicing_profiles, assembly_logic)

        return {
            "bom": bom,
            "slicing_profiles": slicing_profiles,
            "assembly_logic": assembly_logic,
        }

    def _run_ingestion_agent(
        self, brief: str, project_name: str
    ) -> dict[str, Any]:
        print("[Sub-Agent] Activating Ingestion & BOM Agent...")
        bom = self.ingestion.parse_text_brief(brief, project_name=project_name)
        print(
            f"[Sub-Agent] Extracted {len(bom['components'])} components, "
            f"{len(bom['assembly_steps'])} assembly steps."
        )
        return bom

    def _run_dfm_agent(self, bom: dict[str, Any]) -> dict[str, Any]:
        print("[Sub-Agent] Activating DFM Slicing Agent...")
        profiles = self.dfm.generate_profiles(bom)
        print(
            f"[Sub-Agent] Generated {len(profiles.get('profiles', []))} "
            "slicing profiles."
        )
        return profiles

    def _run_kinematics_agent(
        self, bom: dict[str, Any], brief: str
    ) -> dict[str, Any]:
        print("[Sub-Agent] Activating Kinematics & Assembly Agent...")
        assembly = self.kinematics.build_validation_tree(bom, brief)
        print(
            f"[Sub-Agent] Built assembly graph with "
            f"{len(assembly.get('nodes', []))} nodes."
        )
        return assembly

    def _consolidate_outputs(
        self,
        bom: dict[str, Any],
        slicing: dict[str, Any],
        assembly: dict[str, Any],
    ) -> None:
        bom_path = self.workspace / "specs" / "bom.json"
        slicing_path = self.workspace / "outputs" / "config" / "slicing_meta.json"
        assembly_path = self.workspace / "outputs" / "config" / "assembly_logic.json"
        tolerance_path = self.workspace / "outputs" / "code" / "tolerance_test.py"

        with open(bom_path, "w", encoding="utf-8") as handle:
            json.dump(bom, handle, indent=2)
            handle.write("\n")

        with open(slicing_path, "w", encoding="utf-8") as handle:
            json.dump(slicing, handle, indent=2)
            handle.write("\n")

        with open(assembly_path, "w", encoding="utf-8") as handle:
            json.dump(assembly, handle, indent=2)
            handle.write("\n")

        tolerance_script = self.kinematics.generate_tolerance_script(bom)
        with open(tolerance_path, "w", encoding="utf-8") as handle:
            handle.write(tolerance_script)

        report = {
            "consolidated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "component_count": len(bom.get("components", [])),
            "assembly_step_count": len(bom.get("assembly_steps", [])),
            "slicing_profile_count": len(slicing.get("profiles", [])),
            "tolerance_critical_ids": [
                c["component_id"]
                for c in bom.get("components", [])
                if c.get("manufacturing", {}).get("requires_tolerance_tuning")
            ],
            "artifacts": {
                "bom": str(bom_path.relative_to(self.workspace)),
                "slicing_meta": str(slicing_path.relative_to(self.workspace)),
                "assembly_logic": str(assembly_path.relative_to(self.workspace)),
                "tolerance_test": str(tolerance_path.relative_to(self.workspace)),
            },
        }
        report_path = self.workspace / "specs" / "consolidation_report.json"
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")

        print(f"[Orchestrator] Project structured successfully inside: {self.workspace}")
        print(f"[Orchestrator] BOM written to: {bom_path}")
        print(f"[Orchestrator] Slicing meta written to: {slicing_path}")
        print(f"[Orchestrator] Tolerance script written to: {tolerance_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sol 5.6 Max Master Orchestrator — route engineering briefs."
    )
    parser.add_argument(
        "brief",
        nargs="?",
        default=None,
        help="Path to engineering brief text file (default: briefs/sample_brief.txt)",
    )
    parser.add_argument(
        "--project-name",
        default="Dynamic 3D Mechanical Assembly",
        help="Project name stored in BOM metadata",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Override workspace root (defaults to this script's directory)",
    )
    args = parser.parse_args(argv)

    orch = MasterOrchestrator(workspace_dir=args.workspace)
    brief = args.brief
    if brief is None:
        brief = str(orch.workspace / "briefs" / "sample_brief.txt")

    if not Path(brief).exists():
        print(f"[Orchestrator] ERROR: brief not found: {brief}", file=sys.stderr)
        return 1

    orch.route_to_sub_agents(brief, project_name=args.project_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
