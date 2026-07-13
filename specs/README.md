# Specs directory

Generalized project manifests, parsed JSON BOMs, dependency graphs, DFM stress maps, and JSON Schema contracts.

| Path | Purpose |
|------|---------|
| `schemas/` | BOM, slicing, assembly, dependency schemas |
| `bom/` | Project BOMs (`*_bom.json`) |
| `manifests/` | Ingestion provenance + gaps |
| `dependencies/` | Raw edges + synthesized graphs |
| `dfm/` | Stress classification maps |

Templates use a `_template_` prefix. Replace placeholders when a project pipeline runs — do not design beyond source data in Ingestion outputs.
