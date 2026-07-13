#!/usr/bin/env python3
"""Production DFM Slicing Agent (Sol 5.6 Max).

Reads specs/bom.json, evaluates mechanical_profile + material_hint, and
writes optimized print path matrices to outputs/config/slicing_meta.json.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DFMSlicingAgent:
    """Map BOM stress classes to FDM wall/infill/cooling print matrices."""

    def __init__(self, workspace_dir: str | None = None) -> None:
        self.workspace = (
            workspace_dir
            if workspace_dir is not None
            else str(Path(__file__).resolve().parent)
        )
        # Standard rules engine matrix mapping engineering metrics to profiles
        self.slicing_matrix = {
            "load-bearing": {
                "layer_height_mm": 0.16,
                "wall_loops": 5,
                "infill_percentage": 40,
                "infill_pattern": "gyroid",
                "cooling_speed_pct": 40,
            },
            "compliant": {
                "layer_height_mm": 0.20,
                "wall_loops": 3,
                "infill_percentage": 20,
                "infill_pattern": "concentric",
                "cooling_speed_pct": 100,
            },
            "structural": {
                "layer_height_mm": 0.20,
                "wall_loops": 4,
                "infill_percentage": 25,
                "infill_pattern": "grid",
                "cooling_speed_pct": 100,
            },
            "cosmetic": {
                "layer_height_mm": 0.12,
                "wall_loops": 2,
                "infill_percentage": 15,
                "infill_pattern": "lightning",
                "cooling_speed_pct": 100,
            },
        }

    def process_bom_to_slicing_profiles(
        self, bom_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if bom_data is None:
            bom_path = os.path.join(self.workspace, "specs/bom.json")
            if not os.path.exists(bom_path):
                raise FileNotFoundError(
                    f"Target manifest file missing at: {bom_path}"
                )
            with open(bom_path, "r", encoding="utf-8") as handle:
                bom_data = json.load(handle)

        slicing_meta: dict[str, Any] = {
            "project_name": bom_data["project_metadata"]["project_name"],
            "manufacturing_platform": "FDM_Optimized",
            "slicing_strategy": "optimized_per_mechanical_stress",
            "generated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "orchestrator_version": "Sol-5.6-Max-PyOrch",
            "component_profiles": {},
        }

        for component in bom_data["components"]:
            comp_id = component["component_id"]
            profile_type = component["manufacturing"]["mechanical_profile"]
            material = component["manufacturing"]["material_hint"]

            # Fallback configuration matrix routing
            config = self.slicing_matrix.get(
                profile_type, self.slicing_matrix["cosmetic"]
            ).copy()
            config["target_material"] = material
            config["mechanical_profile"] = profile_type
            config["requires_tolerance_tuning"] = component["manufacturing"].get(
                "requires_tolerance_tuning", False
            )

            # Material adjustment rule overrides
            if material in ("PETG", "ABS"):
                config["cooling_speed_pct"] = 30  # Enhance layer adhesion
            elif material == "TPU":
                config["infill_pattern"] = "concentric"  # Preserve elasticity

            # Volumetric metrics derived from print parameters
            config["volumetric_metrics"] = self._estimate_volumetrics(config)

            slicing_meta["component_profiles"][comp_id] = {
                "name": component["name"],
                "quantity": component.get("quantity", 1),
                "print_parameters": config,
            }

        # Also expose a flat profiles list for orchestrator consolidation checks
        slicing_meta["profiles"] = [
            {
                "component_id": cid,
                "name": entry["name"],
                "mechanical_profile": entry["print_parameters"]["mechanical_profile"],
                "material_hint": entry["print_parameters"]["target_material"],
                "wall_loops": entry["print_parameters"]["wall_loops"],
                "layer_height_mm": entry["print_parameters"]["layer_height_mm"],
                "infill_percentage": entry["print_parameters"]["infill_percentage"],
                "infill_pattern": entry["print_parameters"]["infill_pattern"],
                "print_parameters": entry["print_parameters"],
            }
            for cid, entry in slicing_meta["component_profiles"].items()
        ]

        output_path = os.path.join(self.workspace, "outputs/config/slicing_meta.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(slicing_meta, handle, indent=4)
            handle.write("\n")

        print(f"[DFM Agent] Slicing matrix generated down to: {output_path}")
        return slicing_meta

    @staticmethod
    def _estimate_volumetrics(config: dict[str, Any]) -> dict[str, Any]:
        """Derive approximate relative density / wall fraction metrics."""
        wall_loops = config["wall_loops"]
        infill = config["infill_percentage"]
        # Heuristic relative solid volume score (unitless, 0–100 scale)
        relative_density = min(
            100.0, round(wall_loops * 8.0 + infill * 0.7, 2)
        )
        return {
            "relative_density_score": relative_density,
            "wall_fraction_estimate": round(min(1.0, wall_loops / 8.0), 3),
            "infill_fraction": round(infill / 100.0, 3),
        }

    # Compatibility alias used by earlier orchestrator hook
    def generate_profiles(self, bom: dict[str, Any]) -> dict[str, Any]:
        return self.process_bom_to_slicing_profiles(bom_data=bom)


# Backward-compatible alias
DFMSlicingSubAgent = DFMSlicingAgent


if __name__ == "__main__":
    slicer = DFMSlicingAgent()
    try:
        result = slicer.process_bom_to_slicing_profiles()
        for cid, entry in result["component_profiles"].items():
            params = entry["print_parameters"]
            print(
                f"  {cid} ({entry['name']}): walls={params['wall_loops']}, "
                f"layer={params['layer_height_mm']}, "
                f"infill={params['infill_percentage']}% {params['infill_pattern']}, "
                f"cool={params['cooling_speed_pct']}%"
            )
    except FileNotFoundError:
        print(
            "[DFM Agent Idle] Create specs/bom.json first to run matrix test loops."
        )
