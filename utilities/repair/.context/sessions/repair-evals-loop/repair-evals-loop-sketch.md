---
fidelity: story_map + one-scenario-per-story
tool: repair
---

# Sketch — Close The Repair-To-Eval Loop

Grilled against `utilities/repair/repair.py`, `context_tools/base/base_context_tool.py`,
`utilities/sub_agent/sub_agent.py`, `utilities/handoff/handoff.py`, `utilities/partition/partition.py`,
`utilities/sketch/sketch.py`, `utilities/iterate/iterate.py`, `utilities/record_decisions/record_decisions.py`.
Grill answers: `grill-answers.md` (this session folder). One epic, four stories, no sub-epic layer
(story count sits inside 4-9 on its own). Actor is `Maintainer` throughout - same call as
`catalog/cdd-catalog-sketch.md`: internal dev-tool work, one persona, actor carries no real
branching weight here.

This closes the gap named in this session: log_fix/repair already work end to end (generate ->
validate -> log_fix -> repair root-cause -> capture faultyAsset/repairedAsset fixture), but
nothing tags *which* tool/fidelity produced an entry, nothing re-verifies the fixture history
automatically, nothing archives a closed to-fix.log, and — the sharpest complaint — nothing makes
the agent proactively reach for any of this without the user re-explaining it every session.

**Scenario-level depth added below** — one main-flow Given/When/Then per story (a second,
variation scenario on the archive story only, for the mixed-fidelity fallback rule). No
`{Type}ExampleFactory` exists yet for this internal tool code, so Given values reference the
model-sketch classes directly (`repair-model-sketch.md`: `ToFixEntry`, `ToFixLog`,
`RegressionExample`, `RegressionReport`) rather than factory-loaded fakes — the model sketch is
the closest thing to concrete objects this feature has before `generate` writes real code.

---

```
Close The Repair-To-Eval Loop
    Maintainer --> Tag To-Fix Entries With Tool And Fidelity
        every to-fix.log block records which context tool and fidelity produced it, with
        zero new argument for the calling agent - BaseContextTool.log_fix injects
        type(self).__name__ and self.fidelity into the call to self.repairer.log_fix
        tag is present with no extra argument from the agent
            given a Stories host with self.fidelity set to "story_map", and a mistake
                the maintainer has just pointed out in that host's last generated artifact
            when the agent calls log_fix with artifact/rule/wrong/original/improved only -
                no tool or fidelity argument supplied
            then the appended ToFixEntry block in to-fix.log reads tool: Stories and
                fidelity: story_map, sourced from type(self).__name__ and self.fidelity
                on the host - not from anything the agent passed

    Maintainer --> Orchestrate The Fix-To-Eval Loop Via One Action
        one action call replays the whole log -> confirm -> root-cause -> regress -> archive
        roadmap, so logging the *next* mistake in this same session calls the same action
        again and re-surfaces it automatically - no hook, no separate reminder mechanism.
        Repair.improve() (repair.py) carries the full playbook, same shape as
        Sketcher.sketch_session / Iterator.iterate_session / Partition.partition;
        BaseContextTool.improve() stays a thin forward (contexts/examples/templates,
        then self.repairer.improve(...)) - same shape as BaseContextTool.repair() today
        the roadmap resurfaces on its own for a second mistake, same session
            given the agent already called improve() once this session for an earlier
                mistake, and the returned instructions walked log -> confirm -> repair ->
                regress -> archive
            when the maintainer points out a second, unrelated mistake later in the same
                session and the agent calls improve() again
            then the second response carries that same full roadmap text from scratch -
                no separate reminder call, no hook, nothing lost to context length in between

    Maintainer --> Run Regression Across This Tool's Examples As A Background Sub-Agent
        after repair() captures a fresh faultyAsset/repairedAsset pair, a @sub_agent-marked
        run_regression tool launches non-blocking and re-checks every existing pair under
        this tool's own examples/*/ tree only - not repo-wide
        a fresh fixture does not shrink the safety net
            given RegressionReport.examples_root already containing three prior
                RegressionExample pairs, and repair() just wrote a fourth pair after
                today's fix
            when the maintainer accepts the offer and the agent calls
                run_regression(examples_root) as a non-blocking sub-agent
            then RegressionReport.run verifies all four RegressionExample pairs - every
                faultyAsset/faultyAssets file still violates scan, every
                repairedAsset/repairedAssets file still passes - and summary() names any
                pair that regressed

    Maintainer --> Archive The Closed To-Fix Log To The Repo Root
        once the maintainer is satisfied, archive_to_fix moves (not copies) the session's
        to-fix.log to .context/archive/repairs/{tool}-{fidelity}-{date}.log at the repo root -
        write-then-delete, so exactly one durable copy survives
        every entry agrees on tool and fidelity
            given a ToFixLog whose every ToFixEntry reads tool: Repair and
                fidelity: story_map
            when the maintainer calls archive_to_fix(repo_root)
            then ToFixLog.archive writes {repo_root}/.context/archive/repairs/
                repair-story_map-2026-08-03.log, and the session's to-fix.log no longer
                exists once that write returns
        entries disagree on fidelity                                    // variation
            given a ToFixLog whose ToFixEntry values mix fidelity: story_map and
                fidelity: model (the same repair-evals-loop session, deepened mid-sprint)
            when the maintainer calls archive_to_fix(repo_root)
            then ToFixLog.distinct_tags falls back to the session name, and the archive
                writes repair-repair_evals_loop-2026-08-03.log instead of guessing one
                fidelity over the other
~> Increment 1 (closes the proactivity complaint on its own): Tag To-Fix Entries With Tool
   And Fidelity, Orchestrate The Fix-To-Eval Loop Via One Action
~> Increment 2 (adds regression confidence + durability once increment 1 is in daily use):
   Run Regression Across This Tool's Examples As A Background Sub-Agent, Archive The Closed
   To-Fix Log To The Repo Root
```

