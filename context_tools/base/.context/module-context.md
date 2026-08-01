# BaseContextTool (composer + lifecycle)

**Purpose:** Shared base for every concrete context domain — partition/repair peers + generate/validate/satisfy/document (+ grill/sketch/iterate). Domains subclass it directly.

**Seam:** BaseContextTool

**Public API:** `module_dir`; kit providers (`workspace`, `scanner`, `sketcher`, `grill_context`, `iterator`, `decisions`); forwarded session/scan tools; lifecycle actions

**Dependencies:** Session (composed via `workspace()`), Scan (composed instances); PartitionPipeline, Repair (MI peers); Sketcher, GrillContext, Iterator, RecordDecisions (composed)

**Mechanism:** Providers return **real kit instances** (`Session(...)`, `Scan()`, …) — never `self`. Lifecycle bodies call `self.workspace().…` / `self.scanner().…`. Host `@tool`/`@resource` methods are thin forwards for agent CLI. `@action` / `@instruction` / `@tool` remain (primitives only). Domains are ordinary subclasses of BaseContextTool. Scaffolding new domains is **CreateContextTool**.
