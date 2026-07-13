# Assembly Verification Checklist — Fidget Tank Mechanical Monster

State machine for the 7 physical assembly steps. Each step lists hard prerequisites.
Do not advance a step until all boxes for that step are checked.

---

## Global Pre-Flight

- [ ] `docs/bom/fidget_tank_bom.json` present and `validation.bom_matches_manifest == true`
- [ ] Unique component count == **13**
- [ ] Total printed parts == **48**
- [ ] Clicker leaf (`10`) is **PETG** (reject PLA for this SKU)
- [ ] Hole-compensation calibration set printed & measured (axle/clip pairs)

---

## Step 1 — Inspect & Kit

**Purpose:** Ensure physical bag matches BOM before any mechanical work.

**Prerequisites:** none (entry state)

- [ ] Count chassis (`01`) × 1
- [ ] Count track pod LH (`02`) × 1 and RH (`03`) × 1
- [ ] Count road wheel (`04`) × 4
- [ ] Count axle C-clip (`05`) × 6
- [ ] Count axle pin (`06`) × 3
- [ ] Count drive sprocket (`07`) × 2 and idler sprocket (`08`) × 2
- [ ] Count track segment (`09`) × 24
- [ ] Count clicker leaf (`10`) × 1 (PETG)
- [ ] Count turret (`11`) × 1, barrel (`12`) × 1, hatch cover (`13`) × 1
- [ ] GATE: all counts match BOM → unlock Step 2

**Blocks if failed:** Steps 2–7

---

## Step 2 — Chassis Prep

**Purpose:** Validate chassis pegs and clicker cavity before sub-assemblies.

**Prerequisites:** `step_1.complete == true`

- [ ] Chassis (`01`) free of warping / missing pegs
- [ ] Chassis peg OD within design + hole_comp envelope
- [ ] Clicker cavity clear of flash/stringing
- [ ] GATE: chassis geometry OK → unlock Step 3

**Blocks if failed:** Steps 3–7

---

## Step 3 — Mount Track Pods

**Purpose:** Seat LH/RH track pods onto chassis pegs.

**Prerequisites:** `step_2.complete == true`

- [ ] Press track pod LH (`02`) fully onto left chassis pegs
- [ ] Press track pod RH (`03`) fully onto right chassis pegs
- [ ] Verify pod axle bores co-axial L↔R
- [ ] GATE: both pods seated → unlock Step 4

**Hard rule:** Do **not** install wheels or sprockets before this gate.

**Blocks if failed:** Steps 4–5 (drivetrain)

---

## Step 4 — Install Axle Pins

**Purpose:** Insert axle pins through track pod bores.

**Prerequisites:** `step_3.complete == true`

- [ ] Insert axle pin (`06`) × 3 through paired pod bores
- [ ] Axles spin freely without binding (hole_comp validated)
- [ ] Axle grooves visible for C-clip engagement on both ends
- [ ] GATE: all three axles installed → unlock Step 5

**Blocks if failed:** Step 5

---

## Step 5 — Wheels, Sprockets & C-Clips

**Purpose:** Build rolling gear and retain with C-clips.

**Prerequisites:** `step_4.complete == true` **AND** `step_3.complete == true`

- [ ] Slide road wheels (`04`) × 4 onto designated axles
- [ ] Slide drive sprockets (`07`) × 2 onto drive axle ends
- [ ] Slide idler sprockets (`08`) × 2 onto idler axle ends
- [ ] Snap axle C-clips (`05`) × 6 into axle grooves (retainers)
- [ ] Assemble track segments (`09`) × 24 into two loops; mount on sprockets
- [ ] Verify rotation: tracks articulate, no clip walk-off
- [ ] GATE: drivetrain free & retained → unlock Step 6

**Hard rule:** Wheels **cannot** install before track pods are on chassis pegs.

---

## Step 6 — Clicker Leaf (PETG)

**Purpose:** Install fatigue-critical clicker flexure.

**Prerequisites:** `step_2.complete == true` (chassis cavity ready); drivetrain may be complete but not required

- [ ] Confirm leaf material = PETG (`component_id: "10"`)
- [ ] Seat clicker leaf into chassis clicker cavity / pivot bosses
- [ ] Actuate: crisp click, no permanent set after 10 cycles
- [ ] GATE: clicker functional → unlock Step 7

---

## Step 7 — Turret Stack & Final QC

**Purpose:** Finish upper structure and validate full assembly.

**Prerequisites:** `step_5.complete == true` **AND** `step_6.complete == true`

- [ ] Seat turret (`11`) on chassis turret ring; confirm free yaw
- [ ] Install barrel (`12`) into turret muzzle socket
- [ ] Install hatch cover (`13`)
- [ ] Full QC: roll tracks, spin turret, actuate clicker
- [ ] GATE: `assembly_complete == true`

---

## State Machine Graph

```text
[START]
   │
   ▼
 Step1 Inspect/Kit ──fail──► HALT (missing parts)
   │ pass
   ▼
 Step2 Chassis Prep ──fail──► HALT (re-print chassis)
   │ pass
   ▼
 Step3 Track Pods ──fail──► HALT (re-print pods / check pegs)
   │ pass
   ├─────────────────────────┐
   ▼                         ▼
 Step4 Axles              Step6 Clicker Leaf (PETG)
   │ pass                    │ pass
   ▼                         │
 Step5 Wheels/Clips/Tracks   │
   │ pass                    │
   └──────────┬──────────────┘
              ▼
        Step7 Turret Stack
              │ pass
              ▼
           [COMPLETE]
```

## Prerequisite Matrix

| Step | Requires |
|------|----------|
| 1 | — |
| 2 | 1 |
| 3 | 1, 2 |
| 4 | 1, 2, 3 |
| 5 | 1, 2, 3, 4 |
| 6 | 1, 2 |
| 7 | 1, 2, 3, 4, 5, 6 |
