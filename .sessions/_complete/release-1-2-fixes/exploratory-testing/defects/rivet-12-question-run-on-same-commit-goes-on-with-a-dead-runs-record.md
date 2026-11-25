# Question: is a run started after a killed run, on the same commit, meant to go on with the dead run's record?

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestCadence._started`, `TestRun.is_run_by_this_process`
- **Severity:** answered question

## Steps
Sandbox as in rivet-01 (`C:\dev\_et\rivet\work\repo`, CDD_HOME=C:\dev\_et\rivet\cdd_home), RIVET_SLEEP=20.
1. `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`; after four seconds `taskkill /F /PID <pid in test-runs.json>`.
2. Run the same command again without a commit in between, and read `test-runs.json` when it ends.

## Expected
Unclear. `_started` says: "A run left as running by a process that ended, on another commit, is not taken over: this run tests HEAD", which reads as: on the same commit it is taken over, on purpose (it is what lets the cadence's background process finish the run the cadence recorded).

## Actual
The second run records nothing of its own: the one entry keeps the killed run's `started_at` and process id and gets the second run's result. So the killed run is never shown as failed or abandoned, the record says one run happened where two did, and the run's length reads from the first start to the second end. rivet-04 is what follows from keeping the dead process id while the second run is live.

Should a run by hand always record a run of its own, and only the process the cadence started (rivet-02) finish the cadence's record?

## Tier that should catch it
unit - `run_now` over a record left running by a dead process on the same commit; test_runs_spec.py covers the other-commit case.

## Answer (2026-11-23)

Yes: a run by hand always records a run of its own, the run a killed process left running is recorded as abandoned, and only the process the cadence started (named by `--started`) finishes the cadence's record. Built in `harness/release/test_runs.py` (`TestCadence._taken`, `_is_recorded_for_this_process`); tested by `harness/release/test_runs_spec.py` "that a process that was killed left running on this commit" (and its nested context for the cadence's own process) and `harness/release/test_runs_heavy_spec.py` "that is killed while its tier works, and run again on the same commit"; no story on the map yet: the scenario "Run a tier again after a killed run" under the proposed story Person --> Run Test Tier is proposed to the lead.
