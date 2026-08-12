# Handoff — Scaffold migration steps 2–3

## Next session focus

Add `@instruction def scaffold(self): ...` to each tool class, update `partition_guidance()` in `partition_pipeline.py` to use `self.scaffold` instead of looking for `partition.md`, then delete all five `partition.md` files.

## Resume in three lines

- Stage: **partition pipeline cleanup** · no active generator session · scope is `utilities/partition_pipeline` + all five `context_tools/{tool}/`
- Last accepted: Step 1 complete — `## scaffold` fidelity section added to all five tool `.md` files (bdd, ddd, stories, ux, clean_engineering); `partition_guidance.md` cleaned of redundancy; domain `partition.md` files stripped to near-empty stubs
- Next action: add `@instruction def scaffold(self): ...` to each `.py` tool class → update `partition_guidance()` → delete `partition.md` files

## Generator state

- No active toolset session
- Context index: `stories = ./tests/*` (see `context_index_path` below)
- Working folder: `utilities/partition_pipeline/.context`

## Architecture decisions made this session

**scaffold ≠ partition:**
- `scaffold` = a **fidelity level** — the thin top-level artifact index (bounded contexts / epics / screens / subjects / modules)
- `partition` = an **action** that reads a corpus and produces scaffold output, guided by `partition_guidance.md`
- These are NOT aliases; `partition` uses `scaffold` as its target fidelity

**Why `@instruction def scaffold()` works without a new file:**
The instruction system's `_path_for_name()` (in `primitives/instructions/instructions.py` line ~30–47) searches all `.md` files in the module directory for a heading matching the method name. `scaffold` → heading `Scaffold` → finds `## scaffold` in `{tool}.md` → resolves to `{tool}.md § Scaffold`. No new file needed.

## What was changed this session

### `utilities/partition_pipeline/partition_guidance.md`
- Now a `{{param}}`-substituted template (domain-slug, primary_artifact, secondary_artifact, artifact_naming_rule, skim_focus, index_columns, lens_name, partition_done_checks)
- Must follow section rewritten to explain WHY each item is read and what you do with it
- Hard fail removed (was duplicated from here into partition_pipeline.md — kept here, removed from base)
- Cross-references fixed: "base partition.md" → `partition_pipeline.md`

### `utilities/partition_pipeline/partition_pipeline.py`
- `_partition_params()` method added (base returns `{}`)
- `partition_guidance()` substitutes all `{{key}}` from `{"domain_slug": ..., "partition_done_checks": "", **self._partition_params()}`
- Still reads `partition.md` for domain content — **this is step 2 to change**

### `context_tools/{tool}/{tool}.py` (all five)
- `_partition_params()` override added with: `lens_name`, `index_columns`, `primary_artifact`, `secondary_artifact`, `artifact_naming_rule`, `skim_focus`, `partition_done_checks`
- No class attributes added — method override only

### `context_tools/{tool}/{tool}.md` (all five)
- `## scaffold` section added before first fidelity section
- Fidelity tables updated to include scaffold row (stories, ux, clean_engineering, ddd)
- CE progression line updated: `partition (action) → scaffold → modules → model → code`

### `context_tools/{tool}/partition.md` (all five — **to be deleted in step 2**)
- Stripped to near-empty stubs (Top-level artifacts heading was the only remaining content, now moved to scaffold section in tool .md)
- BDD: 6 lines — just the artifact definition + key rules
- DDD, Stories, UX: ~7 lines each — same
- CE: still has Index (First pass CE additions) + Anti-patterns + Segment — these also belong in scaffold section of clean_engineering.md but weren't fully migrated

**CE note:** The CE `partition.md` still has Index § First pass additions, Anti-patterns table, and Segment (domain) section. These were moved into `clean_engineering.md § scaffold` in step 1. Verify the CE scaffold section in `clean_engineering.md` has all of this before deleting `clean_engineering/partition.md`.

## Steps 2–3 in detail

### Step 2a — Add `@instruction def scaffold(self): ...` to each tool class

In each of `bdd/bdd.py`, `ddd/ddd.py`, `stories/stories.py`, `ux/ux.py`, `clean_engineering/clean_engineering.py`:

```python
@instruction
def scaffold(self) -> Instruction: ...
```

Place it alongside `contexts()`. The instruction system resolves this to `{tool}.md § Scaffold` automatically — no file needed.

### Step 2b — Update `partition_guidance()` in `partition_pipeline.py`

Change the domain content block from file-check to instruction:

```python
# BEFORE
if (self.module_dir / "partition.md").is_file():
    domain = Instruction.ref(self, "partition").expand()
    ...

# AFTER
from primitives.instructions.instructions import _instruction_ref_resolves
if _instruction_ref_resolves(self, "scaffold"):
    domain = Instruction.ref(self, "scaffold").expand()
    for k, v in params.items():
        domain = domain.replace("{{" + k + "}}", v)
    return f"{base}\n\n{domain}"
```

Or simpler — just call `self.scaffold` and handle None:
```python
try:
    domain = Instruction.ref(self, "scaffold").expand()
    if domain.strip():
        for k, v in params.items():
            domain = domain.replace("{{" + k + "}}", v)
        return f"{base}\n\n{domain}"
except Exception:
    pass
```

### Step 3 — Delete `partition.md` files

After verifying `partition_guidance()` picks up scaffold content correctly:
```
Remove-Item context_tools/bdd/partition.md
Remove-Item context_tools/ddd/partition.md
Remove-Item context_tools/stories/partition.md
Remove-Item context_tools/ux/partition.md
Remove-Item context_tools/clean_engineering/partition.md
```

## Artifacts to read

- `utilities/partition_pipeline/partition_pipeline.py` — current `partition_guidance()` method
- `utilities/partition_pipeline/partition_guidance.md` — current template
- `primitives/instructions/instructions.py` lines 30–47 — `_path_for_name()` section resolution
- `context_tools/clean_engineering/clean_engineering.md § scaffold` — verify CE scaffold has all CE-specific content before deleting partition.md
- `context_tools/clean_engineering/partition.md` — compare against CE scaffold section
- `C:\Users\thoma\OneDrive - Agile by Design\Shared Documents\Assets\abd-works-repo\abd-context-driven-delivery\.context\context-index.md`

## Open questions / risks

- **CE partition.md** — has more content (Index/First pass additions, Segment nesting rules) than other files. Verify it all landed in `clean_engineering.md § scaffold` before deleting. The Segment nesting rules (flat/nested/parent-base path conventions) are CE-specific and must survive.
- **`{{index_columns}}` in CE partition.md** — CE's First pass "Step 4 (extended)" uses `{{index_columns}}` which is a `_partition_params()` param. This substitution happens in `partition_guidance()`. Ensure it also applies when the content comes from `self.scaffold` (not just from `partition.md`).
- **BDD fidelity table** — BDD's `bdd.md` may not have a top-level fidelity table (not seen in first 40 lines). Scaffold row may not have been added. Check `bdd.md` for a fidelity table and add scaffold row if missing.
