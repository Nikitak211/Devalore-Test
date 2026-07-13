# Sol 5.6 Max — Python Multi-Agent Orchestrator (`3d_project/`)

Decoupled file-system architecture that routes unstructured engineering briefs
through specialized sub-agent execution loops.

## Layout

```text
3d_project/
├── orchestrator.py           # Master controller / router
├── ingestion_engine.py       # Ingestion & BOM parsing engine
├── dfm_engine.py             # DFM slicing profile generator
├── kinematics_engine.py      # Assembly graph + tolerance script generator
├── briefs/
│   └── sample_brief.txt      # Example raw engineering text
├── specs/
│   ├── bom.json              # Structured BOM (generated)
│   ├── bom.schema.json       # JSON Schema for BOM
│   └── consolidation_report.json
├── agents/
│   ├── ingestion.prompt
│   ├── dfm_slicing.prompt
│   └── kinematics.prompt
└── outputs/
    ├── code/
    │   └── tolerance_test.py
    └── config/
        ├── slicing_meta.json
        └── assembly_logic.json
```

## Run the pipeline

```bash
cd 3d_project
python orchestrator.py briefs/sample_brief.txt
```

## Run ingestion only

```bash
cd 3d_project
python ingestion_engine.py
```

## Tests

```bash
cd 3d_project
python -m unittest tests.test_ingestion -v
```

## Cursor verification prompt

```text
Run the IngestionSubAgent script logic using the Sol 5.6 Max context.

Review the raw text input block pasted below, convert it to our target
structured components dictionary map schema, and execute file creation tasks
down into 'specs/bom.json'. Ensure all functional part tolerances are evaluated
accurately based on mechanical usage keywords.

[PASTE YOUR RAW TEXT MANIFEST HERE]
```
