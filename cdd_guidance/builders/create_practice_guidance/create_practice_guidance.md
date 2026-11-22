# Instructions

Build or patch a **PracticeGuidance** domain — a `@agent_toolset` subclass of `PracticeGuidance` under `cdd_guidance/practices/`. The guidance stack lives in **`harness/guidance/`** (`Guidance`, `PracticeGuidance`, `FidelityGuidance`). Scaffolds for new practices live in this builder (`templates/`, `_examples/`). Do not add new practices under `harness/` except through this kit.

Scaffold from **`cdd_guidance/builders/create_practice_guidance/templates/`** (all files, no format filter). Match **`cdd_guidance/builders/create_practice_guidance/_examples/car_chronicle/`** (minimal extension), **`practices/stories/`**, **`practices/bdd/`**, and **`practices/clean_engineering/`** as reference domains. Read **`harness/guidance/AGENTS.md`** for invariants (render, rules injection, skill/MCP copy, companion CE).

Lifecycle actions (**generate**, **repair**, **validate**, **grill**, **sketch**, **iterate**) are **Guidance actions** — pass the practice on the `guidance` argument (e.g. `guidance: [cdd_guidance.practices.stories.stories:Stories]`). They are not methods on `PracticeGuidance`.

Every scaffold pass ends with **validate** on the new or patched practice folder.

---
# Overview
## Favour defaults

- **`favour-defaults`** — `PracticeGuidance` already assembles **overview**, **guidance**, **shared rules**, **fidelities**, **templates** (active format), **examples**, and optional **`model/{format}/`** adapters from `{domain}/{domain}.md` and co-located files. **Do not override** `module_dir`. Put the `.py` module inside the practice folder (`practices/stories/stories.py` is the model). **Do not** re-implement `instructions`, `scoped_markdown`, or `render`. Use **`PracticeGuidance.render`**, and set the class attribute `format_adapters` when the practice owns its formats' parse and render adapters; otherwise render defers to the active fidelity’s Clean Engineering companion. The session a practice works in gives it its folder and the places each fidelity writes; `space/session/.context/module-context.md` describes the session's folder, its workpath, and each practice's folder in it. The Partition action (`cdd_guidance/actions/partition/partition.md`) indexes a source by the **Scaffold** subsection of the practice's current fidelity, so write one for every fidelity: it says what the index lists.

## Minimal Python module

- **`minimal-python-module`** — Domain `.py` is thin: `@agent_toolset`, `class Domain(PracticeGuidance):`, class docstring `"""# Instructions"""` (builder/agent entry — detailed prose lives in `{domain}.md`). Pass **`fidelity`** and **`format`** through `super().__init__(...)`, and set the optional class attributes **`default_workspace_folder`** and **`format_adapters`**, since every instance of the practice shares them. Take no `path` or `session`: the session that works on the practice gives it its folder, so a practice built with its own would write somewhere the session does not know. Write no instruction members and no `key` of your own — `PracticeGuidance` reads the instructions from `{domain}.md` and keys the practice by its folder name (`PracticeGuidance.key`). Add **`@agent_tool`** / **`@Hook`** members only when the practice owns tools; **`inject_rules`** must appear on `tools` if chat edits should load practice rules.

## Canonical practice markdown

- **`canonical-practice-markdown`** — All practice prose lives in **`{domain-slug}.md`** with **`## Overview`**, **`## Guidance`**, **`## Shared rules`**, and **`## Fidelities`** (per-fidelity `#### Guidance`, `#### Rules`, optional `default_format` / `stage` YAML). Criteria are named bullets under Overview or fidelity Rules. **No** `reference/` folder duplicating action kits. **No** copying kit action prose into the practice md.

## Compose other guidance in plain code

- **`compose-like-normal-code`** — To use another practice or toolset, construct it directly (`from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering`). **No** `ToolsetLoader` for in-repo types. Prefer **Guidance actions** with multiple `guidance` entries over duplicating generate/repair bodies on the practice class.

## Underscore folders and imports

- **`underscore-folder-imports`** — Practice folders use underscores (`practices/clean_engineering/`) matching the Python import path. Hyphens in folder names break imports — avoid them.

