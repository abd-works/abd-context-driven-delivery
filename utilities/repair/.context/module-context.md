# Repair

**Purpose:** Record a mistake the moment it's spotted (`log_mistake`) and complete
it once fixed (`log_correction`); when repairing, fix root cause (`repair`);
orchestrate the whole mistake-to-eval loop from one action (`improve`); check
regression across a tool's own examples (`verify_regression`);
archive a closed mistakes.log (`archive_mistakes`). `repair`, `verify_regression`,
and `archive_mistakes` are all `@sub_agent` — the calling agent launches each as
a non-blocking background task rather than running it inline; they stay directly
callable in plain Python (tests, scripts) since `@sub_agent` only changes
agent-facing discovery, not the underlying method.

**Seam:** `Repair`, `MistakeEntry`, `MistakeLog`, `RegressionExample`, `RegressionReport`

## Public API

- `Repair` — `log_mistake`, `log_correction`, `repair` (`@sub_agent @action`),
  `improve`, `verify_regression` (`@sub_agent @tool`), `archive_mistakes`
  (`@sub_agent @tool`). Inside `improve()`, `self.mode = "tool"` then
  `self.repair(...)` lists `repair` as a deferred tool step instead of
  eagerly inlining the whole root-cause loop. A direct top-level `repair()`
  call (e.g. via `BaseContextTool.repair()` -> `self.repairer.repair(...)`)
  keeps the default `mode="action"` and still inlines the full loop.
- `MistakeEntry` — props: `entry_id`, `artifact`, `rule`, `wrong`, `original`,
  `improved`, `status`, `when`, `tool`, `fidelity` (`entry_id` correlates a
  `log_mistake` call to its later `log_correction` — several can stay open at
  once; `tool`/`fidelity` name whichever context tool/fidelity produced the
  entry; auto-injected by the calling host, never supplied by the agent);
  ops: `render`
- `MistakeLog` — props: `path`; ops: `append`, `complete` (rewrites the log in
  place to fill in `improved`/`status` on the entry matching `entry_id` — never
  appends a second entry for the same mistake), `parse`, `distinct_tags`, `archive`
  (moves — never copies — to `.context/archive/repairs/{tool}-{fidelity}-{date}.log`
  under a `repo_root`; falls back to the session name, independently per
  tool/fidelity, when entries disagree)
- `RegressionExample` — props: `folder`, `faulty_paths`, `repaired_paths`, `rule`
  (the rule slug this example exercises — the folder name by default, or a
  `rule.txt` sidecar when two folders deliberately share one scanner); ops:
  `verify` (faulty paths must still violate that one rule; repaired paths must
  still be clean of it — unrelated rules firing on an intentionally-narrow
  fixture snippet do not fail the check). Only exists for **mechanical**
  rules — a judgment-call rule closes on a prose-only fix with no scanner, no
  fixture pair, and nothing here to regress (see `repair.md` § "Not every
  rule is a scanner rule").
- `RegressionReport` — props: `examples_root`, `results`; ops: `verify_examples`,
  `summary` (scoped to one tool's own `examples_root` — never repo-wide)

**Dependencies:** `scanners.Scan` (regression re-scans faultyAsset/repairedAsset
pairs); `sub_agent.sub_agent` (marks `repair`, `verify_regression`, and
`archive_mistakes` as non-blocking launches); `primitives.actions.action`'s
`mode` resource (`self.mode = "tool"` inside `improve` defers the nested
`repair` call)

**Mechanism:** Concrete mergeable class (one test tier — no separate interface)
composing four domain classes, same split as `PartitionPipeline`. `log_mistake`
and `log_correction` are two calls, not one, so the mistake is durably recorded
the instant it's pointed out — never deferred until a fix exists. Approval
asks from `repair` / `improve` (see `repair.md` § Approval ask, `improve.md`
§ 3) must state what went wrong, why, what will change, and the user's
decision — never slug-only boards; the parent resumes the repair sub-agent
to apply after approval.
