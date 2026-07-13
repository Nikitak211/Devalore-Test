# 3D Engineering — Fidget Tank Mechanical Monster

Sol 5.6 Max manufacturing agent workspace using the **Fidget Tank Architecture Framework**.

> GitHub: intended standalone repo name **`3d-engineering`**. This PR seeds the project inside the current remote (integration token cannot create a new GitHub repository). Extract this tree into `Nikitak211/3d-engineering` when ready.

## Layout

```
.cursorrules          # Senior 3D Manufacturing Agent system prompt
/cad                  # Parametric CadQuery + OpenSCAD sources
/config               # FDM slicing profiles per stress/material group
/docs                 # Manifest, BOM, assembly state machine
```

## Deliverables (executed)

### 1. JSON BOM
`docs/bom/fidget_tank_bom.json` — 13 components, material overrides (PETG clicker leaf), tolerance flags.

### 2. CAD architecture
`cad/fidget_tank.py` + `cad/fidget_tank.scad` — all 13 parts with `printer_hole_compensation` for axle/clip pairs.

### 3. Assembly checklist
`docs/assembly/assembly_checklist.md` — 7-step state machine with hard prerequisites (pods before wheels).

## Agent skills

Defined in `.cursorrules`: Analyze Manifest → Generate Slicing Profiles → Build Assembly State Machine.

## Quick validation

```bash
python cad/fidget_tank.py          # registry count == 13
# optional: pip install cadquery && python cad/fidget_tank.py
```