## Fidelity outputs

- **`outputs-relative-to-the-session`** — Declare each fidelity's `outputs` as paths relative to the session's folder, with no `root`. Put `markdown` and `drawio` under `.context/` and code straight in the folder, because the session decides where work lives and a declared root would send every session's artifacts to one place in the repository.

## A practice owns its formats

These four rules hold for every practice, so they are written once here and checked by two specs that run over every practice, not copied into each practice's document.

- **`every-declared-format-has-an-adapter`** — Every format a fidelity declares in its `outputs` has an adapter that reads it and writes it (`parse` and `render`), named in the practice's `format_adapters`, or in the Clean Engineering companion's when the practice has none of its own. `harness/guidance/format_adapter_spec.py` asks this of every fidelity and fails naming the format, because a declared format with no adapter offers a person a choice that answers nothing.
- **`format-returns-what-went-in`** — Name one worked example for each fidelity, as `example:` in the fidelity's YAML block: a file of the practice's folder, or a folder of code files. `cdd_guidance/practices/format_trip_spec.py` renders that example to each format the fidelity declares and back, and compares what came back with what went in (`harness/guidance/format_trip.py`); add the new fidelity's context to that spec. A format nobody has taken there and back is found broken by the first person who picks it.
- **`format-says-what-it-leaves-out`** — When a format holds less than the example, such as a drawing that holds no descriptions, say what it cannot hold and where that content is kept, as `leaves_out:` under the fidelity's YAML block, one sentence for each such format. The same spec fails a format that returns less and says nothing, because a person who picks a smaller format and renders it back loses content nobody told them about.
- **`render-keeps-every-line`** — A render written onto a file already there keeps every line the file holds. An adapter's `reshape` places what it can; the Render action keeps the rest in the file, set apart, and names it in its result as `migrate`; a render that would lose a line fails by name and leaves the file as it was. Never save a format by replacing the file, because the file may hold work the model never knew.

## A practice's graph reading

- **`join-nodes-by-identity`** — When the practice's graph reading (its *PracticeReading*) links two nodes, join them by what the node is: its file, its class, its language. Use the name only inside that, such as the `add` of `Cart` in `cart.py`, and never a shared name alone. A name alone linked a Python step to a TypeScript operation and `super().__init__` to every `__init__` in the project, so rules judged links that were never in the code.

## Practice folder layout

- **`domain-folder-layout`** — One folder per practice. The `.py` module lives **inside** that folder (e.g. `practices/agent_bdd/agent_bdd.py`, `builders/create_practice_guidance/_examples/car_chronicle/car_chronicle.py`). Same folder holds `{domain-slug}.md`, `_examples/examples.md`, optional `templates/` (artifact templates), optional `model/{format}/`, optional `scanners/`. Repair fixtures: `_examples/<descriptive-folder>/faultyAsset` and `repairedAsset`.

## Scaffold vs patch

- **`scaffold-vs-patch`** — Folder missing or empty → create full tree from **`builders/create_practice_guidance/templates/`**. Files already exist → add only missing pieces; **do not** overwrite good content or rebuild from scratch unless asked.

## Do not duplicate content

- **`do-not-duplicate-content`** — Do not re-create markdown the guidance layer already loads. Do not add parallel prose files for sections `PracticeGuidance` already resolves from `{domain}.md`. **Patch surgically** when fixing a practice.

## PracticeGuidance class module

- **`practice-guidance-class-module`** — `from harness.guidance.guidance import PracticeGuidance` and `from harness.agent_tools.agent_tools import agent_toolset`. Class docstring: `"""# Instructions"""`. **Subclass** `PracticeGuidance` (`class Domain(PracticeGuidance):`). The installer and the catalog find the practice through `@agent_toolset`, so it needs no other mark.

## Format templates vs scaffold templates

- **`format-vs-scaffold-templates`** — **`builders/create_practice_guidance/templates/`** = meta scaffolds for **building new practices** (Python + md + examples); loaded through this builder’s `templates` section, **no format filter**. **`templates/`** inside each practice = artifact templates for generate/satisfy (format-aware). **`model/{format}/`** = parse/render adapters, named by the practice's `format_adapters`.

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
