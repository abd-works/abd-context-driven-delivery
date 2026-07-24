# Instructions

Build or patch a **Context domain** — a `@context` toolset under `contexts/` beside `contexts/base/` (Context framework: `context.py`, `base-context/` action prose, `templates/`, `examples/`), not inside `base/`.

Scaffold from **`contexts/base/templates/`** (all files, no format filter). Match **`contexts/base/examples/car_chronicle/`** (minimal extension demo), **`contexts/clean_engineering/`**, and **`contexts/bdd/`** / **`contexts/agent_bdd/`** as reference domains.

Every domain action ends with **validate**.

---
# Contexts

## Favour defaults

- **`favour-defaults`** — The framework (`Context`, `@instruction` slots, action docstrings → `contexts/base/*.md` / domain md) already wires contexts, domain § Generate, examples, format template, and action prose. **Do not override** instruction slots or action docstrings. **Do not override `module_dir`** — put the `.py` file inside the domain folder; default resolution is enough (`contexts/agent_bdd/agent_bdd.py` is the model). Override **action bodies** only to add steps (e.g. compose another toolset). Shared surface also includes **`partition` / `index` / `segment`** (thin corpus partitioning) and optional domain **`partition.md`** (top-level artifacts only; base default if missing). Partition is a **hard fail** if domain `partition.md` / `{domain}.md` § Contexts are ignored or the index mirrors corpus TOC/chapters. **Multi-pass is additive:** later lenses (Stories / UX / BDD / CE) **add columns** mapped to existing `{module}/.context/*-segment.md` chunks — they must not wipe the shared `{subject}-index.md` or re-chunk the corpus (see `base-context/partition.md`).

## Session path

- **`session-path`** - Every generator exposes a **`session`** resource (a `Session` object). Constructor kwargs: `path` (working area, default `"."`) and `session` (bout slug). On `tools run`, pass `context.path` / `context.session`. **Hard layout:**
  - **`session.path`** - durable working area:
    - Partition index / durable diagrams -> `{session.path}/.context/`
    - Partitioned chunks + module-local docs -> `{session.path}/{module}/.context/` (e.g. `{session.path}/checks/.context/checks-segment.md`)
    - Generated code and module folders -> `{session.path}/` (e.g. `{session.path}/checks/`)
  - **`session.folder`** - named process bout under `{session.path}/.context/sessions/{name}/` (session.md, grill-answers, engagement sketches, handoff). Create via `create_session` after confirming path and slug with the user.
- Sketch / grill / iterate / handoff for engagement process work **default to `session.folder`**. Partition `out_root` and durable corpus docs default toward **`session.path`**. Do not invent a divergent working folder.

## Minimal Python module

- **`minimal-python-module`** - Domain `.py` is thin: `@context`, `"""Instructions section"""` (framework Instructions marker), `__init__(format=..., path=..., session=...)`, and optional `@action` body overrides. **No** duplicated `@instruction(override=True)` for `contexts`, `template`, or framework action docstrings (`"""generate"""`, `"""repair"""`, ...). Empty docstring on an overridden action is fine - framework prose resolves from the action name. Pass `path` and `session` through to `super().__init__(..., path=path, session=session)`. Inherit peer entry points from base Context: **`generate`** (plain), **`grill`**, **`sketch`**, **`iterate`** — do not re-decorate domain `generate` with `@grill_with_context` / `@sketch` / `@iterate`.

## Canonical markdown only

- **`canonical-markdown-only`** — All domain prose lives in **`{domain-slug}.md`**: § Instructions, § Contexts, § Generate. **No** `reference/` folder, **no** duplicate `reference/generate.md`, **no** copying framework action prose into the domain md. Criteria live as named bullets under § Contexts.

## Compose other toolsets in plain code

- **`compose-like-normal-code`** — To inline another toolset's action, call it on an instance: `self._clean_engineering().generate()`. **No** `ToolsetLoader` for in-repo toolsets — **direct import** (`from contexts.clean_engineering.clean_engineering import CleanEngineering`). **No** `delegate_action`, **No** `Instruction.ref` overrides for contexts/base/examples/template unless the other toolset is truly external. Actions inline; tools go on the tools list.

## Hyphen folders and imports

- **`underscore-folder-imports`** — Domain folders use underscores (`contexts/clean_engineering/`, `contexts/agent_bdd/`) matching the Python import path. Hyphens in folder names break `__import__` and require fallback loader workarounds — avoid them.

## Domain folder layout

- **`domain-folder-layout`** — One folder per domain. The `.py` module lives **inside** that folder (e.g. `contexts/agent_bdd/agent_bdd.py`, `contexts/base/examples/car_chronicle/car_chronicle.py`). Same folder holds `{domain-slug}.md`, `examples/examples.md`, optional `formats/{format}/{domain-slug}-template.*`, optional `scanners/`. Repair fixtures: `examples/<descriptive-folder>/faultyAsset` and `repairedAsset`. **Never** park Python beside the folder and override `module_dir` to point at it — that is a layout smell.

## Scaffold vs patch

- **`scaffold-vs-patch`** — Folder missing or empty → create full tree from **`contexts/base/templates/`**. Files already exist → add only missing pieces; **do not** overwrite good content or rebuild from scratch unless asked.

## Do not duplicate content

- **`do-not-duplicate-content`** — Do not re-create markdown the framework already loads. Do not copy `contexts/base/generate.md` into the domain. Do not add parallel prose files for slots the base class already resolves. **Patch surgically** when fixing a domain.

## Context class module

- **`context-class-module`** — Line 1: `# @toolset-manifest python -m tools manifest <module>:<Class>`. Class docstring: `"""§ Instructions"""`. Re-export `action` and `concept` only when needed. **Do not** subclass `Context` in source — `@context` merges it. Framework lives at **`contexts/base/`** (`contexts.base.context:Context`).

## Format templates vs scaffold templates

- **`format-vs-scaffold-templates`** — **`contexts/base/templates/`** = meta scaffolds for **building new domains** (Python + md + examples); loaded via `templates` slot, **no format filter**. **`formats/{format}/`** in each domain = artifact templates for generate/satisfy; loaded via `template` slot with active `format`.

## Reference extension example

- **`reference-extension-example`** — **`contexts/base/examples/car_chronicle/`** shows a complete context extension: `car_chronicle.py` beside `car_chronicle.md`, `{domain-slug}-templates.md`, `examples/examples.md`, repair fixtures, and **`output/`** with sample generated artifact (`output/driving-log.md`). No `module_dir` override — the class module and markdown share one folder.

## Examples and repair fixtures

- **`examples-and-fixtures`** — `examples/examples.md` for worked samples. Pair faulty/repaired assets under `examples/<rule-or-scenario>/` for repair regression; see `contexts/base/repair.md`.
