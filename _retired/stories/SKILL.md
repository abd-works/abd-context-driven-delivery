---
name: stories
description: >-
  Turn a fuzzy product idea into named stories, concrete behavioral examples,
  and executable checks — at whatever depth the context supports. Use when
  decomposing features, writing behaviors, or generating acceptance tests.
catalog_garden_tier: practice
context-perspective: stories
---

# Stories Skill

## Purpose

The purpose of this skill is to look at the product through the lens of human and system interactions — the behaviours required to produce a solution — and map those interactions hierarchically at increasing levels of detail and granularity.

This includes:

- Naming the outcomes, activities, and stories that make up the product
- Working out the order in which the stories are delivered
- Describing the exact interactions and results each story represents
- Turning those interactions into automated checks that prove the product does what the stories say

## What this produces

This skill describes user and system interactions at increasing levels of granularity. Each stage deepens the same picture.

- **Shaping** — defining outcomes and activities as an *outline* story map with estimates and confirming stories
- **Discovery** — adding the stories under each activity to the *story map*, and setting the first-cut delivery order as a *thin slice*
- **Exploration** — defining a *scenario* that walks through each story's happy-path / main flow between the user and the system
- **Specification** — defining multiple *scenarios* that walk-through errors, boundaries, alternate flows, along with adding real *examples* using reference *domain* models where available
- **Engineering** — proving each walk-through against a running system with automated acceptance *story tests*

## Invocation

```
/stories [level] [format] [mode]

level:  shaping | discovery | exploration | specification | engineering | all
format: md | json | drawio | ts | tsx | java | python          (default: md)
mode:   consolidated | expanded | flat                         (default: inferred, see Step 2)
```

## How to run

**End-to-end chain (every invocation):**

```
chat / user request
  → this skill (SKILL.md)
  → assemble with fidelity + format + phase     # selects files; stdout = path list
  → read every assembled MD file in full        # NOT “read the manifest and stop”
  → follow generate-instructions/ + templates/ + rules/ from those reads
  → write deliverables
  → assemble --phase validate → read rules → run scanners
```

The assembler returns a **manifest** (JSON paths on stdout). The manifest is only a **reading list**. The skill work is reading those MD files and **doing what they say**.

### Step 1 — Determine format

The format of the output. Chosen by the user via `[format]` on the invocation, or inferred from what already exists on disk. Context read during the run can be in any format — only the output format matters here.

Formats include
- **documents** - `md`,`drawio`,`miro`
- **code** - `py`  , `tsx` , `java`
- **other** - `json`

### Step 2 — Determine layout (per format)

Story content sits on disk in one of three modes. Layout is chosen **per format** — a project can mix modes across formats (e.g. `drawio` map, `md` scenarios, `py` tests).

**The three modes:**

- **Consolidated** — multiple partial documents sliced by increment or epic.  Natural for `md`, `drawio`, `miro`. **Never used for tests** Details: `behavior/artifact-layouts-consolidated.md`
- **Expanded** — story map hierarchy expressed as folders and files. Natural for code. Details: `behavior/artifact-layouts-expanded.md`
- **Flat** — one file for everything. Only mode `json` supports; valid for tiny projects. Details: `behavior/artifact-layouts-flat.md`

For each format being written, resolve the mode:

1. Use `[mode]` from the invocation
2. Otherwise match what already exists on disk for that format
3. Otherwise infer from the format:
   - `json` → `flat`
   - `drawio` / `miro` → `consolidated`
   - code → `expanded` (create the folder hierarchy if none exists); tiny projects start `flat`
   - `md` → whatever is on disk; `consolidated` if starting fresh

Then read the matching per-mode behavior file for concrete locations, naming conventions, and workflow.

**Drift check.** When two representations of the same content coexist (e.g. a `drawio` map and an `md` scenarios file, or a doc and expanded code), check the other before modifying one and warn the user before proceeding. 

### Step 3 — Determine fidelity

Read whatever context exists: existing story content, workspace artifacts, conversation, domain material. Find the highest fidelity level already sufficiently covered using the criteria below. The **execution fidelity set** runs from the first uncovered level up to the level on the invocation.

**Shaping is covered when:**
- Story map is an **outline** — epics and sub-epics with confirming stories, not full decomposition
- Every epic and sub-epic has an **estimate** (`* approx N–M …`) for unmapped story count
- Scope is clear — what is and isn't in play
- Primary actors are named on confirming stories

**Discovery is covered when:**
- Story map has verb-noun stories under each activity with an actor assigned
- Thin slice ordering exists — which stories go first

