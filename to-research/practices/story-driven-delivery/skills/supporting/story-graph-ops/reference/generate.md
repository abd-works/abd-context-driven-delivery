# Generate — story-graph-ops

﻿---
name: story-graph-ops
catalog_garden_tier: foundational
catalogue_one_liner: >-
  Keep the story graph valid and consistent — so downstream tools always read trusted structure.
description: >-
  Create, read, update, and validate story-graph.json as the single source of truth for story structure. Use when editing the story graph or managing its lifecycle on disk.
context-perspective: stories
context-role: support
context-fidelity:
  - level: discovery
    mode: graph-ops
---

# story-graph-ops

## Agent obligations (do not skip)

This skill is **not** satisfied by "I read some other project's graph code and emitted JSON." That is a **supplement** at most—and **out of scope** for claiming this skill is done.

| Must | Detail |
| --- | --- |
| **Use this skill's tooling** | Run **`scripts/story_graph_cli.py`** and/or import from **`story_map`** with **`PYTHONPATH`** including **`…/story-graph-ops/scripts`** (path below). |
| **Finish with validation** | After creating or changing a graph file, run at least: **`story_graph_cli.py read --file <path>`** so a bad structure fails early. Prefer **`names`** or **`search`** when checking coverage. |
| **Declare completion** | Say what you ran (e.g. "validated with `read`")—not only "wrote JSON." |

**Anti-patterns (reject):**

- Hand-rolling JSON and stopping without **`read`** (or equivalent load via `story_map`).
- Using **another codebase's** loaders or domain classes as the *only* authority while ignoring this skill's CLI—those are not proof the serialized file is valid for **story-graph-ops** tooling.
- Skipping **`PYTHONPATH`** then claiming the skill was followed.

**When converting from Markdown, `.txt`, or chat:** build or edit JSON using **`story_map`** in Python **or** write JSON and pipe through **`write`**, then **`read`**—same validation rule.

## Skill root and PYTHONPATH

From the **agilebydesign-skills** repo, this skill's scripts live next to this file:

- **Skill directory:** `skills/story-graph-ops/`
- **Scripts:** `skills/story-graph-ops/scripts/`

```text
# Windows PowerShell example (adjust drive/path to your clone):
$env:PYTHONPATH = "C:\dev\agilebydesign-skills\skills\story-graph-ops\scripts"
cd C:\dev\agilebydesign-skills\skills\story-graph-ops
python scripts/story_graph_cli.py read --file C:\path\to\story-graph.json
```

Add **`…/common/scripts`** only if you import **`scanner_bases`** in the same process.

## Mandatory workflow (checklist)

Use this whenever **`story-graph.json`** (or any graph path) is created or meaningfully edited:

1. **Set `PYTHONPATH`** to include **`story-graph-ops/scripts`**.
2. **Produce JSON** via CLI `write`, or Python (`story_map`, etc.), or a careful hand-edit.
3. **Validate:** `python scripts/story_graph_cli.py read --file <path>` (must succeed).
4. **Optional checks:** `names`, `search`, `filter` as needed.
5. **Report** the validation command you ran.

## When to use this skill

Load **story-graph-ops** whenever work touches **`story-graph.json`** as an artifact:

| Operation | Examples |
| --- | --- |
| **Create** | New graph from scratch; minimal/empty scaffold; build structure from structured input; first save after shaping content. |
| **Read** | Inspect graph, dump JSON, list names, search substring. |
| **Update** | Add/rename/reorder nodes; fix acceptance criteria or scenarios; examples; associate test files, test classes or methods; merge branches of the tree; patch one story or one epic. |
| **Delete** | Remove a story, sub-epic, or epic subtree; strip AC; **replace entire graph** by writing new JSON (delete all prior content). |

Typical situations:

