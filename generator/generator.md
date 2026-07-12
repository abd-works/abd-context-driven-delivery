# Instructions

Build or patch a **Generator domain** — a `@generator_class_annotation` toolset beside `generator/`, not inside it.

Scaffold from **`generator/templates/`** (all files, no format filter). Match **`generator/examples/car_chronicle/`** (minimal extension demo), **`clean-code/`**, and **`agent_bdd/`** as reference domains.

Every domain action ends with **validate**.

---
# Concepts

## Favour defaults

- **`favour-defaults`** — The framework (`Generator`, `@instruction` slots, action docstrings → `generator/*.md`) already wires concepts, rules, domain § Generate, examples, format template, and action prose. **Do not override** instruction slots or action docstrings. **Do not override `module_dir`** — put the `.py` file inside the domain folder; default resolution is enough (`agent_bdd/agent_bdd.py` is the model). Override **action bodies** only to add steps (e.g. compose another toolset).

## Minimal Python module

- **`minimal-python-module`** — Domain `.py` is thin: `@generator_class_annotation`, `"""§ Instructions"""`, `__init__(format=...)`, and optional `@action` body overrides. **No** duplicated `@instruction(override=True)` for `rules`, `concepts`, `template`, or framework action docstrings (`"""generate"""`, `"""repair"""`, …). Empty docstring on an overridden action is fine — framework prose resolves from the action name.

## Canonical markdown only

- **`canonical-markdown-only`** — All domain prose lives in **`{domain-slug}.md`**: § Instructions, § Concepts, § Generate. **No** `reference/` folder, **no** duplicate `reference/generate.md`, **no** copying framework action prose into the domain md. Optional **`rules/*.md`** for scanner-aligned rule files; the `rules` slot finds the folder automatically.

## Compose other toolsets in plain code

- **`compose-like-normal-code`** — To inline another toolset's action, call it on an instance: `self._clean_code().generate()`. **No** `ToolsetLoader` for in-repo toolsets — **direct import** (`from clean_code.clean_code import CleanCode`). **No** `delegate_action`, **No** `Instruction.ref` overrides for concepts/examples/template unless the other toolset is truly external. Actions inline; tools go on the tools list.

## Hyphen folders and imports

- **`hyphen-folder-imports`** — Domain folders use hyphens (`clean-code/`, `agent-bdd/`). Python import path uses underscores (`clean_code.clean_code`). Register once in domain `conf.py` via `ensure_hyphenated_import` if needed — not at every call site.

## Domain folder layout

- **`domain-folder-layout`** — One folder per domain. The `.py` module lives **inside** that folder (e.g. `agent_bdd/agent_bdd.py`, `generator/examples/car_chronicle/car_chronicle.py`). Same folder holds `{domain-slug}.md`, `examples/examples.md`, optional `rules/`, optional `formats/{format}/{domain-slug}-template.*`, optional `scanners/`. Repair fixtures: `examples/<descriptive-folder>/faultyAsset` and `repairedAsset`. **Never** park Python beside the folder and override `module_dir` to point at it — that is a layout smell.

## Scaffold vs patch

- **`scaffold-vs-patch`** — Folder missing or empty → create full tree from **`generator/templates/`**. Files already exist → add only missing pieces; **do not** overwrite good content or rebuild from scratch unless asked.

## Do not duplicate content

- **`do-not-duplicate-content`** — Do not re-create markdown the framework already loads. Do not copy `generator/base-generator/generate.md` into the domain. Do not add parallel prose files for slots the base class already resolves. **Patch surgically** when fixing a domain.

## Generator class module

- **`generator-class-module`** — Line 1: `# @toolset-manifest python -m tools manifest <module>:<Class>`. Class docstring: `"""§ Instructions"""`. Re-export `action` and `generator_class_annotation` only when needed. **Do not** subclass `Generator` in source — the decorator merges it.

## Format templates vs scaffold templates

- **`format-vs-scaffold-templates`** — **`generator/templates/`** = meta scaffolds for **building new domains** (Python + md + examples); loaded via `templates` slot, **no format filter**. **`formats/{format}/`** in each domain = artifact templates for generate/satisfy; loaded via `template` slot with active `format`.

## Reference extension example

- **`reference-extension-example`** — **`generator/examples/car_chronicle/`** shows a complete generator extension: `car_chronicle.py` beside `car-chronicle.md`, `{domain-slug}-template.md`, `examples/examples.md`, repair fixtures, and **`output/`** with sample generated artifact (`output/driving-log.md`). No `module_dir` override — the class module and markdown share one folder.

## Examples and repair fixtures

- **`examples-and-fixtures`** — `examples/examples.md` for worked samples. Pair faulty/repaired assets under `examples/<rule-or-scenario>/` for repair regression; see `generator/base-generator/repair.md`.
