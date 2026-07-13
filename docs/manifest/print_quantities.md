# Fidget Tank Mechanical Monster — Source Manifest

Canonical print/assembly source used by the Sol 5.6 Max engineering agent.
Derived from PRINT QUANTITIES, PRINT NOTES, and ASSEMBLY sections for the physical kit.

## PRINT QUANTITIES

| ID | Part | Qty | Material |
|----|------|-----|----------|
| 01 | chassis | 1 | PLA |
| 02 | track pod LH | 1 | PLA |
| 03 | track pod RH | 1 | PLA |
| 04 | road wheel | 4 | PLA |
| 05 | axle C-clip | 6 | default |
| 06 | axle pin | 3 | PLA |
| 07 | drive sprocket | 2 | PLA |
| 08 | idler sprocket | 2 | PLA |
| 09 | track segment | 24 | PLA |
| 10 | clicker leaf | 1 | **PETG** |
| 11 | turret | 1 | PLA |
| 12 | barrel | 1 | PLA |
| 13 | hatch cover | 1 | PLA |

**Unique components:** 13  
**Total printed parts:** 48

## PRINT NOTES

- Structural load path (chassis, pods, wheels, sprockets, turret stack): **PLA**
- Fatigue flexure (clicker leaf): **PETG only**
- Axle/C-clip/wheel bore interfaces: run hole-compensation calibration before final print
- Default layer height: **0.20 mm**

## ASSEMBLY (Steps 1–7)

1. Inspect & kitting — verify all 13 SKUs against BOM quantities
2. Chassis prep — confirm peg geometry undamaged
3. Mount track pods LH/RH onto chassis pegs
4. Install axle pins through track pod bores
5. Mount road wheels + drive/idler sprockets; secure with axle C-clips
6. Install PETG clicker leaf into chassis clicker cavity
7. Fit turret → barrel → hatch cover; verify free rotation & click action

## Dependency Rule (Hard)

Wheels/sprockets **MUST NOT** be installed before track pods are seated on chassis pegs.
