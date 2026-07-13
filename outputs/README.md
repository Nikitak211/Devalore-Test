# Outputs directory

Code, configurations, and verification scripts produced by sub-agents.

| Path | Producer | Contents |
|------|----------|----------|
| `slicing/` | DFM Slicing Agent | Per-part slice profiles + orientation notes |
| `assembly/` | Kinematics Agent | State machines + assembly checklists |
| `tolerance/` | Kinematics Agent | Hole-compensation / fitment scripts |
| `scripts/` | Framework | Scaffold validators |

Templates (`_template_*`) are shapes only; project runs should write named artifacts such as `<project>_profiles.json`.
