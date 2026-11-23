# Question: a heavy or e2e tier started with scripts/test.ps1 itself is not seen by the runner, which starts its own beside it

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** scripts/test.ps1 (writes nothing to the record); harness/diagnostics/test_runs.py - `TestCadence._live_elsewhere`, `due`
- **Severity:** question

## Steps
Sandbox as in rivet-01, RIVET_SLEEP=25.
1. Chat one: `powershell -File C:\dev\_et\rivet\work\repo\scripts\test.ps1 -Suite heavy`, the command AGENTS.md and test-timing.md give for a tier.
2. Five seconds later, chat two: `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`
3. List the powershell processes running test.ps1.

## Expected
Unclear, hence the question. The runner's promise is one tier at a time on a checkout ("a second run started beside a live one fails on what the first holds"), and the handoff says never to start a tier while another chat runs one on the same checkout. AGENTS.md and `.claude/rules/test-timing.md` send people and agents to `scripts/test.ps1 -Suite heavy | e2e`, not to `python -m harness.diagnostics.test_runs`.

## Actual
The second run does not wait (no "waiting for" line), and two test.ps1 heavy runs work in the one folder at once:
```
41472 parent 10932     <- chat one's test.ps1
15604 parent 17816     <- the runner's test.ps1
```
The cadence would do the same on its hour. Should test.ps1 record its heavy and e2e runs (or refuse while one is recorded live), or should the guidance name `test_runs` as the one entry for those two tiers?

Seen in the same run: killing the runner's test.ps1 child records the run as failed (good), with a summary that ends `Heavy spec (1)` and nothing saying the run was cut short.

## Tier that should catch it
heavy - two real processes; no spec starts test.ps1 beside a recorded run.