- Turning a story map in any form into **concrete graph JSON**—create/update nodes until the file matches intent.
- Output of ABD practice skills (e.g. abd-story-mapping) cleaned up in MD, txt, or other format and the graph must be updated: rename stories, fix AC, reorder nodes.
- **Mechanical passes**: list story names, subset by story name, dump JSON, write through.
- A filtered view: filter by node type, increments, etc.
- **Rules/scanners** on the graph: validators extend **`StoryScanner`** from **`story_scanner`** (on **`PYTHONPATH`** with **`story-graph-ops/scripts`**).

## Relationship to ABD practice skills

| Piece | Role |
| --- | --- |
| **ABD practice skills** | **Guidance and best practices** for abd.works work: how to frame problems, name and structure artifacts, use templates, run quality passes, and apply bundled rules or scanners. They answer *what good looks like* and *which conventions apply*—not the mechanical layer of reading or writing `story-graph.json` on disk. |
| **story-graph-ops** | **Lifecycle on disk**: create, read, update, and delete the **serialized graph** (`story-graph.json`, in whole or in part)—encoding, mutating, and tooling against the file. |

**Same complementary relationship** in every case: use **practice skills** for *how the work should read* and *which quality bars to hit*; use **story-graph-ops** to *create and edit the graph file* **and validate it with this skill's tools**. Whenever the deliverable includes **creating or changing** `story-graph.json`, load **story-graph-ops** and **complete the checklist above**.

## CLI

Implementation: **`scripts/story_graph_cli.py`**.

```text
python scripts/story_graph_cli.py read   --file <path/to/story-graph.json> [--pretty]
python scripts/story_graph_cli.py names  --file <path>
python scripts/story_graph_cli.py search --file <path> --substring <text>
python scripts/story_graph_cli.py filter --file <path> --stories "A","B" [--pretty]
python scripts/story_graph_cli.py sha    --file <path>
python scripts/story_graph_cli.py write  --file <out.json> [--input <in.json>|stdin]
                                          [--expect-sha <hex>] [--no-lock] [--force]
```

**Create / delete via CLI:** `write` accepts JSON on stdin or `--input`—you can emit a **full replacement** graph (effectively delete everything not in the new JSON) or a **filtered** subgraph. Finer-grained create/update/delete often uses **`story_map`** types in Python, then **`read`** to validate after saving.

---

## Reordering epics, sub-epics, or increments

> **Pattern: load JSON in Python, mutate, write back through the CLI.**
> The CLI has no native `reorder` subcommand — you produce modified JSON and commit it with `write`.

### Steps

1. Write a small Python script to a temp file that loads the graph, mutates the target array, and writes modified JSON to a second temp file.
2. Commit it through the CLI:
   ```
   python story_graph_cli.py write --file story-graph.json --input modified.json --no-lock
   ```
3. Validate:
   ```
   python story_graph_cli.py read --file story-graph.json
   ```

### Example — move an increment to a new position

```python
# reorder_increment.py
import json, sys

GRAPH = r"path/to/story-graph.json"
TARGET = "Roster and Desktop Interaction"   # increment name to move
NEW_INDEX = 1                               # 0-based: 1 = second position

with open(GRAPH, encoding="utf-8") as f:
    g = json.load(f)

incs = g["increments"]
idx = next((i for i, x in enumerate(incs) if x["name"] == TARGET), None)
if idx is None:
    sys.exit(f"ERROR: '{TARGET}' not found")

inc = incs.pop(idx)
incs.insert(NEW_INDEX, inc)
for i, x in enumerate(incs, 1):
    x["priority"] = i   # keep priority in sync with list position

OUT = r"path/to/modified.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(g, f, indent=2, ensure_ascii=False)
```

Then commit and validate:
```
python story_graph_cli.py write --file story-graph.json --input modified.json --no-lock
python story_graph_cli.py read  --file story-graph.json
```

The same pattern applies to reordering **epics**, **sub-epics**, or **stories** within their parent arrays — mutate the list, renumber any sequential fields, write, validate.

---

## Converting Markdown to story-graph.json

