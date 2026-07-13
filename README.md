# 3D Engineering Agent

Chat with Cursor. Describe what you want to build. The master agent runs the manufacturing pipeline for you.

You do not need to know files, scripts, or CLI flags. One sentence is enough.

---

## How to use it (Cursor chat)

Open this project in Cursor and say what you want:

```text
create me a box with hinge lid 100mmx100mmx50
```

Other examples:

```text
design a phone stand, 80mm wide, 60mm deep, 100mm tall, snap-fit base
```

```text
make 4 PETG axle pins and a PLA chassis that they press-fit into
```

```text
hinged enclosure 120x80x40mm, wall 2mm, screw lid
```

That is the full input. The master agent takes over from there.

---

## What happens behind the scenes

The master agent (`.cursorrules`) reads your chat message and delegates to sub-agents:

| Step | Sub-agent | What it does |
|------|-----------|--------------|
| 1 | Ingestion | Turns your sentence into a structured BOM |
| 2 | DFM Slicing | Chooses materials, orientation, walls, infill |
| 3 | Kinematics | Maps assembly order, fits, clearances |
| 4 | CAD Generation | Writes OpenSCAD / CadQuery templates |
| 5 | Assembly Docs | Writes a step-by-step assembly manual |
| 6 | Consolidation | Checks IDs, tolerances, and print feasibility |

You get artifacts under `3d_project/` when it finishes. You only review results in chat.

```text
you (chat)
   │
   ▼
Master 3D Engineering Agent
   ├── Ingestion
   ├── DFM Slicing
   ├── Kinematics & Assembly
   ├── CAD Generation
   └── Assembly Docs
   │
   ▼
BOM · slicing profiles · CAD · assembly manual
```

---

## Setup for Cursor

1. Open this repo in Cursor.
2. Keep `.cursorrules` active (project rules).
3. Optionally pin or reference [`agents/GLOBAL_EXECUTION_PROMPT.md`](agents/GLOBAL_EXECUTION_PROMPT.md) once so the agent knows the chat-first contract.
4. Chat normally — describe the part, dimensions, material, and any fit/function notes.

You should not need to run commands yourself. If the agent needs the Python pipeline, it runs that for you.

---

## What to say (cheat sheet)

Include whatever you know; skip what you do not:

- **What** — box, pin, clip, enclosure, hinge lid, …
- **Size** — `100mm x 100mm x 50mm`
- **Count** — `4x pins`, `12 clips`
- **Material** — PLA / PETG / TPU (optional)
- **How it fits** — press-fit, snap, screw, hinge (optional)

Bad (too much ceremony):

```text
Please initialize the orchestrator and run orchestrator.py on briefs/foo.txt
```

Good:

```text
create me a box with hinge lid 100mmx100mmx50
```

---

## Where outputs land

| Output | Path |
|--------|------|
| BOM | `3d_project/specs/bom.json` |
| Consolidation report | `3d_project/specs/consolidation_report.json` |
| Slice settings | `3d_project/outputs/config/slicing_meta.json` |
| Assembly logic | `3d_project/outputs/config/assembly_logic.json` |
| Tolerances | `3d_project/outputs/config/tolerance_matrix.json` |
| Assembly manual | `3d_project/outputs/config/ASSEMBLY_MANUAL.md` |
| CAD templates | `3d_project/outputs/code/` |

Ask the agent in chat to open or summarize any of these.

---

## Project layout (for the agent)

```text
.
├── .cursorrules                 # Master agent rules — chat → sub-agents
├── agents/
│   ├── GLOBAL_EXECUTION_PROMPT.md
│   ├── ingestion.md
│   ├── dfm-slicing.md
│   └── kinematics-assembly.md
├── 3d_project/                  # Engines + generated artifacts
│   ├── orchestrator.py
│   ├── *_engine.py
│   ├── agents/*.prompt
│   ├── briefs/
│   ├── specs/
│   └── outputs/
├── specs/                       # Shared schemas / templates
└── outputs/                     # Shared output templates
```

---

## Agent contract

See [`agents/GLOBAL_EXECUTION_PROMPT.md`](agents/GLOBAL_EXECUTION_PROMPT.md).

Short version for Cursor:

- Treat every casual build request as a full pipeline job.
- Do not ask the user to run CLI unless they explicitly want to.
- Save their words into a brief, run the sub-agent chain, report results in chat.

## License

MIT
