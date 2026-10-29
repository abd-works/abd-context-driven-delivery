---
name: harness-catalog-generator-configure-project-approach
description: >-
  Build a project-specific ``cdd-approach.html`` slide from example artifacts.
  
  project_root={project_root}
  out_root={out_root or '{project_root}/catalog'}
  example_paths={example_paths or 'discover from project tree'}
  
  Each example lands in one practice × stage slot on the approach page.
  Use the same layout as ``catalog/cdd-approach.html``.
  
  **Slots**
  
  | Practice | Discovery | Specification | Implementation |
  | --- | --- | --- | --- |
  | stories | story map (``.drawio`` / image) | scenarios (``.md``) | acceptance / story tests (``.test.ts``) |
  | ddd | bounded-context diagram | aggregate model (``domain-model``) | tactics code |
  | ux | information architecture | mockup (``.html`` / image) | front-end code |
  | clean_engineering | module map / module-context | model diagram / doc | code sample |
  | bdd | — | behavior spec | development tests |
  
  **Step 1 — Collect examples**
  
  Read every path in ``example_paths``. When the list is empty, walk
  ``stories/``, ``domain/``, and ``ux/`` for drawio, markdown, html, and
  test files. Prefer the highest-fidelity artifact that matches the slot.
  
  **Step 2 — Classify each file**
  
  Use file names and folder context:
  
  - ``story-map``, ``story_map`` → stories · discovery
  - ``scenarios``, ``story-scenarios`` → stories · specification
  - ``*_story.test.ts``, ``acceptance`` → stories · implementation
  - ``bounded-context`` → ddd · discovery
  - ``domain-model``, ``ce-domain-model``, ``building-blocks`` → ddd · specification
  - ``*-model.ts`` under ``domain/`` → ddd · implementation
  - ``information-architecture`` → ux · discovery
  - ``mockup/`` html → ux · specification
  - ``front-end``, ``components/`` → ux · implementation
  
  When two files compete for one slot, keep the one whose path and
  content best match the row above. Ask only when classification is
  genuinely ambiguous.
  
  **Step 3 — Confirm the mapping**
  
  Show a short table: practice, stage, relative path. Edit until every
  row the user cares about is filled.
  
  **Step 4 — Generate**
  
  Build ``examples_json`` from the confirmed mapping:
  
  ```json
  {{"examples": {{"stories": {{"discovery": "stories/story-map.drawio", ...}}}}}}
  ```
  
  Call ``generate_project_approach`` with ``project_root``, ``out_root``,
  ``project_title``, ``repo_url``, and ``examples_json``.
---

Build a project-specific ``cdd-approach.html`` slide from example artifacts.

project_root={project_root}
out_root={out_root or '{project_root}/catalog'}
example_paths={example_paths or 'discover from project tree'}

Each example lands in one practice × stage slot on the approach page.
Use the same layout as ``catalog/cdd-approach.html``.

**Slots**

| Practice | Discovery | Specification | Implementation |
| --- | --- | --- | --- |
| stories | story map (``.drawio`` / image) | scenarios (``.md``) | acceptance / story tests (``.test.ts``) |
| ddd | bounded-context diagram | aggregate model (``domain-model``) | tactics code |
| ux | information architecture | mockup (``.html`` / image) | front-end code |
| clean_engineering | module map / module-context | model diagram / doc | code sample |
| bdd | — | behavior spec | development tests |

**Step 1 — Collect examples**

Read every path in ``example_paths``. When the list is empty, walk
``stories/``, ``domain/``, and ``ux/`` for drawio, markdown, html, and
test files. Prefer the highest-fidelity artifact that matches the slot.

**Step 2 — Classify each file**

Use file names and folder context:

- ``story-map``, ``story_map`` → stories · discovery
- ``scenarios``, ``story-scenarios`` → stories · specification
- ``*_story.test.ts``, ``acceptance`` → stories · implementation
- ``bounded-context`` → ddd · discovery
- ``domain-model``, ``ce-domain-model``, ``building-blocks`` → ddd · specification
- ``*-model.ts`` under ``domain/`` → ddd · implementation
- ``information-architecture`` → ux · discovery
- ``mockup/`` html → ux · specification
- ``front-end``, ``components/`` → ux · implementation

When two files compete for one slot, keep the one whose path and
content best match the row above. Ask only when classification is
genuinely ambiguous.

**Step 3 — Confirm the mapping**

Show a short table: practice, stage, relative path. Edit until every
row the user cares about is filled.

**Step 4 — Generate**

Build ``examples_json`` from the confirmed mapping:

```json
{{"examples": {{"stories": {{"discovery": "stories/story-map.drawio", ...}}}}}}
```

Call ``generate_project_approach`` with ``project_root``, ``out_root``,
``project_title``, ``repo_url``, and ``examples_json``.

Use MCP tool: `catalog.configure_project_approach(project_root: 'str', example_paths: 'list[str] | None' = None, out_root: 'str' = '')`
