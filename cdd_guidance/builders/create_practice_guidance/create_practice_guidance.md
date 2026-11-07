# Instructions

Build or patch a **PracticeGuidance** domain — a `@agent_toolset` subclass of `PracticeGuidance` under `cdd_guidance/practices/`. The guidance stack lives in **`harness/guidance/`** (`Guidance`, `PracticeGuidance`, `FidelityGuidance`). Scaffolds for new practices live in this builder (`templates/`, `_examples/`). Do not add new practices under `harness/` except through this kit.

Scaffold from **`cdd_guidance/builders/create_practice_guidance/templates/`** (all files, no format filter). Match **`cdd_guidance/builders/create_practice_guidance/_examples/car_chronicle/`** (minimal extension), **`practices/stories/`**, **`practices/bdd/`**, and **`practices/clean_engineering/`** as reference domains. Read **`harness/guidance/AGENTS.md`** for invariants (render, rules injection, skill/MCP copy, companion CE).

Lifecycle actions (**generate**, **repair**, **validate**, **grill**, **sketch**, **iterate**) are **Guidance actions** — pass the practice on the `guidance` argument (e.g. `guidance: [cdd_guidance.practices.stories.stories:Stories]`). They are not methods on `PracticeGuidance`.

Every scaffold pass ends with **validate** on the new or patched practice folder.

---
# Overview
## Favour defaults

- **`favour-defaults`** — `PracticeGuidance` already assembles **overview**, **guidance**, **shared rules**, **fidelities**, **templates** (active format), **examples**, and optional **`model/{format}/`** adapters from `{domain}/{domain}.md` and co-located files. **Do not override** `module_dir`. Put the `.py` module inside the practice folder (`practices/stories/stories.py` is the model). **Do not** re-implement `instructions`, `scoped_markdown`, or `render`. Use **`PracticeGuidance.render`**, and pass `formats=` to `super().__init__` when the practice owns its formats' parse and render adapters; otherwise render defers to the active fidelity’s Clean Engineering companion. The session a practice works in gives it its folder and the places each fidelity writes; `space/session/.context/module-context.md` describes the session's folder, its workpath, and each practice's folder in it. The Partition action (`cdd_guidance/actions/partition/partition.md`) indexes a source by the **Scaffold** subsection of the practice's current fidelity, so write one for every fidelity: it says what the index lists.

## Minimal Python module

- **`minimal-python-module`** — Domain `.py` is thin: `@agent_toolset`, `class Domain(PracticeGuidance):`, class docstring `"""# Instructions"""` (builder/agent entry — detailed prose lives in `{domain}.md`). Pass **`fidelity`**, **`format`**, and optional **`default_workspace_folder`** / **`formats`** through `super().__init__(...)`. Take no `path` or `session`: the session that works on the practice gives it its folder, so a practice built with its own would write somewhere the session does not know. Write no instruction members and no `context_index_key` class attribute — `PracticeGuidance` reads the instructions from `{domain}.md` and keys the practice by its folder name (`PracticeGuidance.context_index_key`). Add **`@agent_tool`** / **`@Hook`** members only when the practice owns tools; **`inject_rules`** must appear on `tools` if chat edits should load practice rules.

## Canonical practice markdown

- **`canonical-practice-markdown`** — All practice prose lives in **`{domain-slug}.md`** with **`## Overview`**, **`## Guidance`**, **`## Shared rules`**, and **`## Fidelities`** (per-fidelity `#### Guidance`, `#### Rules`, optional `default_format` / `stage` YAML). Criteria are named bullets under Overview or fidelity Rules. **No** `reference/` folder duplicating action kits. **No** copying kit action prose into the practice md.

## Compose other guidance in plain code

- **`compose-like-normal-code`** — To use another practice or toolset, construct it directly (`from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering`). **No** `ToolsetLoader` for in-repo types. Prefer **Guidance actions** with multiple `guidance` entries over duplicating generate/repair bodies on the practice class.

## Underscore folders and imports

- **`underscore-folder-imports`** — Practice folders use underscores (`practices/clean_engineering/`) matching the Python import path. Hyphens in folder names break imports — avoid them.

## Fidelity outputs

- **`outputs-relative-to-the-session`** — Declare each fidelity's `outputs` as paths relative to the session's folder, with no `root`. Put `markdown` and `drawio` under `.context/` and code straight in the folder, because the session decides where work lives and a declared root would send every session's artifacts to one place in the repository.

## Practice folder layout

- **`domain-folder-layout`** — One folder per practice. The `.py` module lives **inside** that folder (e.g. `practices/agent_bdd/agent_bdd.py`, `builders/create_practice_guidance/_examples/car_chronicle/car_chronicle.py`). Same folder holds `{domain-slug}.md`, `_examples/examples.md`, optional `templates/` (artifact templates), optional `model/{format}/`, optional `scanners/`. Repair fixtures: `_examples/<descriptive-folder>/faultyAsset` and `repairedAsset`.

## Scaffold vs patch

- **`scaffold-vs-patch`** — Folder missing or empty → create full tree from **`builders/create_practice_guidance/templates/`**. Files already exist → add only missing pieces; **do not** overwrite good content or rebuild from scratch unless asked.

## Do not duplicate content

- **`do-not-duplicate-content`** — Do not re-create markdown the guidance layer already loads. Do not add parallel prose files for sections `PracticeGuidance` already resolves from `{domain}.md`. **Patch surgically** when fixing a practice.

## PracticeGuidance class module

- **`practice-guidance-class-module`** — `from harness.guidance.guidance import PracticeGuidance` and `from harness.agent_tools.agent_tools import agent_toolset`. Class docstring: `"""# Instructions"""`. **Subclass** `PracticeGuidance` (`class Domain(PracticeGuidance):`). The installer and the catalog find the practice through `@agent_toolset`, so it needs no other mark.

## Format templates vs scaffold templates

- **`format-vs-scaffold-templates`** — **`builders/create_practice_guidance/templates/`** = meta scaffolds for **building new practices** (Python + md + examples); loaded through this builder’s `templates` section, **no format filter**. **`templates/`** inside each practice = artifact templates for generate/satisfy (format-aware). **`model/{format}/`** = parse/render adapters, named by the practice's `formats=`.

## Reference extension example

- **`reference-extension-example`** — **`builders/create_practice_guidance/_examples/car_chronicle/`** shows a minimal practice: `car_chronicle.py` beside `car_chronicle.md`, `car_chronicle-templates.md`, `_examples/examples.md`, repair fixtures, and **`output/`** with sample generated artifact (`output/driving-log.md`).

## Examples and repair fixtures

- **`examples-and-fixtures`** — `_examples/examples.md` for worked samples. Pair faulty/repaired assets under `_examples/<rule-or-scenario>/` for repair regression; see the repair action, `cdd_guidance/actions/improvement/repair.md`.

---
# Generate

1. Read § Overview and **`harness/guidance/AGENTS.md`**.
2. Read reference practices (`stories`, `bdd`, `clean_engineering`) and **`_examples/car_chronicle/`**.
3. Scaffold from **`templates/`**; fill every `{Placeholder}`.
4. Place the new tree under **`cdd_guidance/practices/{domain_slug}/`** (or patch an existing folder).
5. Run **validate** on the practice.
