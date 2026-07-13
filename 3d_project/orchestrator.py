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
from dfm_slicing_engine import DFMSlicingAgent
from kinematics_engine import KinematicsAssemblySubAgent

# Tolerance validator lives under outputs/code/ per architecture contract
_CODE_DIR = Path(__file__).resolve().parent / "outputs" / "code"
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))
from tolerance_test import ToleranceValidator  # noqa: E402


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
        self.dfm = DFMSlicingAgent(workspace_dir=str(self.workspace))
        self.kinematics = KinematicsAssemblySubAgent()
        self.tolerance = ToleranceValidator(workspace_dir=str(self.workspace))

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

        # Persist BOM before DFM (file-system contract: DFM reads specs/bom.json)
        bom_path = self.workspace / "specs" / "bom.json"
        with open(bom_path, "w", encoding="utf-8") as handle:
            json.dump(bom, handle, indent=2)
            handle.write("\n")

        # Step 2: DFM Slicing Agent
        slicing_profiles = self._run_dfm_agent(bom)

        # Step 3: Kinematics & Assembly Agent
        bom = self.kinematics.link_prerequisites(bom)
        assembly_logic = self._run_kinematics_agent(bom, brief_content)

        # Re-write BOM with linked prerequisites
        with open(bom_path, "w", encoding="utf-8") as handle:
            json.dump(bom, handle, indent=2)
            handle.write("\n")

        # Step 4: Tolerance validation step-matrix
        tolerance_matrix = self._run_tolerance_validator(bom)

        self._consolidate_outputs(
            bom, slicing_profiles, assembly_logic, tolerance_matrix
        )

        return {
            "bom": bom,
            "slicing_profiles": slicing_profiles,
            "assembly_logic": assembly_logic,
            "tolerance_matrix": tolerance_matrix,
        }

    def run_dfm_and_tolerance_only(self) -> dict[str, Any]:
        """Verification path: process existing specs/bom.json without re-ingestion."""
        print("[Orchestrator] Running DFM + Tolerance against existing BOM...")
        slicing = self.dfm.process_bom_to_slicing_profiles()
        tolerance = self.tolerance.generate_parametric_clearance_matrix()
        return {"slicing_profiles": slicing, "tolerance_matrix": tolerance}

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
        profiles = self.dfm.process_bom_to_slicing_profiles(bom_data=bom)
        count = len(profiles.get("component_profiles", {}))
        print(f"[Sub-Agent] Generated {count} slicing profiles.")
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

    def _run_tolerance_validator(self, bom: dict[str, Any]) -> dict[str, Any]:
        print("[Sub-Agent] Activating Tolerance Validation Framework...")
        matrix = self.tolerance.generate_parametric_clearance_matrix(
            bom_data=bom, silent=False
        )
        print(
            f"[Sub-Agent] Tolerance matrix covers "
            f"{len(matrix.get('components', []))} critical parts."
        )
        return matrix

    def _consolidate_outputs(
        self,
        bom: dict[str, Any],
        slicing: dict[str, Any],
        assembly: dict[str, Any],
        tolerance: dict[str, Any],
    ) -> None:
        assembly_path = self.workspace / "outputs" / "config" / "assembly_logic.json"
        with open(assembly_path, "w", encoding="utf-8") as handle:
            json.dump(assembly, handle, indent=2)
            handle.write("\n")

        # Distinct wall/layer check for structural vs load-bearing
        walls: dict[str, int] = {}
        for cid, entry in slicing.get("component_profiles", {}).items():
            params = entry["print_parameters"]
            walls[params["mechanical_profile"]] = params["wall_loops"]
        distinct_walls = (
            walls.get("load-bearing") != walls.get("structural")
            if "load-bearing" in walls and "structural" in walls
            else None
        )

        report = {
            "consolidated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "component_count": len(bom.get("components", [])),
            "assembly_step_count": len(bom.get("assembly_steps", [])),
            "slicing_profile_count": len(slicing.get("component_profiles", {})),
            "tolerance_critical_count": len(tolerance.get("components", [])),
            "load_bearing_vs_structural_walls_distinct": distinct_walls,
            "wall_loops_by_profile": walls,
            "tolerance_critical_ids": [
                c["component_id"]
                for c in bom.get("components", [])
                if c.get("manufacturing", {}).get("requires_tolerance_tuning")
            ],
            "artifacts": {
                "bom": "specs/bom.json",
                "slicing_meta": "outputs/config/slicing_meta.json",
                "assembly_logic": "outputs/config/assembly_logic.json",
                "tolerance_matrix": "outputs/config/tolerance_matrix.json",
                "tolerance_test": "outputs/code/tolerance_test.py",
            },
        }
        report_path = self.workspace / "specs" / "consolidation_report.json"
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")

        print(f"[Orchestrator] Project structured successfully inside: {self.workspace}")
        print("[Orchestrator] Artifacts: specs/bom.json, outputs/config/slicing_meta.json,")
        print(
            "              outputs/config/tolerance_matrix.json, "
            "outputs/code/tolerance_test.py"
        )


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
    parser.add_argument(
        "--dfm-tolerance-only",
        action="store_true",
        help="Run DFMSlicingAgent + ToleranceValidator against existing specs/bom.json",
    )
    args = parser.parse_args(argv)

    orch = MasterOrchestrator(workspace_dir=args.workspace)

    if args.dfm_tolerance_only:
        orch.run_dfm_and_tolerance_only()
        return 0

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
