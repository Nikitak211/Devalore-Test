# Global Execution Prompt (Cursor)

Paste the block below into Cursor when you upload a new 3D model project or engineering document to kick off the multi-agent pipeline.

---

```text
Initialize the Master 3D Engineering Orchestrator using Sol 5.6 Max architecture.

Prefer the Python pipeline: `python 3d_project/orchestrator.py <path-to-brief>`.

Review the attached project data and execute the multi-agent pipeline:
1. Activate the 'Ingestion Agent' (`ingestion_engine.py`) to parse the documents and generate a universal JSON BOM structure into `3d_project/specs/bom.json`.
2. Activate the 'DFM Slicing Agent' (`dfm_slicing_engine.py`) to evaluate the mechanical needs of the parsed components and draft slicing strategies into `3d_project/outputs/config/slicing_meta.json`.
3. Activate the 'Kinematics Agent' (`kinematics_engine.py`) to map out the assembly state machine, logical dependencies, and required tolerance parameters into `3d_project/outputs/config/assembly_logic.json`.
4. Invoke the ToleranceValidator (`outputs/code/tolerance_test.py`) step-matrix for parts with `requires_tolerance_tuning: true`.

Verification shortcut when BOM already exists:
`python3 3d_project/orchestrator.py --dfm-tolerance-only`
```

---

## Expected write targets after a successful run

| Sub-agent | Primary paths |
|-----------|----------------|
| Ingestion | `/specs/bom/`, `/specs/manifests/`, `/specs/dependencies/*_raw_deps.json` |
| DFM Slicing | `/specs/dfm/`, `/outputs/slicing/` |
| Kinematics | `/specs/dependencies/*_graph.json`, `/outputs/assembly/`, `/outputs/tolerance/` |

## Orchestrator consolidation checklist

- [ ] Every BOM `component_id` has a DFM stress class + slice profile (or explicit deferral)
- [ ] Dependency graph is acyclic; assembly steps respect prerequisites
- [ ] Tolerance-critical interfaces have hole-compensation / fitment coverage
- [ ] Material vs process conflicts called out in the consolidated report
