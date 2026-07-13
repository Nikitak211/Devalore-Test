# CAD Architecture Plan — Fidget Tank Mechanical Monster

## Objective

Programmatically model all **13** BOM components with a shared
`printer_hole_compensation` variable for axle / C-clip / bore pairs.

## Stack

| Path | Role |
|------|------|
| `cad/fidget_tank.py` | CadQuery builders + export sweep |
| `cad/fidget_tank.scad` | OpenSCAD twin (same IDs / params) |
| `docs/bom/fidget_tank_bom.json` | Authority for IDs / qty / material |

## Tolerance Model

```
female_bore_id = nominal + printer_hole_compensation
male_pin_od    = nominal
clip_id        ≈ pin_od - 2 * clip_groove_depth   (snap over groove)
```

Default `printer_hole_compensation = 0.15 mm`.
Calibration sweep: `{0.00, 0.10, 0.15, 0.20, 0.25}` via `export_all(hole_comp=...)`.

## Component ↔ Builder Map

| ID | Name | Tolerance-critical |
|----|------|--------------------|
| 01 | chassis | peg OD vs pod
| 02/03 | track pod LH/RH | axle bores |
| 04 | road wheel | axle bore |
| 05 | axle C-clip | groove snap |
| 06 | axle pin | OD + grooves |
| 07/08 | drive/idler sprocket | axle bore |
| 09 | track segment | pin/hinge holes |
| 10 | clicker leaf | geometry only (PETG in slice) |
| 11–13 | turret / barrel / hatch | non-critical |

## Validation Gate (run before STL export)

1. `len(COMPONENT_REGISTRY) == 13`
2. BOM `quantity` totals unchanged (48 parts)
3. Material for `10` remains PETG in slicing config
4. Steps 3→5 assembly order respected (pods before wheels)

## Next Implementation Pass

- Flesh chassis peg / turret ring mating features to measured drawings
- Add assembly CQ script that mates parts and fails if prerequisites unmet
- Emit one STL per (component × hole_comp) for fit test racks
