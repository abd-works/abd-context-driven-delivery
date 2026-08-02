# ux_model (canonical UX map)

**Purpose:** Canonical in-memory UX model — `UxMap` → screens → regions → controls/interactions, plus transitions, nav, content types, and layout catalog.

**Seam:** Shared model for all UX channels and scanners (parse into / render from this tree)

**Dependencies:** None outside this package for the core tree; channels and scanners consume it

**Public API:** `UxMap`, `Screen`, `Region`, `Control`, `StoryDemoControl`, `Transition`, `Workspace`, `layouts` helpers, `ReferencePaths`
