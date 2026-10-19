# Render

Create a Draw.io class (or modules) diagram, then **validate** layout rules, then **repair** on failure.

Layout violations are always a **coding** problem in the render/layout path (`drawio_class_model.py` / `drawio_tools.py`) — never hand-edit the `.drawio` to greenwash scanners while leaving the generator broken. Follow the shared **repair** loop (faultyAsset / repairedAsset under `examples/evals/`).

## Steps

1. **Create** — call `create_diagram` with the source model text (or path). When the user asks to keep positioning, pass `keep_positioning=true`: look for an existing `.drawio` at the output path, update matching class contents in place, leave existing relationship routing, and layout only new classes/edges. Full regeneration (the default) destroys manual positioning.
2. **Validate** — load **contexts** (`drawio.md`) and run **scan** on the written `.drawio` path(s). Definitive failures: `edges-do-not-cross-classes`, class overlap, `base-above-derived`. Minimize: overlap / shared-anchor / approach.
3. **Repair** — when scan reports definitive layout violations, invoke **repair** as a **sub-agent** with `asset` = the diagram path and `violation` = the scan report. Repair fixes the **generator**, regenerates, and re-validates until clean.

Do not declare the diagram done while `edges-do-not-cross-classes` (or class overlap) violations remain.
