"""
Fidget Tank Mechanical Monster — CadQuery architecture plan
Sol 5.6 Max / Fidget Tank Architecture Framework

Models all 13 BOM components with a shared `printer_hole_compensation` parameter
for axle / clip / bore pairs.

Usage (once cadquery is installed):
  pip install cadquery
  python -c "from fidget_tank import export_all; export_all()"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

# Optional runtime dependency — architecture imports cleanly without CQ installed.
try:
    import cadquery as cq  # type: ignore
except ImportError:  # pragma: no cover
    cq = None


# ---------------------------------------------------------------------------
# Global tolerance / scale controls
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PrintParams:
    """Dynamic scaling for interlocking joints (pins, clips, bore fits)."""

    printer_hole_compensation: float = 0.15  # mm — expand female bores
    pin_od_nominal: float = 4.0              # mm
    clip_groove_depth: float = 0.6           # mm
    wall_min: float = 1.2                    # mm


def compensated_bore(nominal: float, p: PrintParams) -> float:
    """Female feature ID after hole compensation."""
    return nominal + p.printer_hole_compensation


def compensated_pin_od(nominal: float, p: PrintParams) -> float:
    """
    Male pin OD. Keep near nominal; clearance comes from female expansion.
    Optional negative bias for tight printers: pass printer_hole_compensation
    and subtract a fraction if empirical fit requires it.
    """
    return nominal


# ---------------------------------------------------------------------------
# Component builders (architecture stubs — parametric envelopes)
# IDs MUST match docs/bom/fidget_tank_bom.json
# ---------------------------------------------------------------------------

def build_01_chassis(p: PrintParams):
    if cq is None:
        return None
    body = cq.Workplane("XY").box(80, 40, 12)
    peg = cq.Workplane("XY").circle(3).extrude(8)
    pegs = (
        peg.translate((-25, -18, 6))
        .union(peg.translate((-25, 18, 6)))
        .union(peg.translate((25, -18, 6)))
        .union(peg.translate((25, 18, 6)))
    )
    return body.union(pegs)


def build_02_track_pod_lh(p: PrintParams):
    if cq is None:
        return None
    bore = compensated_bore(p.pin_od_nominal, p)
    return (
        cq.Workplane("XY")
        .box(50, 14, 18)
        .faces(">Y")
        .workplane()
        .pushPoints([(-15, 0), (0, 0), (15, 0)])
        .hole(bore)
    )


def build_03_track_pod_rh(p: PrintParams):
    # Mirror of LH about YZ
    part = build_02_track_pod_lh(p)
    if part is None:
        return None
    return part.mirror(mirrorPlane="YZ")


def build_04_road_wheel(p: PrintParams):
    if cq is None:
        return None
    bore = compensated_bore(p.pin_od_nominal, p)
    return (
        cq.Workplane("XY")
        .circle(8)
        .extrude(4)
        .faces(">Z")
        .workplane()
        .hole(bore)
    )


def build_05_axle_c_clip(p: PrintParams):
    """C-clip sized to snap over compensated axle groove."""
    if cq is None:
        return None
    pin = compensated_pin_od(p.pin_od_nominal, p)
    groove_od = pin - 2 * p.clip_groove_depth
    outer = groove_od / 2 + 1.2
    inner = groove_od / 2
    ring = cq.Workplane("XY").circle(outer).circle(inner).extrude(1.0)
    # Open the C gap
    gap = cq.Workplane("XY").box(outer * 2, 1.2, 1.2).translate((outer, 0, 0.5))
    return ring.cut(gap)


def build_06_axle_pin(p: PrintParams):
    if cq is None:
        return None
    od = compensated_pin_od(p.pin_od_nominal, p)
    length = 48
    shaft = cq.Workplane("XY").circle(od / 2).extrude(length)
    # Groove near each end for C-clips
    groove = (
        cq.Workplane("XY")
        .circle(od / 2)
        .circle(od / 2 - p.clip_groove_depth)
        .extrude(1.2)
    )
    g1 = groove.translate((0, 0, 3))
    g2 = groove.translate((0, 0, length - 4.2))
    return shaft.cut(g1).cut(g2)


def build_07_drive_sprocket(p: PrintParams):
    if cq is None:
        return None
    bore = compensated_bore(p.pin_od_nominal, p)
    disc = cq.Workplane("XY").circle(10).extrude(5)
    teeth = cq.Workplane("XY").polygon(8, 12).extrude(5)
    return disc.union(teeth).faces(">Z").workplane().hole(bore)


def build_08_idler_sprocket(p: PrintParams):
    # Same envelope as drive; lower tooth aggression can be differentiated later
    return build_07_drive_sprocket(p)


def build_09_track_segment(p: PrintParams):
    if cq is None:
        return None
    return (
        cq.Workplane("XY")
        .box(10, 8, 4)
        .faces(">X")
        .workplane()
        .hole(2.0 + p.printer_hole_compensation * 0.5)
    )


def build_10_clicker_leaf(p: PrintParams):
    """PETG flexure — geometry only; material enforced in slicing profile."""
    if cq is None:
        return None
    return (
        cq.Workplane("XY")
        .box(30, 8, 1.2)
        .faces(">Z")
        .workplane()
        .rect(6, 6)
        .cutBlind(-0.4)
    )


def build_11_turret(p: PrintParams):
    if cq is None:
        return None
    return cq.Workplane("XY").circle(14).extrude(10)


def build_12_barrel(p: PrintParams):
    if cq is None:
        return None
    return cq.Workplane("XY").circle(3).extrude(28)


def build_13_hatch_cover(p: PrintParams):
    if cq is None:
        return None
    return cq.Workplane("XY").ellipse(8, 6).extrude(2)


COMPONENT_REGISTRY: Dict[str, Callable[[PrintParams], object]] = {
    "01": build_01_chassis,
    "02": build_02_track_pod_lh,
    "03": build_03_track_pod_rh,
    "04": build_04_road_wheel,
    "05": build_05_axle_c_clip,
    "06": build_06_axle_pin,
    "07": build_07_drive_sprocket,
    "08": build_08_idler_sprocket,
    "09": build_09_track_segment,
    "10": build_10_clicker_leaf,
    "11": build_11_turret,
    "12": build_12_barrel,
    "13": build_13_hatch_cover,
}

COMPONENT_NAMES = {
    "01": "chassis",
    "02": "track_pod_lh",
    "03": "track_pod_rh",
    "04": "road_wheel",
    "05": "axle_c_clip",
    "06": "axle_pin",
    "07": "drive_sprocket",
    "08": "idler_sprocket",
    "09": "track_segment",
    "10": "clicker_leaf",
    "11": "turret",
    "12": "barrel",
    "13": "hatch_cover",
}


def validate_registry_vs_bom_count() -> None:
    assert len(COMPONENT_REGISTRY) == 13, "CAD registry must match 13-part BOM"


def export_all(
    hole_comp: float = 0.15,
    out_dir: str = "cad/exports",
) -> None:
    """Export STL for each component using the given hole compensation."""
    validate_registry_vs_bom_count()
    if cq is None:
        raise RuntimeError("cadquery not installed; architecture only")

    import os

    os.makedirs(out_dir, exist_ok=True)
    params = PrintParams(printer_hole_compensation=hole_comp)
    for cid, builder in COMPONENT_REGISTRY.items():
        solid = builder(params)
        path = f"{out_dir}/{cid}_{COMPONENT_NAMES[cid]}_hc{hole_comp:.2f}.stl"
        cq.exporters.export(solid, path)
        print(f"wrote {path}")


if __name__ == "__main__":
    validate_registry_vs_bom_count()
    print("Registry OK: 13 components")
    print("Default PrintParams:", PrintParams())
    if cq is None:
        print("CadQuery not installed — architecture validation only.")
    else:
        export_all()
