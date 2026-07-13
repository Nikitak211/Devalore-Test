# Sol 5.6 Max — Python Multi-Agent Orchestrator (`3d_project/`)

Decoupled file-system architecture that routes unstructured engineering briefs
through specialized sub-agent execution loops.

## Layout

```text
3d_project/
├── orchestrator.py              # Master controller / router
├── ingestion_engine.py          # Ingestion & BOM parsing engine
├── dfm_slicing_engine.py        # Production DFM slicing agent
├── dfm_engine.py                # Compatibility shim → dfm_slicing_engine
├── kinematics_engine.py         # Assembly graph generator
├── briefs/
│   └── sample_brief.txt
├── specs/
│   ├── bom.json
│   ├── bom.schema.json
│   └── consolidation_report.json
├── agents/
│   ├── ingestion.prompt
│   ├── dfm_slicing.prompt
│   └── kinematics.prompt
└── outputs/
    ├── code/
    │   └── tolerance_test.py    # ToleranceValidator framework
    └── config/
        ├── slicing_meta.json
        ├── assembly_logic.json
        └── tolerance_matrix.json
```

## Full pipeline

```bash
cd 3d_project
python3 orchestrator.py briefs/sample_brief.txt
```

## DFM + Tolerance only (verification prompt)

```bash
cd 3d_project
python3 orchestrator.py --dfm-tolerance-only
# or:
python3 dfm_slicing_engine.py
python3 outputs/code/tolerance_test.py
```

## Cursor verification prompt

```text
Run the DFMSlicingAgent execution logic on the existing 'specs/bom.json' dataset.

Verify that structural and load-bearing components receive distinct wall-count
profiles and layer metrics inside the 'outputs/config/slicing_meta.json' matrix
structure. Once written, invoke the tolerance validator step-matrix framework
to output geometric gap definitions for components flagged for tolerance testing.
```

## Tests

```bash
cd 3d_project
python3 -m unittest tests.test_ingestion -v
```
