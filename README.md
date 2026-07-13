# Master 3D Engineering Orchestrator

Multi-agent manufacturing pipeline that turns unstructured engineering briefs into BOM data, DFM slicing profiles, assembly logic, parametric CAD templates, and assembly manuals.

This repository also includes a legacy **Pets** web app (React + Express + MongoDB). The primary system is the Sol 5.6 Max orchestrator under `3d_project/`.

---

## Overview

| Layer | Path | Role |
|-------|------|------|
| Master router | `.cursorrules`, `3d_project/orchestrator.py` | Routes briefs through sub-agents and consolidates results |
| Agent prompts | `agents/`, `3d_project/agents/` | Skill scopes for each sub-agent |
| Specs & schemas | `specs/`, `3d_project/specs/` | BOM, DFM maps, dependency graphs, JSON Schema contracts |
| Generated outputs | `outputs/`, `3d_project/outputs/` | Slice profiles, assembly state machines, CAD, manuals |
| Legacy web app | `client/`, `server/` | Pets submission UI + API |

### Pipeline

1. **Ingestion** — Parse text briefs → universal JSON BOM  
2. **DFM Slicing** — Stress-class parts → FDM/SLA print parameters  
3. **Kinematics & Assembly** — Dependency graph, state machine, tolerances  
4. **CAD Generation** — Parametric OpenSCAD / CadQuery templates  
5. **Assembly Docs** — Step-by-step `ASSEMBLY_MANUAL.md`  
6. **Consolidation** — ID coverage, cycle checks, tolerance / feasibility flags  

```text
brief.txt
   │
   ▼
ingestion_engine.py ──► specs/bom.json
   │
   ▼
dfm_slicing_engine.py ──► outputs/config/slicing_meta.json
   │
   ▼
kinematics_engine.py ──► outputs/config/assembly_logic.json
   │
   ▼
tolerance_test.py ──► outputs/config/tolerance_matrix.json
   │
   ▼
cad_generation_engine.py ──► outputs/code/*.scad, *_cq.py
   │
   ▼
assembly_doc_engine.py ──► outputs/config/ASSEMBLY_MANUAL.md
```

---

## Requirements

### 3D Orchestrator

- Python 3.10+ (stdlib only for the core pipeline)

### Pets web app (optional)

- Node.js + npm
- MongoDB
- `.env` in `server/` with `MONGODB_URI` (and optional `PORT`)

---

## Command prompt examples

### Clone

```bash
git clone <repository-url>
cd <repository-directory>
```

### Full manufacturing run (recommended)

Uses `3d_project/briefs/sample_brief.txt` when no path is given:

```bash
cd 3d_project
python3 orchestrator.py
```

Or pass an explicit brief:

```bash
cd 3d_project
python3 orchestrator.py briefs/sample_brief.txt
```

From repo root:

```bash
python3 3d_project/orchestrator.py 3d_project/briefs/sample_brief.txt
```

Custom project name and workspace:

```bash
python3 3d_project/orchestrator.py briefs/sample_brief.txt \
  --project-name "My Chassis Assembly" \
  --workspace /absolute/path/to/3d_project
```

### Partial verification paths

```bash
# Existing BOM only → DFM profiles + tolerance matrix
python3 3d_project/orchestrator.py --dfm-tolerance-only

# Existing BOM only → OpenSCAD/CadQuery + ASSEMBLY_MANUAL.md
python3 3d_project/orchestrator.py --cad-docs-only

# Ingest → DFM → kinematics → tolerance (skip CAD & docs)
python3 3d_project/orchestrator.py --core-only briefs/sample_brief.txt
```

Run partial flags from inside `3d_project/`:

```bash
cd 3d_project
python3 orchestrator.py --dfm-tolerance-only
python3 orchestrator.py --cad-docs-only
python3 orchestrator.py --core-only briefs/sample_brief.txt
```

### Run with your own brief

```bash
# 1. Add a brief
cat > 3d_project/briefs/my_design.txt <<'EOF'
PRINT REQUIREMENTS:
2x hinge pins - PETG
1 enclosure shell - PLA

ASSEMBLY INDEX:
Step 1: Press fit hinge pins into enclosure shell.
EOF

# 2. Execute pipeline
python3 3d_project/orchestrator.py 3d_project/briefs/my_design.txt \
  --project-name "Hinge Enclosure"
```

### Inspect generated artifacts

```bash
# BOM + consolidation
cat 3d_project/specs/bom.json
cat 3d_project/specs/consolidation_report.json

# Manufacturing configs
cat 3d_project/outputs/config/slicing_meta.json
cat 3d_project/outputs/config/assembly_logic.json
cat 3d_project/outputs/config/tolerance_matrix.json
cat 3d_project/outputs/config/ASSEMBLY_MANUAL.md

# CAD templates
ls 3d_project/outputs/code/
```

### Tests & scaffold validation

```bash
# Ingestion unit tests
cd 3d_project
python3 -m unittest tests.test_ingestion -v

# From repo root: scaffold completeness
python3 outputs/scripts/validate_scaffold.py

# Dry-run hole-compensation template
python3 outputs/tolerance/_template_hole_compensation.py
```

### Cursor kickoff prompt

Paste the block in [`agents/GLOBAL_EXECUTION_PROMPT.md`](agents/GLOBAL_EXECUTION_PROMPT.md), or use:

```text
Initialize the Master 3D Engineering Orchestrator using Sol 5.6 Max architecture.
Prefer: python3 3d_project/orchestrator.py <path-to-brief>
```

---

## Pets web app (legacy)

### Install

```bash
cd server && npm install
cd ../client && npm install
```

### Configure

Create `server/.env`:

```bash
MONGODB_URI=mongodb://localhost:27017/pets
PORT=7000
```

### Run

```bash
# Terminal 1 — API (nodemon)
cd server && npm start

# Terminal 2 — React client (dev)
cd client && npm start

# Or production-style: build client, then serve via Express
cd client && npm run build
cd ../server && npm start
```

From repo root (runs client build, then server):

```bash
npm start
```

Open [http://localhost:7000](http://localhost:7000).

---

## Directory map

```text
.
├── .cursorrules                 # Orchestrator runtime rules
├── 3d-orchestrator.md           # Architecture notes
├── 3d_project/                  # Production Python pipeline
│   ├── orchestrator.py
│   ├── *_engine.py
│   ├── agents/*.prompt
│   ├── briefs/
│   ├── specs/
│   ├── outputs/{code,config}/
│   └── tests/
├── agents/                      # Human-readable sub-agent docs
├── specs/                       # Shared schemas + mirrored manifests
├── outputs/                     # Shared slicing/assembly/tolerance templates
├── client/                      # Pets React app
└── server/                      # Pets Express API
```

---

## Further reading

- [`3d_project/README.md`](3d_project/README.md) — Python orchestrator details  
- [`agents/README.md`](agents/README.md) — Sub-agent registry  
- [`specs/README.md`](specs/README.md) — Manifest & schema layout  
- [`outputs/README.md`](outputs/README.md) — Generated artifact layout  
- [`agents/GLOBAL_EXECUTION_PROMPT.md`](agents/GLOBAL_EXECUTION_PROMPT.md) — Full Cursor execution prompt  

## License

MIT