**Exploration is covered when:**
- Each story has a happy-path scenario walk-through
- Walk-throughs use domain-grounded terms
- `Given`, `When`, `Then` are all stated

**Specification is covered when:**
- Each story's scenarios cover the important variations (errors, boundaries)
- Variations use real domain values, not invented placeholders
- Shared-structure variations are outline walk-throughs with example tables

**Engineering is covered when:**
- Every scenario walk-through has a story test
- Tests use the same words as the walk-through
- Tests mirror the story map hierarchy

> Example: `/stories specification md` + context shows a story list exists but no walk-throughs → execution fidelity set is `[exploration, specification]`. The AI runs instructions for both, with specification as the target and exploration filled in along the way.

### Step 4 — Assemble the right content

Run the assembler with the execution fidelity set, format, and phase. The phase determines which directories are in scope:

- `interview` — `concepts/`, `grill-me-questions/`
- `generate` — `concepts/`, `behavior/`, `generate-instructions/`, `templates/`, `rules/`, `examples/`
- `validate` — `rules/`

```bash
python stories/src/skill/assembly/assemble_components.py \
  --skill-root stories/ \
  --fidelity exploration,specification \
  --format md \
  --phase generate
```

**What assemble returns:** JSON on **stdout** — a manifest of **file paths** to read. It does not substitute for reading those files.

**What you must do next (hard gate):**

1. Parse the manifest paths.
2. **Read every listed file in full** — especially `generate-instructions/<fidelity>.md`, matching `templates/`, and `rules/`.
3. **Follow the instructions** in those files. The assembled MD *is* the skill guidance for this run; the manifest is only how you discover which files apply.

Do not treat the manifest JSON as the instructions. Do not generate until the reads in step 2 are complete.

Any file with unknown fidelity, invalid YAML, or missing front matter is soft-failed — dropped from the manifest and reported as an **anomaly** on **stderr**. Read the anomaly report and either fix the flagged file, waive it, or proceed knowingly. The CLI never aborts silently; if it cannot run at all, it emits a structured `error` payload on stderr instead.

### Step 5 — Generate

**Prerequisite:** Step 4 reads complete — you have read the assembled `generate-instructions/`, `templates/`, and `rules/` for this fidelity set.

Apply **`generate-instructions/<fidelity>.md`** for each fidelity in the execution set, **in fidelity order**. Those files tell you what to produce and how. Match **`templates/`** structure exactly; obey every **`rules/`** DO / DO NOT.

**Before generating into a code format, decide the producer.** There are two producers that can write into a stories tree, and they have opposite guarantees:

- The **code path** — invoked via `python stories/cli/main.py <command> ...` (see `stories/cli/README.md`) — is deterministic and owns full-tree renders, first spec-file renders, and first tier-file scaffolds. Use it for new formats or large new subtrees of an existing format.
- The **AI** owns everything else — filling scaffolded tier bodies with real assertions, small in-place edits (one scenario, one Examples row, an actor rename), and iterating on validation feedback. This is the majority of the work.

Never AI-generate a new spec file from scratch or hand-write tier scaffolding when the CLI can do it reproducibly; never re-run the CLI expecting to overwrite tier files that already have AI/human-authored bodies (they are write-once).

See `behavior/code-scaffolding-vs-ai-editing.md` for the full decision table, the CLI subcommands per situation, and the round-trip constraints on spec-file edits.

Three cross-cutting behaviors apply during generation:

- **Pick the producer** for each artifact — see `behavior/code-scaffolding-vs-ai-editing.md`
- **Record gaps inside the artifact** when source material is missing information — see `behavior/context-gaps.md`
- **Revise the story map** when deeper fidelity exposes a structural problem (a story that should split, a wrong boundary, a hidden capability): stop and recommend a revision — see `behavior/revising-story-map.md`

### Step 6 — Validate

1. Run `assemble --phase validate` to get the rule paths and **read every listed rule file in full**.
2. Run **all** applicable scanners against the generated workspace with the single command below — do not pick and choose:

```bash
python stories/src/skill/run_scanners.py \
  --workspace <path-to-workspace> \
  --rules-root stories/rules
```

`run_scanners.py` auto-detects which scanners apply to the workspace (based on which artifact kinds are present), runs every one of them, and emits one JSON violation line per failure plus a summary to stderr. Exit 0 = clean; exit 1 = violations found.

3. If violations are found: use `behavior/agentic-repair-loop.md` (background sub-agent, iterative fix loop). If the user has already fixed the problem manually: use `behavior/manual-repair-loop.md` (capture fail/pass fixtures).

---
