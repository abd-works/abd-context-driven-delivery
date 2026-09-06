# Architecture-Centric Engineering — Diagram Workflow (shared)

Architecture diagrams use **`arch-drawio.ps1`** from the project or skill scripts folder. Each skill ships `reference/diagram-workflow.md` with its diagram set; this file owns the shared init/export/verify sequence.

---

## Shared commands

```powershell
# Seed diagram(s)
.\scripts\arch-drawio.ps1 init -ProjectRoot <target-project-root>

# Export PNGs
.\scripts\arch-drawio.ps1 export -ProjectRoot <target-project-root>

# Verify — must print PASS
.\scripts\arch-drawio.ps1 verify -ProjectRoot <target-project-root>
```

Fill seeded `.drawio` files from element-inventory markdown before export.

---

## By skill

| Skill | Diagrams |
| --- | --- |
| `abd-architecture-outline` | `system-context.drawio` |
| `abd-architecture-blueprint` | `platform-architecture.drawio`, `module-overview.drawio`, `architecture-flow.drawio`, `testing-flow.drawio` |
| `abd-architecture-specification` | `architecture-flow.drawio`, `architecture-specification-participants.drawio` |

See each skill's `reference/diagram-workflow.md` for fill order and element-inventory sources.
