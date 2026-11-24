# Clean Engineering review: index

Every round of the Clean Engineering review of this repository's code, in date order: what each round found, what was fixed, and what is still open. It covers two pieces of work. The first is the refactor on the branch `ensure-domain-orientation-refactor` (rounds 1 to 9, 2026-11-01 to 2026-11-09), whose files moved here from `.context/model/repo-review/` because they are session work, not durable context. The second is this release's review (2026-11-18 to 2026-11-24): the Validate action's runs, seven judges, the design proposals and the refactor built from them.

**Current state:** the latest Validate run over the whole production code is [clean-engineering-code-20261124T010849.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261124T010849.md) (2026-11-24 01:08 UTC, commit `94b59f9`). A scoped run of the review pass that followed it is [clean-engineering-code-20261124T013014.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261124T013014.md). Every finding's history (found, fixed, judged) is in [violation-history.jsonl](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\violation-history.jsonl), and the release's account of the review, with the errors the refactor introduced and the measures before and after, is sections 2 (wave 6), 5 and 6 of [release-1-2-fixes-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\release-1-2-fixes-report.md).

## Where the files are

| Folder | What it holds |
|---|---|
| [refactor-rounds-1-9](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\README.md) | The earlier refactor: the first rule-based relationship list (`repo-model-disconnected.md`), the round-4 relationship review (its `README.md` and the five area files `harness-core.md`, `harness-upper.md`, `space-tools.md`, `actions-patterns.md`, `practices.md`), the per-area files and reports of rounds 5 to 9, the AI findings trend (`trend-rounds-1-9.md`), the code measures trend (`code-metrics-trend.md`), the plan left at the end (`remaining-work-plan.md`), and `concern_counts.py`, which counts a round's findings from those files. |
| [judge-round](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round) | This release's review: the seven judges' reports (`judgment-*.md`), the merged [design-proposals.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round\design-proposals.md), and [code-measures-before-and-after-judge-fixes.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round\code-measures-before-and-after-judge-fixes.md). |
| [scripts](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\scripts) | `measure_revision.py` and `metrics_gate.py` (the earlier refactor's measures and the gate every change had to pass from round 9; run with a metrics venv, the gate imports the measures from beside it), `measure_checkout.py` (the reshape's lizard measures), `invokes_dump.py` and `graph_json_dump.py` (dump a checkout's invokes edges or whole saved graph to compare before and after a change). |
| [validation-reports](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\README.md) | The Validate action's own reports, left where the action writes them. |
| [exploratory-testing/analysis/code-metrics.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\exploratory-testing\analysis\code-metrics.md) | 2026-11-22: which measures would have flagged the release's 146 defects; it reads the review's measures but belongs to the exploratory testing analysis. |

The durable model of the code is one class model per module, `{module}/.context/{module}-model.md` and `.drawio` (such as [graph-model.md](C:\devbd-cdd-release-1-2-fixes\harness\graph\.context\graph-model.md); `space/work_state` is in `space/.context/space-model.md`, and the board keeps `space/kanban/.context/kanban-model.md`), split unchanged from the whole-repository `repo-model.md` and `.drawio`, which are gone with `repo-model.whiteboard`. The runtime relationships between the modules' classes stay in `.context/model/repo-runtime.md`.

## The rounds, in date order

### Rounds 1 to 3: AI judges on every rule (early November, `d6c41b23` to `42ab935c`)

- **Found:** round 1, 64–114 findings (21–41 high) over the modules, model and code fidelities; round 2, 23–44 over the six practice folders and module cards; round 3, 38–48 over the whole repository. The bugs were the server crashing and piling up, data erased, hooks logging into the wrong session, format round trips losing data, and paths resolved against the server's folder.
- **Fixed:** round 3 confirmed 10 round-1 bugs and about 14 structural fixes; four earlier mistakes had come back in code no spec covered.
- **Where:** counts in [trend-rounds-1-9.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\trend-rounds-1-9.md). The round reports themselves lived in `.sessions/ensure-domain-orientation-refactor/`, which is no longer in this checkout; they are in git history.

### Round 4: relationship review (2026-11-07, `d589b161`)

- **Found:** five agents read the code behind all 921 runtime relationships and 832 classes, against the first rule-based list in [repo-model-disconnected.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\repo-model-disconnected.md): 363 relationships with the wrong shape, 19 classes with no use, 84 earlier verdicts overturned, and three defects. Summary and themes: [refactor-rounds-1-9/README.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\README.md).
- **Fixed (by 2026-11-07, `4c6ebb8d`):** the 19 unused classes deleted or kept with the use the review missed; option A, one graph and one practice object per session (`GraphPractice`, `GraphPractices`, `PracticeGraph` deleted); the package moves (diagnostics, installation, annotations, `tools`, `space/session`'s file manager); every harness, space, tools, actions and patterns area; both rounds of practice fixes; DDD's draw.io on Clean Engineering's diagram classes.
- **Left open then:** space/kanban and the follow-up fixes were still running; the old `_skip_inactive_fidelity` and `_activate(stage=...)` hooks; the format as a `Format` object; one Clean Engineering companion per session.

### Round 5: cross-file validation (2026-11-08, `d71e0b20`)

- **Found:** 170 findings, 21 high, over twelve concerns that span files ([round5-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\round5-report.md)). Actions sent prompts with text missing, one graph validate stalled the whole server (B10), the graph went empty after a ticket switch, and second object models and hidden import cycles remained. 150 findings fell in the loop's three goal classes: bad resource orientation, shadow models, duplicated functions.
- **Fixed:** about 120 of them by round 6.

### Round 6 (2026-11-08, `b91a73eb`)

- **Found:** 133 findings, 12 high, goal classes 110 ([round6-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\round6-report.md)); two regressions from the round-5 fixes, B10 still stalling the server, a stale hook daemon, session tools losing the calling chat.
- **Fixed:** goal classes fell to 39 by round 7.

### Round 7 (2026-11-08, `c8921451`)

- **Found:** 54 findings, 4 high, goal classes 39 ([round7-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\round7-report.md)): a DDD crash in the graph worker, 12 rules that never ran on the live graph, a validate reporting clean code wrongly.
- **Fixed:** the DDD crash; rule examples go through the schema.

### Round 8 (2026-11-08, `4359b907`)

- **Found:** 43 findings, 4 high, goal classes 31, 21 in the scope round 7 checked ([round8-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\round8-report.md)): the same crash in the Stories reader, Grill handing the agent the wrong fidelity, the board's TypeScript packages importing each other.
- **Fixed:** the graph hotfix (`c5404b75`) for every reader with one design.

### Round 9 (2026-11-08 to 2026-11-09, `5f36e6a2` to `a4440c7f`)

- **Found:** 62 findings, 3 high; goal classes 27 in round 8's scope, 56 with new scope, as the graph check ran in all six areas and the code measures were used for the first time (the six `round9-*.md` files; no separate report). The high: the UX explorer crashing on a reopened graph.
- **Fixed:** the high, the 4 regressions, and splits of the oversized classes (`Graph`, `PracticeGuidance` and others), every change through the metrics gate: nothing got worse and 16 of 23 guarded measures improved ([code-metrics-trend.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\code-metrics-trend.md)).
- **Left open at the end of that refactor:** no round 10 was run; the class sizes kept by decision records (`FidelityGuidance`, `GuidanceAction`, `TypeScriptToolset`, `Ticket`); the measures still short of target. All in [remaining-work-plan.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\remaining-work-plan.md).

### Release 1.2, scoped validates during the fix waves (2026-11-18 to 2026-11-21)

- Each fix wave of exploratory testing validated the files it changed, at the code, model and modules fidelities of Clean Engineering and the Stories and UX fidelities: the earlier reports in [validation-reports](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\README.md).

### Release 1.2, whole-code validate and the seven judges (2026-11-21, `33b3839e3`)

- **Found:** 388 graph findings in 24 rules ([clean-engineering-code-20261121T212842.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261121T212842.md)). Seven judges then read every production file and wrote 1,106 findings, local fixes and 86 design proposals (the `judgment-*.md` files in [judge-round](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round)).
- **Fixed:** each area's local fixes (`631e9b19d` to `21158c99b`). The 86 proposals were merged into 25 and 13 smaller changes ([design-proposals.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round\design-proposals.md)), approved by the person, and built in four refactor rounds ending at `3c77725bc` (2026-11-22).
- **Measured:** the reshape left the size and complexity measures slightly worse, since nobody measured between rounds: functions over 3 parameters 72 → 95, module import loops 2 → 4 ([code-measures-before-and-after-judge-fixes.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\judge-round\code-measures-before-and-after-judge-fixes.md)).

### Release 1.2, cross-file checks built (2026-11-22, `73245e7a8` to `87a3b8c75`)

- The size and complexity limits became graph rules measured with lizard, and rules of scope "all" read the whole repository: unused classes and operations, module cards against the code, and judged candidates. The plan is [check-clean-engineering-across-files.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\_backlog\check-clean-engineering-across-files.md).

### Release 1.2, second whole-code validate (2026-11-23, `04300fa`)

- **Found:** 2,733 violations and 2,972 candidates ([clean-engineering-code-20261123T205308.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261123T205308.md)). 1,831 of the violations only say lizard is not installed; 529 come from rules that did not report at the first run. What was found, what was fixed, why the number jumped and what is open are in wave 6 of section 2 of [release-1-2-fixes-report.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\release-1-2-fixes-report.md), the measures in its section 6.
- **Fixed:** 164 of the first run's 388; the import loop between the measures and the reading (`c7e865340`).

### Release 1.2, latest whole-code validate (2026-11-24 01:08 UTC, `94b59f9`) — the current state

- **Found:** 2,616 violations in 22 rules and 2,920 candidates ([clean-engineering-code-20261124T010849.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261124T010849.md)). 1,808 of the violations (`limit-paths-through-a-function` 666, `keep-functions-readable` 666, `limit-class-complexity` 476) say lizard is not installed. Of the other 808: `keep-class-methods-sharing-data` 208, `declared-exception-raised-by-a-test` 163, `use-typed-signatures` 137, `limit-operation-parameters` 133, `seam-names-current-code` 76, and fewer than 20 each in the rest (`one-way-deps` 3).
- **Fixed since the run before:** 69 findings.
- **Then:** a review pass (`52d22fe88`) ended the installation import cycle and brought the release and session-diagnostics module cards in line; its scoped validate is [clean-engineering-code-20261124T013014.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\validation-reports\clean-engineering-code-20261124T013014.md) (323 violations and 101 candidates over the files it touched, 9 fixed). Design proposals 8 (c), the node type tables, and 21 (c), `NameFacts`, were built and passed the metrics gate (`689eba692`, `57d723cbd`, `857091cb9`). `repo-model2.drawio` was removed and `repo-model.whiteboard` drawn again (`62fe55b10`, `86fceac2c`).

## Still open

1. Install lizard into the tests' and the dev lane's Python, so the 1,808 "not installed" findings become measures, then run the heavy tier once.
2. Find why the metrics gate reported every measure unchanged after large changes ([metrics_gate.py](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\scripts\metrics_gate.py)).
3. The 76 module-card drift findings (`seam-names-current-code`). The 3 `one-way-deps` findings are the three files of one loop in `harness/installation`, ended by `52d22fe88` after that run; a whole-code validate has not confirmed it yet.
4. The 163 declared exceptions no test raises ([test-every-declared-exception.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\_backlog\test-every-declared-exception.md)) and the 9 `refuse-unreadable-input` violations.
5. The 2,920 judged candidates, which need a judge pass (`judge_all`); whether to run a second judge round is the person's decision.
6. Bolt's chain walk for BDD observation links (`10c77ff64`, `5a7c43cc3`): measure the invokes edges before and after with `invokes_dump.py`.
7. "One thing is one node in the graph" ([one-thing-one-node-in-the-graph.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\_backlog\one-thing-one-node-in-the-graph.md)), after every robot is done; until then the cross-file rules run on the code fidelity only.
8. From the earlier refactor and still not measured again: the targets in [remaining-work-plan.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\clean-engineering-review\refactor-rounds-1-9\remaining-work-plan.md).

The full list of the release's open items, tests and defects included, is section 7 of the release report and the latest handoff, [handoff-20261123T2130.md](C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\handoff-20261123T2130.md).
