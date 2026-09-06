# Diagram workflow — abd-architecture-outline

Shared commands: [`../../../reference/diagram-workflow.md`](../../../reference/diagram-workflow.md)

**This skill:** `src/system-context.drawio` — must exist and verify PASS before the cell is marked done.

```powershell
# 1. Seed — creates system-context.drawio under src/
.\scripts\arch-drawio.ps1 init -ProjectRoot <target-project-root>

# 2. Fill system-context.drawio with the same systems named in the Surrounding systems
#    section of src/architecture-context.md — one node per ### entry, in lockstep.

# 3. Export PNG
.\scripts\arch-drawio.ps1 export -ProjectRoot <target-project-root>

# 4. Verify — must print PASS
.\scripts\arch-drawio.ps1 verify -ProjectRoot <target-project-root>
```

Fill the seeded `.drawio` from the Surrounding systems section of `src/architecture-context.md` (written first in generate step 2a) before export. The diagram and that section are two views of one element list — neither is the source of truth on its own.

The `architecture-context.md` template includes the diagram hyperlink commented out until the PNG is exported:

```markdown
> Source: [`./system-context.drawio`](./system-context.drawio)
>
> <!-- ![System Context](./system-context.png) -->
```

Uncomment the `![]()` line after the PNG is produced and placed at `src/system-context.png`.
