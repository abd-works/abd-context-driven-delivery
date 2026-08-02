# UX scanners

**Purpose:** Cross-format UX rules that load a `Workspace` and judge the canonical model (never file syntax).

**Seam:** `UxWorkspaceScanner` subclasses discovered via `ScannerCollection` under the UX package

**Dependencies:** `scanners.Scanner` / `ScannerCollection`; `Workspace` from ux_model

**Public API:** Scanner classes with `scan_workspace` — tab states, story budget, named regions, domain terms, story/domain JS imported
