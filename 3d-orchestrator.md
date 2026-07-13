# Sol 5.6 Max — Master 3D Engineering Orchestrator

Generalized multi-agent framework for analyzing **any** 3D model project or engineering document and delegating work to specialized sub-agents.

## Architecture

```
.cursorrules                 # Master Router / Orchestrator
/agents                      # Sub-agent system prompts + skill maps
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

## Kick off in Cursor

Paste the prompt from [`agents/GLOBAL_EXECUTION_PROMPT.md`](agents/GLOBAL_EXECUTION_PROMPT.md) and attach your project data.

## Validate scaffold

```bash
python outputs/scripts/validate_scaffold.py
python outputs/tolerance/_template_hole_compensation.py
```

## How to run a project

1. Drop source notes/images into a working area (or attach in Cursor).
2. Invoke the Global Execution Prompt.
3. Agents write into `/specs` and `/outputs` using the `_template_*` files as shapes.
4. Review the Orchestrator consolidation report before manufacturing.