Three dedicated parser scripts convert skill-generated Markdown into graph JSON. **Always try the matching script first.** If the file does not match the expected format (the script exits with code 2), fall back to AI-assisted JSON construction; name the fallback script with a `_<variant>` suffix inserted just before the stem (e.g. `md_story_map_to_story_graph_custom.py`) so it can be reused.

### Naming convention for parser scripts

```
md_<artifact>_to_story_graph.py          -- canonical parser for one skill's output
md_<artifact>_to_story_graph_<variant>.py -- fallback or project-specific variant
```

| Script | Source skill | Converts |
| --- | --- | --- |
| `md_story_map_to_story_graph.py` | abd-story-mapping | `story-map.md` tree → epics, sub-epics, stories |
| `md_acceptance_criteria_to_story_graph.py` | abd-story-acceptance-criteria | `acceptance-criteria.md` → AC items on existing stories |
| `md_thin_slice_to_story_graph.py` | abd-thin-slicing | `thin-slicing.md` → increments array |

All three scripts exit with **code 2** when they cannot recognise the format — this is the signal to create a `_<variant>` script instead of hand-patching JSON.

---

### `md_story_map_to_story_graph.py` — story map

When a story map exists as a Markdown file in the `abd-story-mapping` tree format (epics, sub-epics, and stories with `(E)` / `(S)` markers), use this script rather than hand-building JSON.

**Format the parser expects:**

```text
(E) Epic Name
    (E) Sub-Epic Name
        (S) Actor --> Story Name
        opt (S) Actor --> Optional Story Name
    (S) Actor --> Story Directly Under Epic
```

- Indentation is **4 spaces per level**; depth determines parent.
- `(E)` lines become epics (depth 0) or sub-epics (any deeper depth).
- `(S)` lines become stories; the word before `-->` becomes `story_type`.
- `opt (S)` lines are treated identically to `(S)` lines.
- Any `## ` section header (consolidation notes, context gaps, etc.) ends parsing.

**Usage:**

```text
python scripts/md_story_map_to_story_graph.py <input-story-map.md> <output-story-graph.json>

# Validate immediately after:
python scripts/story_graph_cli.py read  --file <output-story-graph.json>
python scripts/story_graph_cli.py names --file <output-story-graph.json>
```

**After converting, always run `read` and `names`** — this confirms the JSON is well-formed and all stories parsed correctly before any downstream work.

---

### `md_acceptance_criteria_to_story_graph.py` — acceptance criteria

Merges acceptance criteria from an `acceptance-criteria.md` file into an **existing** `story-graph.json`. Matches by story name; injects numbered AC strings (preserving WHEN/THEN/AND/Evidence format) without disturbing scenarios or other fields.

**Prerequisite:** the graph must exist. Run `md_story_map_to_story_graph.py` first if starting from scratch.

**Format the parser expects** (generated by abd-story-acceptance-criteria):

```text
## Story: <story name>

**Story type:** <actor>

### Domain terms
- *Term* -- definition

### Acceptance criteria

1. **WHEN** the customer ...
   **THEN** the system ...
   **AND** each entry shows ...
   **Evidence:** source -- line N

2. **WHEN** ...
```

**Usage:**

```text
python scripts/md_acceptance_criteria_to_story_graph.py <input-ac.md> <story-graph.json>

# Validate after:
python scripts/story_graph_cli.py read  --file <story-graph.json>
```

**Exit codes:** `0` success · `1` missing file or unmatched stories · `2` unrecognised format (use a `_<variant>` script).

---

### `md_thin_slice_to_story_graph.py` — thin slicing / increments

Parses `thin-slicing.md` and **replaces** the `increments` array in the graph. Each `### Increment N: <name>` block becomes one increment with ordered story references. If the graph file does not exist, a minimal scaffold (empty `epics`) is created.

**Format the parser expects** (generated by abd-thin-slicing):

