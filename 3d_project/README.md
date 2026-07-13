# Sol 5.6 Max — Python Multi-Agent Orchestrator (`3d_project/`)

Decoupled file-system architecture that routes unstructured engineering briefs
through specialized sub-agent execution loops.

## Layout

```text
3d_project/
├── orchestrator.py              # Master controller / router
├── ingestion_engine.py
├── dfm_slicing_engine.py
├── kinematics_engine.py
├── cad_generation_engine.py     # OpenSCAD / CadQuery templates
├── assembly_doc_engine.py       # ASSEMBLY_MANUAL.md compiler
├── briefs/sample_brief.txt
├── specs/bom.json
├── agents/*.prompt
└── outputs/
    ├── code/                    # *.scad, *_cq.py, tolerance_test.py
    └── config/                  # slicing_meta, tolerance_matrix, ASSEMBLY_MANUAL.md
```

## Full manufacturing run (default)

```bash
cd 3d_project
python3 orchestrator.py briefs/sample_brief.txt
```

## Partial verification paths

```bash
python3 orchestrator.py --dfm-tolerance-only
python3 orchestrator.py --cad-docs-only
python3 orchestrator.py --core-only briefs/sample_brief.txt
```

## Cursor verification prompt

```text
Run the full updated MasterOrchestrator architecture pipeline using the Sol 5.6 Max context loops.

Ingest our structural engineering components dataset, map the internal geometry flags,
compile the matching parametric OpenSCAD scripts down into '/outputs/code/', and generate
our step-by-step interactive Markdown manual file inside '/outputs/config/'. Verify all
code interfaces exit cleanly with zero dependency exceptions.
```

## Tests

```bash
cd 3d_project
python3 -m unittest tests.test_ingestion -v
```
