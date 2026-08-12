---
fidelity: [scenarios]
artifact: [story-context]
format: md
---

# Plan Delivery Routes

**Status:** fully expanded for scenarios generation

**Stories in scope:**

Enter Zones On Route:
- *Create Delivery Route*
- *Add Zone To Route*
- *Remove Zone From Route*
- *View Stops On Route*
- *Search Zones*
- *Preview Zone Stops*

Sequence Route Path:
- *Reorder Route Zones*
- *Recalculate Route Path*
- *View Route Path*
- *View Stop Order*
- *View Path Change Summary*

Hang Packages On Stops:
- *Assign Package To Stop*
- *Unassign Package From Stop*
- *Move Package Between Stops*
- *List Packages On Route*
- *Search Packages*

Shape Delivery Zones:
- *Define Zone Boundary*
- *Edit Zone Boundary*
- *List Zones*
- *View Zone Detail*
- *Import Zone Boundary*
- *Preview Zone Coverage*

**Context / notes:** Route enters ordered zones; stop on route iff it falls in an entered zone; stop created/reused from package recipient address at intake; path calculated from zone order then shorter-path check. Sources: `.context/sessions/courier-ops/cdd-sketch.md`.