```text
### Increment 1: `Walk-in driver`

**Outcome:** ...

**Stories in this increment** *(order reflects flow):*

- *View Store Map*
- *View Store List*
```

**Usage:**

```text
python scripts/md_thin_slice_to_story_graph.py <input-thin-slicing.md> <story-graph.json>

# Validate after:
python scripts/story_graph_cli.py read --file <story-graph.json>
```

**Exit codes:** `0` success · `1` missing file · `2` unrecognised format (use a `_<variant>` script).

## Parallel runs and concurrent writes

`story-graph.json` is **shared mutable state** across the delivery flow — every stage mutates the same file. The planning skill allows **parallel runs** when outputs are independent (e.g. story definition for one slice while discovery continues for another). The policy and the mechanical safeguards are:

**Policy (planning-level):**

- **Do not edit the same slice in parallel.** Partition by slice / epic / story id up front, in the plan's run scope.
- When two runs must touch the same subtree, serialize them — run B waits for run A's **CHECKPOINT** to confirm before starting.
- The delivery lead's **Scope guard** at each exit gate flags when a team member added work outside the current run's scope.

**Mechanical safeguards (CLI-level):** `story_graph_cli.py write` enforces two independent checks so a race does not silently clobber another writer's edit.

1. **Advisory lock.** For the duration of a write, the CLI holds an exclusive lock file at `<path>.lock`. If another process holds a live lock, the write is refused with exit code **4**. Stale locks older than 5 minutes are cleaned up automatically. Bypass with `--no-lock` (not recommended) or `--force` (recovery only).

2. **Optimistic concurrency via `--expect-sha`.** Capture the file's content hash at read time and pass it back on write:

    ```bash
    SHA=$(python scripts/story_graph_cli.py sha --file story-graph.json)
    # … build your edit locally …
    python scripts/story_graph_cli.py write --file story-graph.json --expect-sha $SHA --input new.json
    ```

    If the file changed between the `sha` call and the `write` call, the write is refused with exit code **3** and an actionable message asking the caller to re-read, merge, and retry. This is the check that catches "Run A wrote between my read and my write" across processes or across sessions.

**Exit codes for `write`:** `0` success · `1` bad input / validation failure · `2` path resolution failure · `3` `--expect-sha` mismatch · `4` active lock held by another writer.

**Agent expectation:** every **`write`** during an active multi-run engagement uses both `--expect-sha` (captured from a prior `sha` or `read`) and the default advisory lock. `--force` is reserved for explicit recovery after a stale lock or an intentionally-clobbered edit, and should be logged as a correction entry (**`correct_output`** / corrections log).

## Relationship to other skills

| Piece | Role |
| --- | --- |
| **common** | Base rules bundler: **`run_scanners.py`**, violations, scan context. Prepends **`story-graph-ops/scripts`** then **`common/scripts`** on **`PYTHONPATH`** for scanners. |

Practice skills that ship graph-aware rules or scanners (importing **`story_map`** / **`StoryScanner`**): see **Relationship to ABD practice skills** above; **`common`** runs the scanner pipeline.

**Rules that need the graph:** declare `scanner:` in rule frontmatter; scanner modules use **`from story_map import …`**, **`from story_scanner import StoryScanner`**, plus **`scanner_bases`**. Shared graph code lives only in **story-graph-ops** — not under **`scanner_bases`**.

## Sources

- Python modules: **`scripts/story_map.py`**, **`scripts/story_scanner.py`**, **`scripts/graph_filters.py`**, **`scripts/story_graph_file.py`** (validated load/save for tools such as **drawio-story-sync**), …
- CLI: **`scripts/story_graph_cli.py`**
- Details: **`scripts/README.md`**
- **Parity with agile_bots `story_graph.nodes`**, mutation CLI, and test porting plan: **`MIGRATION_PARITY.md`** (the lightweight `story_map` types are not a full replacement for **`nodes.StoryMap`** until that migration is done).
