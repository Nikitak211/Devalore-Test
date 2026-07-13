#!/usr/bin/env python3
"""DFM Slicing Sub-Agent — maps mechanical stress profiles to print matrices."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# Print matrices keyed by mechanical_profile
PROFILE_MATRICES: dict[str, dict[str, Any]] = {
    "load-bearing": {
        "layer_height_mm": 0.16,
        "wall_count": 4,
        "top_bottom_layers": 6,
        "infill_percent": 60,
        "infill_pattern": "gyroid",
        "orientation_hint": "axis_horizontal_max_layer_adhesion",
        "notes": "Prioritize shear resistance across layer bonds.",
    },
    "structural": {
        "layer_height_mm": 0.2,
        "wall_count": 3,
        "top_bottom_layers": 5,
        "infill_percent": 30,
        "infill_pattern": "grid",
        "orientation_hint": "largest_flat_on_bed",
        "notes": "Balance stiffness and print time.",
    },
    "compliant": {
        "layer_height_mm": 0.16,
        "wall_count": 2,
        "top_bottom_layers": 3,
        "infill_percent": 15,
        "infill_pattern": "rectilinear",
        "orientation_hint": "flex_axis_perpendicular_to_layers",
        "notes": "Preserve elasticity; avoid over-thick walls.",
    },
    "cosmetic": {
        "layer_height_mm": 0.12,
        "wall_count": 2,
        "top_bottom_layers": 4,
        "infill_percent": 15,
        "infill_pattern": "lines",
        "orientation_hint": "show_face_up",
        "notes": "Fine layers for surface quality.",
    },
}


class DFMSlicingSubAgent:
    """Evaluate BOM stress classes and emit per-component slicing metadata."""

    def generate_profiles(self, bom: dict[str, Any]) -> dict[str, Any]:
        profiles: list[dict[str, Any]] = []
        for component in bom.get("components", []):
            manufacturing = component.get("manufacturing", {})
            mechanical = manufacturing.get("mechanical_profile", "cosmetic")
            matrix = PROFILE_MATRICES.get(mechanical, PROFILE_MATRICES["cosmetic"])
            profiles.append(
                {
                    "component_id": component["component_id"],
                    "name": component["name"],
                    "material_hint": manufacturing.get("material_hint", "PLA"),
                    "mechanical_profile": mechanical,
                    "requires_tolerance_tuning": manufacturing.get(
                        "requires_tolerance_tuning", False
                    ),
                    "slicing": dict(matrix),
                }
            )

        return {
            "slicing_strategy": "optimized_per_mechanical_stress",
            "generated_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            "orchestrator_version": "Sol-5.6-Max-PyOrch",
            "profiles": profiles,
        }
