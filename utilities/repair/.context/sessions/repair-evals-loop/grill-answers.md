# Grill Answers

### Tool/fidelity tag source on to-fix entries

tool and fidelity are auto-injected by BaseContextTool.log_fix (and .repair) at
the forwarding call site - type(self).__name__ for tool, getattr(self, 'fidelity', None)
for fidelity - never a new argument the calling agent must supply. log_fix
gains tool/fidelity params with empty-string defaults so direct Repair(...) callers
(outside a BaseContextTool host) still work without them.

### Non-blocking regression - home and scope

Lives inside repair() itself, at step 7, right after the pass fixture (step 6)
is captured - not a new standalone lifecycle action, not automatic. repair.md
step 7 prose gains: ask the user whether to re-run regression across this tool's
examples/*/ pairs; on yes, call a new @sub_agent @tool run_regression(examples_root)
on Repair, non-blocking. Scope is this tool only - examples_root = str(self.module_dir
/ 'examples') on the BaseContextTool host calling repair(), mirroring the existing
self.sketcher = Sketcher(agent_dir=str(self.module_dir)) pattern. Not repo-wide.

### Archive trigger and naming

New explicit tool archive_to_fix(repo_root) on Repair, called on demand (not tied
to close_session) - same explicit-call shape as Handoff.write_handoff. Archive path
is flat: {repo_root}/.context/archive/repairs/{tool}-{fidelity}-{date}.log (falls
back to session name in place of fidelity when a session's entries mix fidelities).

### Archive is a move, not a copy

archive_to_fix deletes the session's to-fix.log after the repo-root archive write
succeeds (write-then-delete, never delete-then-write). Exactly one durable copy
survives at .context/archive/repairs/{tool}-{fidelity}-{date}.log; no stale
duplicate left at {session}/to-fix.log to be mistaken for current.

### Orchestrator action - thin host, fat kit (confirmed against every utility)

Checked partition.py, sketch.py, iterate.py, scan.py, record_decisions.py against
repair.py/base_context_tool.py - all follow one template with no exception:
the KIT's own @action (Partition.partition, Sketcher.sketch_session,
Iterator.iterate_session, RecordDecisions.record_decisions_session) carries ALL
the orchestration as numbered docstring prose plus self.<tool>() calls in the same
file - fully self-contained, no host state needed. The HOST's matching @action on
BaseContextTool stays minimal: load THIS domain's self.contexts/self.examples/
self.templates (the only thing a bare kit instance cannot know), then delegate
everything else to the kit's action in one line - exactly what BaseContextTool.repair()
already does (self.scan(); self.contexts; self.examples; self.templates;
self.repairer.repair(asset, violation)).

Decision: new action follows the identical split. Repair.improve(artifact, rule,
wrong, original, improved, status) is a new @action in repair.py carrying the full
playbook (log via self.log_fix -> on confirmation call self.repair(asset, violation)
for root cause+fixture capture -> offer self.run_regression(examples_root) non-blocking
-> offer self.archive_to_fix(repo_root)) exactly like repair.md today, just one level
up. BaseContextTool.improve() is a thin forward: self.contexts; self.examples;
self.templates; self.repairer.improve(...). No new logic on the host beyond what
repair()/log_fix() already do there.

Working name: improve (matches domain vocabulary used throughout this session).

### Model-fidelity class boundaries (CleanEngineering)

Four new domain classes, following the exact precedent set by partition.py
(Partition stays a toolset; PartitionIndex/Segment/SegmentEntry are the real
domain classes it composes): ToFixEntry (value object - artifact/rule/wrong/
original/improved/status/when/tool/fidelity + render), ToFixLog (owns entries;
append; parse existing file back into ToFixEntry values - required because
archive() must know which tool(s)/fidelity(ies) are actually present to name
the archive file; archive(repo_root) write-then-delete), RegressionExample
(one faultyAsset/repairedAsset pair; verify() calls Scanner on each side),
RegressionReport (owns RegressionExample per run; discovers examples_root/*/;
aggregates verify() results; summary()). Repair (the toolset) composes and
calls all four from log_fix/archive_to_fix/run_regression - it does not
become a modeled domain class itself, same as Partition never does.

### Scenario-level depth added to the story-map sketch

Deepened repair-evals-loop-sketch.md from story_map to story_map + one-scenario-per-story
(frontmatter updated). One main-flow Given/When/Then per story, Given values drawn from
repair-model-sketch.md's classes (ToFixEntry, ToFixLog, RegressionExample, RegressionReport)
since no {Type}ExampleFactory exists yet for this internal code. Archive story gets a second,
variation scenario for the mixed-fidelity fallback (falls back to session name) since that is
a real decided branch from an earlier grill tick, not an invented edge case - the other three
stories stay single-scenario. No shared background factored out yet at this depth.

### Amendment — log_fix split into log_mistake/log_correction (post-implementation)

A later pass found the single `log_fix(..., improved, ...)` call assumed the fix is
already known when the mistake is logged — wrong: the mistake must be logged the
moment it is *pointed out*, before any fix exists, then completed once the fix
lands. Split into `log_mistake` (returns `entry_id`) and `log_correction(entry_id,
improved, status)`, correlated by `entry_id` rather than a single "current mistake"
resource so several mistakes can stay open at once — the agent tracks each id
itself. `to-fix.log` renamed `mistakes.log`; `ToFixEntry`/`ToFixLog` renamed
`MistakeEntry`/`MistakeLog`; `archive_to_fix` renamed `archive_mistakes`. Full
before/after in `repair-model-sketch.md`'s own "Amendment" section.

Same pass added a real `self.repair(asset="", violation="")` reference inside
`Repair.improve`'s body — the original design always intended the root-cause loop
to be part of `improve`, but the implemented body never actually called it, so it
never inlined into `improve`'s response. `repair.md` Step 4 also gained an explicit
approval gate: draft the fix wherever root cause actually lives — the context
tool itself, or occasionally a shared utility/primitive underneath it — present
it to the user, and wait for approval before applying. Also dropped "generator"
as the word for that root-cause location: this framework has no generic code
generator, only context tools (and the utilities/primitives they depend on), so
the prose now names those directly instead of the borrowed term.

### Amendment — repair goes non-blocking too; run_regression folded in (post-implementation)

The plain `self.repair(asset="", violation="")` reference above turned out wrong
in a different way: an @action reference inside another @action's body inlines
the *entire* nested loop by default — every `improve` call would have re-inlined
all seven steps of `repair.md`, defeating its purpose as a lightweight roadmap
that resurfaces cheaply. Fixed with `AgenticToolset`'s existing `mode` resource
(the same mechanism `Stories.ce()` already used): added a `repair_tool` property
that returns a fresh `Repair` companion with `mode = "tool"`, and `improve` now
calls `self.repair_tool.repair(...)` — mode="tool" makes a nested action call
list itself as a deferred tool step instead of expanding inline. A direct
top-level `repair()` call (still the normal-mode instance) is unaffected and
keeps inlining the full loop.

Separately, `repair`, `verify_regression`, and `archive_mistakes` all picked up
`@sub_agent` directly, so the agent launches each as a non-blocking background
task rather than running it inline — same non-blocking intent `run_regression`
already existed for, just applied uniformly instead of to regression alone.
That made the old `run_regression` wrapper (an empty-bodied `@sub_agent @tool`
whose only job was dispatching `verify_regression` non-blocking) fully redundant,
so it was removed; `verify_regression` is now the sub-agent entry directly, and
still plain-Python-callable for tests/scripts since `@sub_agent` only changes
agent-facing discovery, not the underlying method.

