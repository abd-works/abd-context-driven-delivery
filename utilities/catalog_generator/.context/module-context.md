# catalog_generator — module context

## Purpose

Discover-and-render primitives for the CDD HTML catalog (see `[cdd-catalog-plan.md](../../../catalog/cdd-catalog-plan.md)` / `[cdd-catalog-sketch.md](../../../catalog/cdd-catalog-sketch.md)`). Wraps the real object model directly — `Toolset.tools`, `AgenticToolset.actions`, `BaseContextTool.fidelities` — there is no separate scraped schema and no parallel data hierarchy.

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
- `resolve_lifecycle_actions() -> list[ActionResolution]` — AST-walks `BaseContextTool`'s public `@action` methods in source order (currently ten: partition … repair, improve); a peer-kit `(attribute, method)` call pair is an action's delegate only when no *other* action calls that exact pair (two actions may each own a distinct call on the same peer kit without colliding — see `repair`/`improve` both delegating to `Repair`); no unique pair falls back to `context_tools/base/`. Action guides prefer `{action}.md` over `{dirname}.md` so `improve` gets `improve.md` while sharing `utilities/repair/` with `repair`.
- `skill_slash_name(module_dir_name) -> str | None` — reads the deployed `.cursor/skills/{name}/SKILL.md` frontmatter `name:` field; tries the hyphenated form too (`clean_engineering` → `clean-engineering`).

**Render (Render Self-Contained Catalog Pages — Clean Engineering pass):** `CatalogTool`, `CatalogAction`, `CatalogFidelity`, `CatalogContextTool`, `CatalogUtility`, `Catalog` — each one class wrapping one real primitive one-for-one, each exposing exactly one `generate_catalog(...)` operation. `Catalog.generate_catalog(...)` is the only entry point `generate_cdd_catalog.py` calls; it writes every page under its `out_root`.

**Portability (Make Catalog Output Portable):**
- `git_blob_url` / `git_blob_url_for_callable` — the single seam every citation goes through; never a local filesystem path.
- `resolve_repo_remote` / `normalize_repo_url` — the CLI's zero-flag defaults.
- `write_page` — writes one page's already-literal HTML under `out_root`; no runtime fetch back into `context_tools/`/`utilities/`.
- `build_run_request` / `dump_run_request_yaml` / `write_raw_manifests` — at generate time, read each context tool's live `Cls.manifest` signature and write request YAML under `manifests/{tool}/` (plus full `manifest.yaml` front matter and per-action HTML under `manifests/actions/`). Fidelity/action "Raw manifest format →" links point at these files, never at `.py` source.

**Illustrated examples (Configure Illustrated Examples):**
- `parse_illustrated_examples`, `extract_whole_file`, `extract_heading_section`, `extract_comment_tag`, `resolve_illustrated_example` (dispatches by anchor shape).

## Seam

`@tool`-shaped, deterministic, zero agentic judgment points (per the sketch's Clean Engineering grill decision — scrape → render → write is a fixed pipeline, so this module is not itself a `@toolset`/`@action` host; `generate_cdd_catalog.py` just calls it directly). Reads real files/classes; `write_page` is the only place it writes, and only under `out_root`.

## Dependencies

stdlib only (`ast`, `importlib`, `inspect`, `re`, `subprocess`, `pathlib`, `dataclasses`) plus the real `context_tools.*` / utility classes it discovers and instantiates at call time.

## Tests

`catalog_generator_spec.py` (discover, 17 examples), `catalog_generator_render_spec.py` (render, 13 examples), `catalog_generator_portability_spec.py` (5 examples), `catalog_generator_illustrated_examples_spec.py` (5 examples) — 40 acceptance tests total, one `it` per sketch story's single main-flow scenario, plus one extra dispatch test. All green; verified alongside the repo's broader fast (`*_spec.py`, non-agentic) suite with no new regressions.
