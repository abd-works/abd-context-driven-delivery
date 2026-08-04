---
fidelity: model
tool: clean_engineering
---

# Sketch — Repair-to-eval loop, model fidelity

Deepens `repair-evals-loop-sketch.md` (story_map) into classes. Precedent followed:
`utilities/partition/partition.py` — `Partition` stays a toolset; `PartitionIndex`,
`Segment`, `SegmentEntry` are the real domain classes it composes and calls. `Repair`
follows the same split — it stays a toolset (`log_fix`, `improve`, `archive_to_fix`,
`run_regression` as `@tool`/`@action`), and composes four new domain classes below.
Grilled: see `grill-answers.md` — "Model-fidelity class boundaries" for the four-vs-two-
vs-zero decision.

Interfaces (`I{Class}`) are not drawn yet — informal class names only, per this
tool's own sketch-notation rule (`I{Type}` names emerge when the formal `generate`
artifact is written, not before).

---

```
ToFixLog
  path
  entries
       ToFixEntry                          <-- owned value object (composition, 0..*)
         artifact
         rule
         wrong
         original
         improved
         status
         when
         tool
         fidelity
         render
           // wrong stays one line; multi-line detail lives in original/improved
  append entry
    -> entry.render
    // creates the file's header comment block on first write only; always
    // appends afterward - never overwrites a prior entry
  parse
    // reads every "--- … ---" block in the file back into ToFixEntry values -
    // the only way archive can know which tool(s)/fidelity(ies) are present
  distinct_tags
    -> self.parse
    // one (tool, fidelity) pair when every entry agrees; otherwise falls back
    // to the session name for archive-naming purposes
  archive repo_root
    -> self.parse
    -> self.distinct_tags
    // writes .context/archive/repairs/{tool}-{fidelity}-{date}.log under repo_root
    // deletes self.path only after that write succeeds - never delete-then-write
  // entries only grow across a session - append-only until archive() runs
  // exactly one durable copy of a closed log survives once archive() returns

  ----
 Scanner                                    <-- association; existing Scan kit (utilities/scanners/scan.py)

RegressionReport
  examples_root
  results
       RegressionExample                    <-- owned per run (composition, 0..*)
         folder
         faulty_paths
         repaired_paths
         verify
           -> Scanner.scan faulty_paths
           -> Scanner.scan repaired_paths
           // every faultyAsset/faultyAssets file must still violate scan
           // every repairedAsset/repairedAssets file must still be clean
     verify_examples                              <-- implemented as verify_examples, not run
       -> RegressionExample.verify
       // once per example folder directly under examples_root - never recurse
       // into the faultyAsset/repairedAsset payload folders themselves
       // renamed from "run" during implementation - use-domain-language scanner
       // flagged "run" as too generic for a public operation
  summary
    // pass/fail counts plus the name of every failing example folder
  // results reflect examples_root as of the last run() - call run() again
  // after a fresh fixture pair lands before trusting the summary
```

---

## Toolset call sites (existing `@tool`/`@action` shape on `Repair` — not modeled classes)

```
Repair.log_fix(artifact, rule, wrong, original, improved, status, tool, fidelity)
  -> ToFixEntry construction
  -> ToFixLog(self.workspace.folder).append

Repair.archive_to_fix(repo_root)
  -> ToFixLog(self.workspace.folder).archive repo_root

Repair.run_regression(examples_root)          // @sub_agent - non-blocking
  -> RegressionReport(examples_root).run
  -> RegressionReport.summary

Repair.improve(artifact, rule, wrong, original, improved, status)   // new orchestrating @action
  -> self.log_fix                              // writes the ToFixEntry immediately
  -> self.repair asset violation                // on confirmation - existing root-cause loop
  -> self.run_regression examples_root           // offered, non-blocking
  -> self.archive_to_fix repo_root               // offered, once satisfied
```

---

## Notes

- **`tool`/`fidelity` on `ToFixEntry` are auto-injected**, never supplied by the calling
  agent — `BaseContextTool.log_fix`/`.improve` hold `type(self).__name__` and
  `self.fidelity` at the call site (per the story-map sketch's first decision).
- **`ToFixLog.parse` is new behavior**, not present in `repair.py` today — it exists
  solely so `archive` can name the destination file correctly. Without it, `archive`
  would have to guess the tag from the session name alone, defeating the point of
  tagging entries individually.
- **`RegressionExample`/`RegressionReport` scope to one `examples_root`** — a single
  tool's `examples/` tree, per the story-map sketch's regression-scope decision. Never
  repo-wide.
- **No relationship drawn between `RegressionReport` and `ToFixLog`.** They are used
  from the same `improve()` call sequence but do not hold references to each other —
  `run_regression` takes a plain `examples_root` string, not a `ToFixLog`.

---

## Amendment — two-phase logging, renamed during a later implementation pass

The single `log_fix(artifact, rule, wrong, original, improved, status)` call above
assumed the mistake and its fix are always known at the same moment. In practice the
mistake is spotted first and the fix lands later, sometimes with several mistakes open
at once — so the log and the class it renders were split and renamed:

- `ToFixEntry` → **`MistakeEntry`**, gains `entry_id` (assigned by `log_mistake`,
  never supplied by the agent) so a later `log_correction` call can complete the
  exact same entry instead of opening a new one.
- `ToFixLog` → **`MistakeLog`**; the file itself is now `mistakes.log`, not
  `to-fix.log`. `append` still only ever adds a new (open) entry; a new `complete`
  op rewrites the log in place to fill in `improved`/`status` on the entry matching
  `entry_id` — the one exception to "append-only until archive," and still never a
  second entry for the same mistake.
- `Repair.log_fix` → **`Repair.log_mistake(artifact, rule, wrong, original, tool,
  fidelity)`** (returns `entry_id`) plus **`Repair.log_correction(entry_id,
  improved, status)`**.
- `Repair.archive_to_fix` → **`Repair.archive_mistakes`**.
- `Repair.improve` also picked up a nested `self.repair(asset="", violation="")`
  reference so the full root-cause loop inlines into `improve`'s own response —
  the earlier sketch's call-site list above named `repair` as a step but the
  implemented body had not actually referenced it as a tool/action call, so it
  never surfaced.

## Amendment — repair deferred via mode="tool"; run_regression folded into verify_regression

The nested `self.repair(asset="", violation="")` call above still inlined the
*entire* `repair.md` loop into every `improve` response — too heavy for a
roadmap meant to resurface on every logged mistake. `Repair` gained a
`repair_tool` property (a fresh `Repair` companion with `mode = "tool"`,
the same `AgenticToolset` mechanism `Stories.ce()` already used); `improve`
now calls `self.repair_tool.repair(...)`, which lists `repair` as a deferred
tool step instead of expanding it. `repair`, `verify_regression`, and
`archive_mistakes` also picked up `@sub_agent` directly, so all three launch
as non-blocking background tasks — the same non-blocking treatment
`run_regression` had, now applied uniformly instead of to regression alone.
`run_regression` itself (an empty-bodied wrapper whose only job was
dispatching `verify_regression` non-blocking) became redundant and was
removed; `verify_regression` is now the sub-agent directly, still callable
as plain Python for tests since `@sub_agent` changes discovery, not the
underlying method. A direct top-level `repair()` call (e.g. via
`BaseContextTool.repair()` → `self.repairer.repair(...)`, a normal-mode
instance) is unaffected and still inlines the full loop.
