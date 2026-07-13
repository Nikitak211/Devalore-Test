#!/usr/bin/env python3
"""Tolerance Evaluation & Validation Framework (Sol 5.6 Max).

Checks all components marked requires_tolerance_tuning: true and builds a
parametric dimensional step-table for male/female pin clearance adjustments.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ToleranceValidator:
    """Parametric clearance matrix generator for fit-critical BOM parts."""

    def __init__(self, workspace_dir: str | None = None) -> None:
        self.workspace = (
            workspace_dir
            if workspace_dir is not None
            else str(Path(__file__).resolve().parents[2])
        )

    def generate_parametric_clearance_matrix(
        self, bom_data: dict[str, Any] | None = None, *, silent: bool = False
    ) -> dict[str, Any]:
        if bom_data is None:
            bom_path = os.path.join(self.workspace, "specs/bom.json")
            if not os.path.exists(bom_path):
                if not silent:
                    print("[Tolerance] specs/bom.json missing — skip matrix.")
                return {"components": []}
            with open(bom_path, "r", encoding="utf-8") as handle:
                bom_data = json.load(handle)

        matrix: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "orchestrator_version": "Sol-5.6-Max-PyOrch",
            "units": "mm",
            "note": (
                "Use these offsets inside your OpenSCAD/CadQuery design definitions."
            ),
            "components": [],
        }

        if not silent:
            print("\n--- PARAMETRIC TOLERANCE STEP-MATRIX ---")
            print(
                "Use these offsets inside your OpenSCAD/CadQuery design definitions:\n"
            )

        for component in bom_data.get("components", []):
            manufacturing = component.get("manufacturing", {})
            if not manufacturing.get("requires_tolerance_tuning"):
                continue

            comp_name = component["name"]
            profile = manufacturing.get("mechanical_profile", "cosmetic")
            material = manufacturing.get("material_hint", "PLA")

            # Base interference defaults adjusted by mechanical demands
            base_clearance = 0.15 if profile == "load-bearing" else 0.25
            tight = round(base_clearance - 0.05, 2)
            loose = round(base_clearance + 0.05, 2)

            entry = {
                "component_id": component["component_id"],
                "name": comp_name,
                "mechanical_profile": profile,
                "material_hint": material,
                "nominal_default_gap_mm": base_clearance,
                "test_matrix_tight_mm": tight,
                "test_matrix_loose_mm": loose,
                "recommended_fit": (
                    "press_to_slip"
                    if profile == "load-bearing"
                    else "flexible_clearance"
                ),
            }
            matrix["components"].append(entry)

            if not silent:
                print(f"Component: {comp_name.upper()} ({profile})")
                print(f"  -> Nominal Default Gap: {base_clearance}mm")
                print(f"  -> Test Matrix (Tight): {tight}mm")
                print(f"  -> Test Matrix (Loose): {loose}mm")
                print("-" * 40)

        # Persist JSON matrix alongside the validation script outputs
        out_dir = os.path.join(self.workspace, "outputs/config")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "tolerance_matrix.json")
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(matrix, handle, indent=2)
            handle.write("\n")

        if not silent:
            print(f"[Tolerance] Matrix written to: {out_path}")

        return matrix

    @staticmethod
    def evaluate_pin_hole_pair(
        pin_od_mm: float,
        hole_id_mm: float,
        hole_compensation_mm: float = 0.15,
    ) -> dict[str, Any]:
        """Return clearance after applying hole compensation."""
        compensated_hole = hole_id_mm + hole_compensation_mm
        clearance = compensated_hole - pin_od_mm
        return {
            "pin_od_mm": pin_od_mm,
            "hole_id_mm": hole_id_mm,
            "compensated_hole_mm": compensated_hole,
            "clearance_mm": round(clearance, 4),
            "fit": (
                "press"
                if clearance < 0.05
                else "slip"
                if clearance < 0.25
                else "loose"
            ),
        }


if __name__ == "__main__":
    # Default workspace is 3d_project/ (two levels up from outputs/code/)
    validator = ToleranceValidator()
    result = validator.generate_parametric_clearance_matrix()
    if result["components"]:
        sample = ToleranceValidator.evaluate_pin_hole_pair(5.0, 5.0)
        print(f"\nSample pin/hole evaluation: {sample}")
