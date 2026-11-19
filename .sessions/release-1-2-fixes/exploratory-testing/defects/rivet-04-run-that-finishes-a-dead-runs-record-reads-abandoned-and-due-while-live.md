# A run that goes on with a dead run's record keeps the dead process id, so while it runs the health report says abandoned and the cadence finds the tier due

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestCadence._started` (returns the held run without writing its own pid), `TestCadence.due`, `_settled`
- **Severity:** wrong result

## Steps
Sandbox as in rivet-01, RIVET_SLEEP=20; an e2e run recorded as passed just now so heavy alone can be due. `due.py` prints `TestCadence(main_checkout(repo), TestRunRecord(home)).latest_runs` and `.due()`.
1. `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`; after four seconds kill it (`taskkill /F /PID 6096`).
2. Run the same command again on the same commit (pid 3640). It goes on with the record the dead run left (same `started_at`, pid 6096).
3. While it runs: `python C:\dev\_et\rivet\due.py C:\dev\_et\rivet\work\repo C:\dev\_et\rivet\cdd_home`

## Expected
While pid 3640 runs the tier, the health report shows heavy as running and `due()` is empty ("none while a run is live").

## Actual
```
health report states: [('heavy', 'abandoned', 6096), ('e2e', 'passed', 1)] due: ['heavy']
```
The record still names the dead pid 6096, so the live run reads as abandoned, an abandoned run is due at once, and the next health report read starts another heavy run on the checkout beside the live one. A third run started by hand does not wait either, for the same reason. The finished record also keeps pid 6096 and the dead run's start time, so the killed run is never shown as failed or abandoned: its record becomes the second run's result.

## Tier that should catch it
unit - a spec for `run_now` with a record left running by a dead pid on the same commit, checking the pid saved before the runner starts; test_runs_spec.py checks the take-over but not which pid the record holds during the run.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). The report's `due.py` is not in the report; I wrote its two lines from rivet-04's description. RIVET_SLEEP=20. The first run killed after four seconds; the second (pid 13332) went on with its record, which kept pid 45824 and the first start time. While the second ran: `health report states: [('heavy', 'abandoned', 45824), ('e2e', 'passed', 1)] due: ['heavy']`. The finished record still names pid 45824. The killed run's test.ps1 was also still running beside the second, as in rivet-03.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestCadence._started`: a run that goes on with a dead run's record does not write its own pid into it, so `TestRun.is_live` is false for a run that is live.
- Shares its cause with: rivet-02, rivet-03, rivet-05