---

## Notes on calls made here

- **Auto-inject, never a new required argument.** `write_to_fix` gains `tool`/`fidelity`
  params, but the calling agent never states them — `BaseContextTool.log_fix`/`.improve`
  already hold `type(self).__name__` and `self.fidelity` at the call site. Matches the
  existing rule that host `@tool`/`@action` wrappers are thin forwards, never a place the
  agent must repeat what the host already knows.
- **Orchestration lives in the kit, not the host — confirmed against every utility, not
  assumed from repair alone.** `Partition.partition`, `Sketcher.sketch_session`,
  `Iterator.iterate_session`, `RecordDecisions.record_decisions_session` all carry their
  entire numbered playbook as self-contained docstring prose + `self.<tool>()` calls in
  the same file. The host's matching action never repeats that logic — it loads the one
  thing a bare kit instance cannot know (this domain's `contexts`/`examples`/`templates`)
  and delegates the rest in a single line. `Repair.improve()` / `BaseContextTool.improve()`
  follow that same split, not a bespoke shape invented for this feature.
- **No hook.** A `beforeSubmitPrompt`-style hook that pattern-matches chat text
  ("to fix", "this is correct") was considered and explicitly rejected — the fix is a
  richer action, not a listener on the conversation.
- **Regression is scoped to one tool, not repo-wide.** Matches the user's own wording —
  "make sure that everything still works for the context tool in question" — and
  `repair.md` step 7's existing scope (`<domain>/examples/*/`).
- **Archive is a move, not a copy.** Exactly one durable copy of a closed to-fix.log
  should exist; write-then-delete order avoids data loss if the write path is wrong.
- **Naming (open):** working name for the new action is `improve` — matches the
  domain vocabulary used throughout this session, not yet explicitly confirmed by the
  user against alternatives (e.g. `close_the_loop`).
- **Scenario depth, one main-flow each, one variation.** Only the archive story gets a
  second scenario — the mixed-fidelity fallback is a real decided branch (see the
  archive-naming grill answer), not an invented edge case, so it earns a variation rather
  than staying an unstated assumption. The other three stories stay single-scenario at
  this depth; `no-shared-background-yet` applies (per `stories-sketch.md`'s exploration
  guidance) — every scenario spells out its own `given`, nothing factored out yet.

---

## Amendment — vocabulary renamed during implementation

Everything above uses the vocabulary this sketch was drafted with: `log_fix`,
`to-fix.log`, `ToFixEntry`/`ToFixLog`, `archive_to_fix`. A later implementation pass
found `log_fix` conflated two moments that actually happen at different times — the
mistake is known before the fix is — and split/renamed throughout:

- `log_fix` → `log_mistake` (call the instant a mistake is pointed out; returns
  `entry_id`) + `log_correction` (`entry_id`, `improved`, `status` — completes that
  same entry once the fix lands)
- `to-fix.log` → `mistakes.log`
- `ToFixEntry`/`ToFixLog` → `MistakeEntry`/`MistakeLog`
- `archive_to_fix` → `archive_mistakes`

The four stories and their scenarios still hold as written — read every `log_fix` as
`log_mistake` immediately followed by `log_correction`, and every `to-fix.log` /
`ToFixEntry` / `ToFixLog` / `archive_to_fix` as its renamed counterpart above. Full
rationale in `grill-answers.md`'s own "Amendment" note and `repair-model-sketch.md`'s
own "Amendment" section.

## Amendment — repair() also non-blocking; run_regression retired

The "Run Regression" story above named a separate `run_regression` tool as the
`@sub_agent`-marked launcher, called with `verify_regression` implied as the real
check underneath. A later pass applied that same non-blocking treatment to
`repair` and `archive_mistakes` too, directly — both are now `@sub_agent` in
their own right, same as `verify_regression` now is. Since `verify_regression`
itself became the sub-agent, the separate `run_regression` wrapper (whose only
job was dispatching it non-blocking) was retired — read every `run_regression`
above as `verify_regression`, launched the same non-blocking way. The "Repair
As Root Cause" story implicitly gained the same non-blocking option: `improve`'s
nested reference to `repair` now lists it as a deferred tool step (via a
`repair_tool` companion in `mode="tool"`) instead of inlining the whole loop,
so the maintainer's confirmed correction leads to an *offer* to launch `repair`
non-blocking, not an inline expansion of all seven of its steps. Full mechanism
in `repair-model-sketch.md`'s own matching "Amendment" section.
