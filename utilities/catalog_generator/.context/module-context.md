# catalog_generator — module context

## Purpose

Discover-and-render primitives for the CDD HTML catalog (see `catalog/cdd-catalog-plan.md` / `catalog/cdd-catalog-sketch.md`). Wraps the real object model directly — `Toolset.tools`, `AgenticToolset.actions`, `BaseContextTool.fidelities` — there is no separate scraped schema and no parallel data hierarchy.

Implements all four epics from the sketch's story map: Assemble Catalog Page Data (discover), Render Self-Contained Catalog Pages (the Clean Engineering pass's six render classes), Make Catalog Output Portable, and Configure Illustrated Examples (mechanism only — see the plan's `illustrated-examples` todo for the outstanding content-authoring half).

## Primary use case

`generate_cdd_catalog.py` builds the six render classes over a `Catalog(...)` and calls `.generate_catalog()`. Run it from the repo root:

```
python -m utilities.catalog_generator.generate_cdd_catalog
```

Defaults `--out catalog`, `--repo-url` from `git remote get-url origin`, `--ref` from current `HEAD`; all three are overridable flags.

## Public API

**Discover (Assemble Catalog Page Data):**
- `load_registry() -> (list[RegistryEntry], list[RegistryEntry])` — resolves `CONTEXT_TOOL_REGISTRY` / `UTILITY_REGISTRY` to real classes; import failure is a hard fail, not a silent gap.
- `scrape_fidelities(cls) -> list[FidelityGuidance]` — fidelity key, default format, and `## {fidelity}` guidance body from `{module_dir}/{module_dir.name}.md`; missing heading resolves to a `"Guidance missing"` stub.
- `resolve_lifecycle_actions() -> list[ActionResolution]` — walks `BaseContextTool`'s public `@action` methods in source order; peer-kit action delegates follow unique call pairs.
- `skill_slash_name(module_dir_name) -> str | None` — reads the deployed `.cursor/skills/{name}/SKILL.md` frontmatter `name:` field; tries the hyphenated form too (`clean_engineering` → `clean-engineering`).

**Render (Render Self-Contained Catalog Pages — Clean Engineering pass):** `CatalogTool`, `CatalogAction`, `CatalogFidelity`, `CatalogContextTool`, `CatalogUtility`, `Catalog` — each one class wrapping one real primitive one-for-one, each exposing exactly one `generate_catalog(...)` operation. `Catalog.generate_catalog(...)` is the only entry point `generate_cdd_catalog.py` calls; it writes every page under its `out_root`, including `workflow.html` rendered from `catalog/workflow.md` and linked from the hub body beneath the board.

**Portability (Make Catalog Output Portable):**
- `git_blob_url` / `git_blob_url_for_callable` — the single seam every citation goes through; never a local filesystem path.
- `resolve_repo_remote` / `normalize_repo_url` — the CLI's zero-flag defaults.
- `write_page` — writes one page's already-literal HTML under `out_root`; no runtime fetch back into `context_tools/`/`utilities/`.
- `build_run_request` / `dump_run_request_yaml` / `write_raw_manifests` — at generate time, read each context tool's live `Cls.manifest` signature and write request YAML under `manifests/{tool}/`.

**Illustrated examples (Configure Illustrated Examples):**
- `parse_illustrated_examples`, `extract_whole_file`, `extract_heading_section`, `extract_comment_tag`, `resolve_illustrated_example` (dispatches by anchor shape).

## Seam

`Catalog` is the deployed toolset (`catalog_generator.catalog_generator:Catalog`). `Catalog.generate_catalog` carries `@prompt(name="generate-catalog")` — slash `/generate-catalog`, not a catalog skill. `CatalogAction` (and the other `generate_catalog` helpers) are page renderers, not IDE files.

Reads real files/classes; `write_page` is the only place it writes, and only under `out_root`. CLI: `python -m utilities.catalog_generator.generate_cdd_catalog`.

## Dependencies

stdlib only (`ast`, `importlib`, `inspect`, `re`, `subprocess`, `pathlib`, `dataclasses`) plus the real `context_tools.*` / utility classes it discovers and instantiates at call time.
