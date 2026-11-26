# Check Story Tests Against Recorded Tiers

Analysis and planning: the story here is not built yet. Decided by the person on 2026-11-22, as the follow-up to change 6 of the defect analysis (`.sessions/release-1-2-fixes/exploratory-testing/defect-causes.md`).

**Outcome:** validate fails a story of a module whose record names the server or web tier when the story has no test at that tier, so a missing server or browser test is found by a check and not by a judge.

## What is there today

- A session records, for each module, the test tiers it uses and the test tool of each (`test_tiers` in `session.json`, `space/session/test_tiers.py`), filled by generate and render as they write tests (`cdd_guidance/practices/tdd/module_tiers.py`).
- The TDD supplement's rule `story-tested-at-each-recorded-tier` (`cdd_guidance/practices/tdd/tdd.md`) is judged by validate, not checked on the graph.
- TDD's graph overlay records the tier of each story test file on its Story node (`cdd_guidance/practices/tdd/graph_overlay.py`).

## Why it is not a graph check yet

A story test sits under `story_tests/<epic>/<sub-epic>/`, and nothing on the graph joins it to the module it tests. A check that joined them by matching names would repeat the `name-matching` defects of release 1.2, so the check waits for a join by identity.

## Story

- (S:system) Knowledge Graph --> Check Story Tests Against Recorded Tiers: once a story test is joined to its module by identity, such as by the operations its When steps call, which Clean Engineering reads into classes of a module, the graph rule reads the session's record and each story's test files and their tiers, and reports a story of a module that records the server or web tier with no test at it. The rule then moves from judged to checked in `tdd.md`, with a failing and a repaired example.

## Open question

- Whether generate should tell the server and web tiers from the module's code (a class the module publishes as a tool of a server, a page it serves) is not decided; generate asks the agent today.
