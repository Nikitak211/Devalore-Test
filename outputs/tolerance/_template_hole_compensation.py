#!/usr/bin/env python3
"""Programmatic fitment / printer hole-compensation framework.

Kinematics & Assembly Agent copies this template to:
  /outputs/tolerance/<project>_hole_compensation.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class FitBand:
    min_mm: float
    max_mm: float


class HoleCompensationModel:
    """Male/female pair scaling with a global hole compensation offset."""

    def __init__(self, printer_hole_compensation_mm: float = 0.15) -> None:
        self.comp = printer_hole_compensation_mm
        self._failures: List[str] = []

    def female_hole_id(self, nominal_mm: float) -> float:
        """Enlarge holes so printed pins seat after XY shrinkage / elephant foot."""
        return nominal_mm + self.comp

    def male_pin_od(self, nominal_mm: float, intentional_interference_mm: float = 0.0) -> float:
        return nominal_mm + intentional_interference_mm

    def validate_pair(
        self,
        name: str,
        measured_clearance_mm: float,
        band: FitBand,
    ) -> bool:
        ok = band.min_mm <= measured_clearance_mm <= band.max_mm
        if not ok:
            self._failures.append(
                f"{name}: clearance {measured_clearance_mm:.3f} mm "
                f"outside [{band.min_mm:.3f}, {band.max_mm:.3f}]"
            )
        return ok

    def assert_all(self) -> None:
        if self._failures:
            raise AssertionError("Fitment failures:\n- " + "\n- ".join(self._failures))


# Example interface registry — replace per project.
DEFAULT_BANDS: Dict[str, FitBand] = {
    "pin_in_bore": FitBand(0.05, 0.35),
    "clip_over_groove": FitBand(0.00, 0.25),
    "slide_clearance": FitBand(0.20, 0.60),
}


def demo() -> None:
    model = HoleCompensationModel(0.15)
    pin = model.male_pin_od(5.0)
    hole = model.female_hole_id(5.0)
    clearance = hole - pin
    model.validate_pair("demo_pin_bore", clearance, DEFAULT_BANDS["pin_in_bore"])
    model.assert_all()
    print(f"ok: pin={pin:.3f} hole={hole:.3f} clearance={clearance:.3f}")


if __name__ == "__main__":
    demo()
