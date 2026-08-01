# Instructions

Build or patch a **BaseContextTool domain** — a subclass under `context_tools/` beside `context_tools/base/`. Lifecycle + composer live in `base_context_tool.py` (kit action prose beside peer kits / base); scaffolds live in this CreateContextTool domain (`templates/`, `examples/`). Do not put new domains inside `base/` except under `create_context_tool/`.

Scaffold from **`context_tools/create_context_tool/templates/`** (all files, no format filter). Match **`context_tools/create_context_tool/examples/car_chronicle/`** (minimal extension demo), **`context_tools/clean_engineering/`**, and **`context_tools/bdd/`** / **`context_tools/agent_bdd/`** as reference domains.

Every domain action ends with **validate**.

---
# Contexts

## Favour defaults

- **`favour-defaults`** — The framework (`BaseContextTool`, `@instruction` slots, bare action/tool names → kit `{slug}.md` **sections** or `{name}.md` beside the defining peer kit / domain md) already wires contexts, domain § Generate, examples, format template, and action prose. **Do not override** instruction slots or action docstrings. **Do not override `module_dir`** — put the `.py` file inside the domain folder; default resolution is enough (`context_tools/agent_bdd/agent_bdd.py` is the model). Override **action bodies** only to add steps (e.g. compose another toolset). Session / workspace layout and tools live in **`utilities/sessions/workspace_session.md`**. Shared surface also includes **`partition` / `index` / `segment`** (prose in `utilities/partition_pipeline/partition_pipeline.md`) and optional domain **`partition.md`** (top-level artifacts only; base default if missing). Partition is a **hard fail** if domain `partition.md` / `{domain}.md` § Contexts are ignored or the index mirrors corpus TOC/chapters. **Multi-pass is additive:** later lenses (Stories / UX / BDD / CE) **add columns** mapped to existing `{module}/.context/*-segment.md` chunks — they must not wipe the shared `{subject}-index.md` or re-chunk the corpus (see **Partition** in `partition_pipeline.md`).

## Minimal Python module

- **`minimal-python-module`** - Domain `.py` is thin: `class Domain(BaseContextTool):`, `"""Instructions section"""` (framework Instructions marker), class attrs **`default_workspace_folder`** + **`context_index_key`**, `__init__(format=..., path=..., session=..., workspace=...)`, and optional `@action` body overrides. **No** duplicated `@instruction(override=True)` for `contexts`, `template`, or framework action docstrings (`"""generate"""`, `"""repair"""`, ...). Empty docstring on an overridden action is fine - framework prose resolves from the action name. Pass `path` and `session` through to `super().__init__(..., path=path, session=session)`. Inherit peer entry points from BaseContextTool: **`generate`** (plain), **`grill`**, **`sketch`**, **`iterate`** — do not re-decorate domain `generate` with `@grill_with_context` / `@sketch` / `@iterate`.

## Canonical markdown only

- **`canonical-markdown-only`** — All domain prose lives in **`{domain-slug}.md`**: § Instructions, § Contexts, § Generate. **No** `reference/` folder, **no** duplicate `reference/generate.md`, **no** copying framework action prose into the domain md. Criteria live as named bullets under § Contexts.

## Compose other toolsets in plain code

- **`compose-like-normal-code`** — To inline another toolset's action, call it on an instance: `self._clean_engineering().generate()`. **No** `ToolsetLoader` for in-repo toolsets — **direct import** (`from context_tools.clean_engineering.clean_engineering import CleanEngineering`). **No** `delegate_action`, **No** `Instruction.ref` overrides for create_context_tool examples/template unless the other toolset is truly external. Actions inline; tools go on the tools list.

## Hyphen folders and imports

- **`underscore-folder-imports`** — Domain folders use underscores (`context_tools/clean_engineering/`, `context_tools/agent_bdd/`) matching the Python import path. Hyphens in folder names break `__import__` and require fallback loader workarounds — avoid them.

## Domain folder layout

- **`domain-folder-layout`** — One folder per domain. The `.py` module lives **inside** that folder (e.g. `context_tools/agent_bdd/agent_bdd.py`, `context_tools/create_context_tool/examples/car_chronicle/car_chronicle.py`). Same folder holds `{domain-slug}.md`, `examples/examples.md`, optional `formats/{format}/{domain-slug}-template.*`, optional `scanners/`. Repair fixtures: `examples/<descriptive-folder>/faultyAsset` and `repairedAsset`. **Never** park Python beside the folder and override `module_dir` to point at it — that is a layout smell.

## Scaffold vs patch

- **`scaffold-vs-patch`** — Folder missing or empty → create full tree from **`context_tools/create_context_tool/templates/`**. Files already exist → add only missing pieces; **do not** overwrite good content or rebuild from scratch unless asked.

## Do not duplicate content

- **`do-not-duplicate-content`** — Do not re-create markdown the framework already loads. Do not copy `base_context_tool.md` § Generate into the domain. Do not add parallel prose files for slots the base class already resolves. **Patch surgically** when fixing a domain.

## BaseContextTool class module

- **`base-context-tool-class-module`** — Line 1: `# @toolset-manifest python -m tools manifest <module>:<Class>`. Class docstring: `"""§ Instructions"""`. **Subclass** `BaseContextTool` directly (`class Domain(BaseContextTool):`). Framework lives at **`context_tools/base/`** (`context_tools.base.base_context_tool:BaseContextTool`).

## Format templates vs scaffold templates

- **`format-vs-scaffold-templates`** — **`context_tools/create_context_tool/templates/`** = meta scaffolds for **building new domains** (Python + md + examples); loaded via `templates` slot, **no format filter**. **`formats/{format}/`** in each domain = artifact templates for generate/satisfy; loaded via `template` slot with active `format`.

## Reference extension example

- **`reference-extension-example`** — **`context_tools/create_context_tool/examples/car_chronicle/`** shows a complete context extension: `car_chronicle.py` beside `car_chronicle.md`, `{domain-slug}-templates.md`, `examples/examples.md`, repair fixtures, and **`output/`** with sample generated artifact (`output/driving-log.md`). No `module_dir` override — the class module and markdown share one folder.

## Examples and repair fixtures

- **`examples-and-fixtures`** — `examples/examples.md` for worked samples. Pair faulty/repaired assets under `examples/<rule-or-scenario>/` for repair regression; see `utilities/repair/repair.md`.
