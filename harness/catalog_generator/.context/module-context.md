# catalog_generator — module context

## Purpose

Discover-and-render primitives for the CDD HTML catalog (see `catalog/cdd-catalog-plan.md` / `catalog/cdd-catalog-sketch.md`). Wraps the real object model directly — the practice catalogue's `PracticeGuidance` and `FidelityGuidance`, and each action kit's `AgentTool`s — there is no separate scraped schema and no parallel data hierarchy.

Implements all four epics from the sketch's story map: Assemble Catalog Page Data (discover), Render Self-Contained Catalog Pages (the Clean Engineering pass's six render classes), Make Catalog Output Portable, and Configure Illustrated Examples (mechanism only — see the plan's `illustrated-examples` todo for the outstanding content-authoring half).

## Primary use case

`generate_cdd_catalog.py` builds the six render classes over a `Catalog(...)` and calls `.generate_catalog()`. Run it from the repo root:

```
python -m harness.catalog_generator.generate_cdd_catalog
```

Defaults `--out cdd_guidance/catalog`, `--repo-url` from `git remote get-url origin`, `--ref` from current `HEAD`; all three are overridable flags.

## Public API

**Discover (Assemble Catalog Page Data):**
- `catalog_practices() -> list[CatalogPractice]` — every practice in `PracticeCatalogue` with a fidelity on the board, in the order of each practice's `catalog_card`. A `CatalogPractice` wraps the live `PracticeGuidance`: its card (name, label, colour family), its fidelities, `fidelity_in(column)`, its page links, and the practice guide's practice-level sections. Every page, board row, and grid card reads it, so nothing is copied into module globals.
- `catalog_utilities() -> list[RegistryEntry]` — resolves `UTILITY_REGISTRY` to real classes; import failure is a hard fail, not a silent gap. A class marked `@noCatalog` is left out. The mark does not change install or deploy.
- `STAGE_COLUMNS` (in `foundry_chrome`) — the board's stage columns. Each `StageColumn` pairs a fidelity stage (`specification`) with its board key in the page markup and scripts (`spec`), its heading, its scope shape, and the words template front matter uses for it. It is the only place a stage meets its board key.
- `noCatalog` — decorator on a class, fidelity, or operation. The catalog skips it (registry row, fidelity page, lifecycle action). `@Skill`, `@Command`, `@Mcp`, and `@Hook` on the same target still deploy. The utility registry classes carry `@noCatalog` until they are ready to show. `@noDeploy` is the install mark; it lives on the operation and does not change catalog inclusion.
- Fidelity pages come from the practice's live fidelities: `practice.fidelities.entries`, less any marked `@noCatalog`. Each `FidelityGuidance` gives its `name`, `default_format`, `overview`, and `section`, its whole `### {fidelity}` block. `CatalogFidelity.generate_catalog(practice, fidelity)` renders from that object rather than copies of its fields, so a page shows exactly what the guidance holds.
- `resolve_lifecycle_actions() -> list[LifecycleAction]` — `LIFECYCLE_ACTIONS` is the one list of lifecycle actions, each naming the action kit class that owns it. An action is shown when its kit has a live tool of that name not marked `@noCatalog`; its folder is the kit's folder.
- `SkillSlashName(skills_roots).resolve(module_dir_name) -> str | None` — reads the deployed SKILL.md frontmatter `name:` field from `.claude/skills/{category}-{name}/` (Claude joins the category into the folder name, e.g. `practices-stories`) or `.cursor/skills/{category}/{name}/`; tries the hyphenated form too (`clean_engineering` → `practices-clean-engineering`).

**Render (Render Self-Contained Catalog Pages — Clean Engineering pass):** `CatalogTool`, `CatalogAction`, `CatalogFidelity`, `CatalogContextTool`, `CatalogUtility`, `Catalog` — each renderer is built once with what every page shares and exposes one `generate_catalog(...)` operation that renders the live object it is given (a `LifecycleAction`, a `CatalogPractice` and its fidelity, a utility's `RegistryEntry`); nothing is copied into a renderer between pages. `Catalog.generate_catalog(...)` is the only entry point `generate_cdd_catalog.py` calls; it writes every page under its `out_root`, including `workflow.html` rendered from `catalog/workflow.md` and linked from the hub body beneath the board.

**Portability (Make Catalog Output Portable):**
- `git_blob_url` / `git_blob_url_for_callable` — the single seam every citation goes through; never a local filesystem path.
- `resolve_repo_remote` / `normalize_repo_url` — the CLI's zero-flag defaults.
- `write_page` — writes one page's already-literal HTML under `out_root`; no runtime fetch back into `practices/`/`tools/`.
- `build_run_request` / `dump_run_request_yaml` / `write_raw_manifests` — at generate time, read each context tool's live `Cls.manifest` signature and write request YAML under `manifests/{tool}/`.

**Illustrated examples (Configure Illustrated Examples):**
- `parse_illustrated_examples`, `extract_whole_file`, `extract_heading_section`, `extract_comment_tag`, `resolve_illustrated_example` (dispatches by anchor shape).

## Seam

`Catalog` is the deployed toolset (`harness.catalog_generator.catalog_generator:Catalog`). `Catalog.generate_catalog` carries `@prompt(name="generate-catalog")` — slash `/generate-catalog`, not a catalog skill. `CatalogAction` (and the other `generate_catalog` helpers) are page renderers, not IDE files.

Reads real files/classes; `write_page` is the only place it writes, and only under `out_root`. CLI: `python -m harness.catalog_generator.generate_cdd_catalog`.

## Dependencies

stdlib only (`ast`, `importlib`, `inspect`, `re`, `subprocess`, `pathlib`, `dataclasses`) plus the real `practices.*` / utility classes it discovers and instantiates at call time.
