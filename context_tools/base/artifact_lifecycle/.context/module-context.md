# ArtifactLifecycle

**Purpose:** ContextTool-only lifecycle — generate / validate / satisfy / document + thin grill/sketch/iterate wrappers.

**Seam:** ArtifactLifecycle

**Public API:** `generate`, `validate`, `satisfy`, `document`, `generate_output`, `add_generate_header_to_generated`, `grill`, `sketch`, `iterate`; instruction slots `generate_instructions`, `document_instructions`, `examples`, `templates`

**Dependencies:** (none)

**Mechanism:** Concrete mergeable class under `context_tools/base/` (one test tier — no separate interface). Engagement engines stay in utilities via decorators. Lifecycle instruction slots live here and merge into ContextTool.
