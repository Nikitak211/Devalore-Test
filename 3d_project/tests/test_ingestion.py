#!/usr/bin/env python3
"""Unit tests for IngestionSubAgent parsing and orchestrator consolidation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion_engine import IngestionSubAgent  # noqa: E402
from orchestrator import MasterOrchestrator  # noqa: E402


SAMPLE = """
PRINT REQUIREMENTS:
4x drive axle pins - print in high strength PETG
1 main outer chassis casing - PLA standard
12 snap clips (flexible tpu material)

ASSEMBLY INDEX:
Step 1: Press fit drive axle pins into the outer chassis casing.
Step 2: Snap locking clips along outer body track lines.
"""


class TestIngestionSubAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = IngestionSubAgent()

    def test_extracts_three_components(self) -> None:
        bom = self.parser.parse_text_brief(SAMPLE)
        self.assertEqual(len(bom["components"]), 3)
        by_name = {c["name"]: c for c in bom["components"]}
        self.assertIn("drive axle pins", by_name)
        self.assertEqual(by_name["drive axle pins"]["quantity"], 4)
        self.assertEqual(
            by_name["drive axle pins"]["manufacturing"]["material_hint"], "PETG"
        )
        self.assertEqual(
            by_name["drive axle pins"]["manufacturing"]["mechanical_profile"],
            "load-bearing",
        )
        self.assertTrue(
            by_name["drive axle pins"]["manufacturing"]["requires_tolerance_tuning"]
        )

        self.assertEqual(by_name["main outer chassis casing"]["quantity"], 1)
        self.assertEqual(
            by_name["main outer chassis casing"]["manufacturing"]["material_hint"],
            "PLA",
        )
        self.assertEqual(
            by_name["main outer chassis casing"]["manufacturing"][
                "mechanical_profile"
            ],
            "structural",
        )

        self.assertEqual(by_name["snap clips"]["quantity"], 12)
        self.assertEqual(
            by_name["snap clips"]["manufacturing"]["material_hint"], "TPU"
        )
        self.assertEqual(
            by_name["snap clips"]["manufacturing"]["mechanical_profile"],
            "compliant",
        )

    def test_extracts_assembly_steps(self) -> None:
        bom = self.parser.parse_text_brief(SAMPLE)
        self.assertEqual(len(bom["assembly_steps"]), 2)
        self.assertEqual(bom["assembly_steps"][0]["step_number"], 1)
        self.assertIn("Press fit", bom["assembly_steps"][0]["instruction"])

    def test_metadata_present(self) -> None:
        bom = self.parser.parse_text_brief(
            SAMPLE, project_name="Dynamic 3D Mechanical Assembly"
        )
        meta = bom["project_metadata"]
        self.assertEqual(meta["project_name"], "Dynamic 3D Mechanical Assembly")
        self.assertEqual(meta["orchestrator_version"], "Sol-5.6-Max-PyOrch")
        self.assertIn("timestamp", meta)


class TestOrchestrator(unittest.TestCase):
    def test_full_pipeline_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            brief_dir = workspace / "briefs"
            brief_dir.mkdir(parents=True)
            brief_path = brief_dir / "sample_brief.txt"
            brief_path.write_text(SAMPLE, encoding="utf-8")

            orch = MasterOrchestrator(workspace_dir=str(workspace))
            result = orch.route_to_sub_agents(brief_path)

            bom_path = workspace / "specs" / "bom.json"
            slicing_path = workspace / "outputs" / "config" / "slicing_meta.json"
            tolerance_path = workspace / "outputs" / "code" / "tolerance_test.py"
            assembly_path = workspace / "outputs" / "config" / "assembly_logic.json"

            self.assertTrue(bom_path.exists())
            self.assertTrue(slicing_path.exists())
            self.assertTrue(tolerance_path.exists())
            self.assertTrue(assembly_path.exists())

            bom = json.loads(bom_path.read_text(encoding="utf-8"))
            self.assertEqual(len(bom["components"]), 3)
            self.assertEqual(len(result["slicing_profiles"]["profiles"]), 3)

            # Prerequisites should be linked for step 1 (pins + chassis)
            step1 = bom["assembly_steps"][0]
            self.assertGreaterEqual(len(step1["prerequisite_components"]), 2)

            # Tolerance script should mention load-bearing / compliant parts
            script = tolerance_path.read_text(encoding="utf-8")
            self.assertIn("TOLERANCE_CRITICAL_PARTS", script)
            self.assertIn("HOLE_COMPENSATION_MM", script)


if __name__ == "__main__":
    unittest.main()
