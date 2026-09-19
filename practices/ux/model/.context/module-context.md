# ux_model (canonical UX map)

**Purpose:** Canonical in-memory UX model — `UxMap` → screens → regions → controls/interactions, plus transitions, nav, and content types.

**Seam:** Shared model for all UX channels and scanners (parse into / render from this tree)

**Dependencies:** None outside this package for the core tree; channels and scanners consume it

**Public API:** `UxMap`, `Screen` (`apply_layout` sets the layout name only - no seeded regions), `Region`, `Control`, `StoryDemoControl`, `Transition`, `Workspace`, `ReferencePaths`. Layout vocabulary lives as reference files at `../specifications/generic/` (plus branded siblings under `../specifications/`), not as a code catalog.
