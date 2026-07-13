#!/usr/bin/env python3
"""Production CAD Generation Sub-Agent (Sol 5.6 Max).

Reads specs/bom.json (+ optional outputs/config/slicing_meta.json and
tolerance_matrix.json) and emits parametric OpenSCAD / CadQuery templates
under outputs/code/.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


class CADGenerationAgent:
    """Emit parametric OpenSCAD (+ CadQuery companion) templates per BOM part."""

    def __init__(self, workspace_dir: str | None = None) -> None:
        self.workspace = (
            workspace_dir
            if workspace_dir is not None
            else str(Path(__file__).resolve().parent)
        )

    @staticmethod
    def _clean_name(name: str) -> str:
        cleaned = re.sub(r"[^\w]+", "_", name.strip().lower())
        return cleaned.strip("_") or "part"

    def _load_json(self, relative: str) -> dict[str, Any] | None:
        path = os.path.join(self.workspace, relative)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _clearance_for(
        self,
        component: dict[str, Any],
        tolerance_matrix: dict[str, Any] | None,
    ) -> str:
        needs_tuning = component["manufacturing"]["requires_tolerance_tuning"]
        if not needs_tuning:
            return "0.00"
        if tolerance_matrix:
            for entry in tolerance_matrix.get("components", []):
                if entry.get("component_id") == component["component_id"]:
                    return f"{entry.get('nominal_default_gap_mm', 0.15):.2f}"
        profile = component["manufacturing"].get("mechanical_profile", "")
        return "0.15" if profile == "load-bearing" else "0.25"

    def _profile_dims(
        self,
        component: dict[str, Any],
        slicing_meta: dict[str, Any] | None,
    ) -> dict[str, float]:
        """Derive bounding-box heuristics from mechanical profile / quantity."""
        profile = component["manufacturing"].get("mechanical_profile", "cosmetic")
        qty = max(1, int(component.get("quantity", 1)))
        base = {
            "load-bearing": {"w": 24.0, "d": 12.0, "h": 8.0, "bore": 4.0},
            "structural": {"w": 60.0, "d": 40.0, "h": 12.0, "bore": 5.0},
            "compliant": {"w": 18.0, "d": 10.0, "h": 4.0, "bore": 2.5},
            "cosmetic": {"w": 30.0, "d": 20.0, "h": 10.0, "bore": 4.0},
        }.get(profile, {"w": 30.0, "d": 20.0, "h": 10.0, "bore": 4.0})

        # Soft scale structural housings by part count signal (no inventing geometry)
        if profile == "structural" and qty == 1:
            pass
        elif profile == "load-bearing":
            base["w"] = max(base["w"], 6.0 * min(qty, 6))

        # Enrich comment trail from slicing meta when present
        wall_loops = None
        if slicing_meta:
            entry = slicing_meta.get("component_profiles", {}).get(
                component["component_id"]
            )
            if entry:
                wall_loops = entry.get("print_parameters", {}).get("wall_loops")
        base["wall_loops"] = float(wall_loops) if wall_loops is not None else 0.0
        return base

    def generate_parametric_cad_templates(
        self, bom_data: dict[str, Any] | None = None
    ) -> list[str]:
        if bom_data is None:
            bom_path = os.path.join(self.workspace, "specs/bom.json")
            if not os.path.exists(bom_path):
                print("[CAD Agent] Hold: 'specs/bom.json' missing.")
                return []
            with open(bom_path, "r", encoding="utf-8") as handle:
                bom_data = json.load(handle)

        slicing_meta = self._load_json("outputs/config/slicing_meta.json")
        tolerance_matrix = self._load_json("outputs/config/tolerance_matrix.json")

        code_dir = os.path.join(self.workspace, "outputs/code")
        os.makedirs(code_dir, exist_ok=True)

        print("[CAD Agent] Creating parametric source definitions...")
        written: list[str] = []

        for component in bom_data["components"]:
            comp_id = component["component_id"]
            name_clean = self._clean_name(component["name"])
            clearance_var = self._clearance_for(component, tolerance_matrix)
            dims = self._profile_dims(component, slicing_meta)
            material = component["manufacturing"]["material_hint"]
            profile = component["manufacturing"]["mechanical_profile"]

            scad_template = f"""// Parametric Source File for: {component["name"]}
// Generated via Sol-5.6-Max-PyOrch CAD Agent
// Component ID: {comp_id}
// Material hint: {material} | Mechanical profile: {profile}
// Suggested wall_loops from DFM: {int(dims["wall_loops"]) if dims["wall_loops"] else "n/a"}

$fn = 64; // Render resolution
hole_compensation = {clearance_var}; // Dynamic FDM printer gap adjustment

body_w = {dims["w"]};
body_d = {dims["d"]};
body_h = {dims["h"]};
bore_r = {dims["bore"]};

module generate_{name_clean}_model() {{
    difference() {{
        // Core structural bounding hull (parametric)
        cube([body_w, body_d, body_h], center = true);

        // Dynamic interlocking peg / clearance track
        translate([0, 0, 0])
            cylinder(h = body_h + 2, r = bore_r + hole_compensation, center = true);
    }}
}}

generate_{name_clean}_model();
"""
            scad_path = os.path.join(code_dir, f"{comp_id}_{name_clean}.scad")
            with open(scad_path, "w", encoding="utf-8") as handle:
                handle.write(scad_template)
            written.append(scad_path)

            # Companion CadQuery sketch for the same parametric envelope
            cq_template = f'''"""Parametric CadQuery companion for: {component["name"]}
Generated via Sol-5.6-Max-PyOrch CAD Agent — Component ID: {comp_id}
"""
from __future__ import annotations

# Optional: `pip install cadquery` to execute this sketch.
try:
    import cadquery as cq
except ImportError:  # pragma: no cover - offline sketch fallback
    cq = None

HOLE_COMPENSATION = {clearance_var}
BODY_W, BODY_D, BODY_H = {dims["w"]}, {dims["d"]}, {dims["h"]}
BORE_R = {dims["bore"]}


def build():
    if cq is None:
        return {{
            "component_id": "{comp_id}",
            "name": "{component["name"]}",
            "dims": (BODY_W, BODY_D, BODY_H),
            "bore": BORE_R + HOLE_COMPENSATION,
            "note": "cadquery not installed — parameters only",
        }}
    return (
        cq.Workplane("XY")
        .box(BODY_W, BODY_D, BODY_H)
        .faces(">Z")
        .workplane()
        .hole(2 * (BORE_R + HOLE_COMPENSATION))
    )


if __name__ == "__main__":
    result = build()
    print(result)
'''
            cq_path = os.path.join(code_dir, f"{comp_id}_{name_clean}_cq.py")
            with open(cq_path, "w", encoding="utf-8") as handle:
                handle.write(cq_template)
            written.append(cq_path)

        print(
            f"[CAD Agent] Parametric CAD templates deployed safely inside: "
            f"{code_dir} ({len(written)} files)"
        )
        return written


if __name__ == "__main__":
    generator = CADGenerationAgent()
    generator.generate_parametric_cad_templates()
