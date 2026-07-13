#!/usr/bin/env python3
"""Generated CadQuery/parameter tolerance evaluation scaffold.

Produced by Kinematics & Assembly Sub-Agent (Sol 5.6 Max).
Evaluates hole compensation for tolerance-critical BOM parts.
"""

from __future__ import annotations

# Nominal FDM hole compensation (mm) — tune per printer family
HOLE_COMPENSATION_MM = 0.15

TOLERANCE_CRITICAL_PARTS = [
    {"component_id": "COMP-46CFD2", "name": "drive axle pins", "qty": 4, "material": "PETG", "profile": "load-bearing"},
    {"component_id": "COMP-F6BB37", "name": "snap clips", "qty": 12, "material": "TPU", "profile": "compliant"},
]


def evaluate_pin_hole_pair(pin_od_mm: float, hole_id_mm: float) -> dict:
    """Return clearance after applying hole compensation."""
    compensated_hole = hole_id_mm + HOLE_COMPENSATION_MM
    clearance = compensated_hole - pin_od_mm
    return {
        "pin_od_mm": pin_od_mm,
        "hole_id_mm": hole_id_mm,
        "compensated_hole_mm": compensated_hole,
        "clearance_mm": round(clearance, 4),
        "fit": (
            "press" if clearance < 0.05 else
            "slip" if clearance < 0.25 else
            "loose"
        ),
    }


def report() -> None:
    print(f"Tolerance-critical parts: {len(TOLERANCE_CRITICAL_PARTS)}")
    for part in TOLERANCE_CRITICAL_PARTS:
        print(f"  - {part['component_id']}: {part['name']} "
              f"({part['profile']}, {part['material']})")
    sample = evaluate_pin_hole_pair(pin_od_mm=5.0, hole_id_mm=5.0)
    print(f"Sample pin/hole evaluation: {sample}")


if __name__ == "__main__":
    report()
