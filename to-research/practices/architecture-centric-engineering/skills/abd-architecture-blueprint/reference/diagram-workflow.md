# Diagram workflow — abd-architecture-blueprint

Shared commands: [`../../../reference/diagram-workflow.md`](../../../reference/diagram-workflow.md)

**This skill:** two diagrams alongside `src/architecture-context.md` — `system-context.drawio` and `architecture-flow.drawio`. Both must exist and verify PASS before the cell is marked done.

- **`system-context.drawio`** — One box per surrounding system named in the *Surrounding systems* section of `architecture-context.md`, with the system-under-design at the centre and one labelled edge per integration. The diagram and the markdown section share one element list; if a system is in the diagram it is in the section, and vice versa.
- **`architecture-flow.drawio`** — One row per step in the *Architecture Flow* table in `architecture-context.md`, showing the mechanisms active at each step in the composition order. The mechanism labels in the diagram come verbatim from the *Architecture Mechanisms* section; if a mechanism is in the flow it is defined in the section, and vice versa.

```powershell
# 1. Seed — creates both drawio files alongside src/architecture-context.md
.\scripts\arch-drawio.ps1 init -ProjectRoot <target-project-root>

# 2. Fill system-context.drawio from the Surrounding systems section
#    Fill architecture-flow.drawio from the Architecture Flow table

# 3. Export PNGs
.\scripts\arch-drawio.ps1 export -ProjectRoot <target-project-root>

# 4. Verify — must print PASS
.\scripts\arch-drawio.ps1 verify -ProjectRoot <target-project-root>
```

Fill seeded `.drawio` files from the matching sections of `src/architecture-context.md` before export. The drawio file and the markdown section are kept in lockstep — neither is the source of truth on its own; they are two views of the same element list.

**Retired diagrams** (kept in `retired/` for reference, no longer produced by this skill): `platform-architecture.drawio`, `module-overview.drawio`, `testing-flow.drawio`, `platform-architecture-elements.md`. The earlier four-diagram surface fragmented one architectural picture across multiple files; the current skill keeps it on one page in `architecture-context.md` and supports it with the two diagrams above.
