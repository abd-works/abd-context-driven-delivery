# A run recorded as running whose process id now belongs to another program makes every later run wait for ever, and the cadence never finds a tier due

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestRun.is_live` (`RunningProcess(pid).alive` alone), `TestCadence._started`, `TestCadence.due`
- **Severity:** blocks work

## Steps
Sandbox as in rivet-01.
1. Start any long-lived unrelated program and note its pid (here `python -c "import time; time.sleep(45)"`, pid 16888). This stands for Windows giving a dead run's pid to a new process, as it does after a restart.
2. Put in `cdd_home\test-runs.json` a run left as running nine days ago with that pid:
   `{"heavy": {"latest": {"tier": "heavy", "outcome": "running", "pid": 16888, "commit": "z", "started_at": "2026-11-10T10:00:00+00:00"}}}`
3. `python C:\dev\_et\rivet\due.py C:\dev\_et\rivet\work\repo C:\dev\_et\rivet\cdd_home`
4. `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`

## Expected
A run "recorded as running, but its process is gone without a result, such as when the computer restarted" reads as abandoned (`RunOutcome.ABANDONED`), the tier is due at once, and a run by hand starts.

## Actual
The nine-day-old run reads as running, nothing is due, and the run by hand prints the same line every ten seconds with no end (stopped by hand after 24 s):
```
health report states: [('heavy', 'running', 16888)] due: []
waiting for the heavy run process 16888 started at 2026-11-10T10:00:00+00:00 to end
waiting for the heavy run process 16888 started at 2026-11-10T10:00:00+00:00 to end
```
Liveness asks only whether some process has that id: not whether it is a python or test.ps1 process, nor whether it started before the run did, nor how old the run is. Heavy and e2e stop running on their cadence, silently, until the other program ends; the waiting message does not say how to get out (delete the entry).

## Tier that should catch it
unit - `RunningProcess` can be faked alive for an old record; test_runs_spec.py has only "live in another process" and "process gone", never "alive but not the run".

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). The report's `due.py` is not in the report; I wrote its two lines from rivet-04's description. With a nine-day-old `running` entry whose pid a sleeping Python program now has: `health report states: [('heavy', 'running', 43496), ('e2e', 'passed', 1)] due: []`, and the run by hand was still printing `waiting for the heavy run process 43496 started at 2026-11-10T10:00:00+00:00 to end` after 24 s. Once the other program ended the same read answered `abandoned` and `due: ['heavy']`.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestRun.is_live`: `self.outcome is RunOutcome.RUNNING and RunningProcess(self.pid).alive`, with no look at what the process is or when it started.
- Shares its cause with: rivet-03, rivet-04; rivet-10 (a wait with no end and no way out said)
