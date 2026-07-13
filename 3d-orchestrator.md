# Sol 5.6 Max — Master 3D Engineering Orchestrator

Generalized multi-agent framework for analyzing **any** 3D model project or engineering document and delegating work to specialized sub-agents.

## Architecture

```
.cursorrules                 # Master Router / Orchestrator runtime rules
/3d_project                  # Production Python orchestrator + engines
  orchestrator.py
  ingestion_engine.py
  dfm_slicing_engine.py
  kinematics_engine.py
  cad_generation_engine.py
  assembly_doc_engine.py
  agents/*.prompt
  specs/bom.json
  outputs/code/tolerance_test.py
  outputs/code/*.scad
  outputs/config/ASSEMBLY_MANUAL.md
  outputs/config/
/agents                      # Sub-agent system prompts + skill maps (docs)
  ingestion.md
  dfm-slicing.md
  kinematics-assembly.md
  GLOBAL_EXECUTION_PROMPT.md
/specs                       # Manifests, BOM, dependency graphs, schemas
  schemas/
  bom/
  manifests/
  dependencies/
  dfm/
/outputs                     # Sub-agent generated configs + scripts
  slicing/
  assembly/
  tolerance/
```

## Pipeline

1. **Ingestion** — Parse briefs / images / CAD meta-data → universal JSON BOM
2. **DFM Slicing** — Stress-class components → FDM/SLA slice directives
3. **Kinematics & Assembly** — Interface map, state machine, hole-compensation tests
4. **Consolidation** — Orchestrator checks ID coverage, cycles, tolerance conflicts, feasibility

## Run the Python orchestrator

```bash
cd 3d_project
python orchestrator.py briefs/sample_brief.txt
python -m unittest tests.test_ingestion -v
```

## Kick off in Cursor

Paste the prompt from [`agents/GLOBAL_EXECUTION_PROMPT.md`](agents/GLOBAL_EXECUTION_PROMPT.md) and attach your project data — or run the verification prompt in [`3d_project/README.md`](3d_project/README.md).

## Validate scaffold

```bash
python outputs/scripts/validate_scaffold.py
python outputs/tolerance/_template_hole_compensation.py
```

## How to run a project

1. Drop source notes into `3d_project/briefs/` (or attach in Cursor).
2. Run `python 3d_project/orchestrator.py <brief>` or invoke the Global Execution Prompt.
3. Agents write into `/3d_project/specs`, `/3d_project/outputs`, and mirrored `/specs` + `/outputs` trees.
4. Review the Orchestrator consolidation report before manufacturing.
