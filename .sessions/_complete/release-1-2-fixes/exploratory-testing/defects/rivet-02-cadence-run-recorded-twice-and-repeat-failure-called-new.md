# A run the cadence starts from a chat is recorded twice, half a second apart, and a repeated failure is then called a new failure

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this (known open item: main handoff-20261118T173207.md, Outstanding 2 - still happens after the fix-e2e-42d8bf7d5 merge)
- **Module and class:** harness/diagnostics/test_runs.py - `TestCadence._started`, `TestRun.is_run_by_this_process`, `TestRunRecord.save`
- **Severity:** wrong result

## Steps
Sandbox repo on main as in rivet-01; CDD_HOME=C:\dev\_et\rivet\cdd_home; RIVET_SLEEP=6. The record holds a finished heavy run that FAILED, started two hours ago (pid 18624), and an e2e run just passed, so heavy alone is due.
1. From a command a Claude Code chat runs (so the process is in the chat's job), run `python C:\dev\_et\rivet\cadence.py C:\dev\_et\rivet\work\repo C:\dev\_et\rivet\cdd_home`, which calls `TestCadence(main_checkout(repo), TestRunRecord(home)).start_due()`.
2. Read `test-runs.json` every half second, and when the run ends.

## Expected
One run: the process the cadence starts finishes "a run the cadence recorded as running" (`run_now` docstring). The failed run from two hours ago stays the previous run, so this second failure in a row is not a new failure (`is_new_failure`: "It failed, and the run of its tier before it did not").

## Actual
Two runs, 0.47 s apart. The cadence records pid 48372 (the launcher `BackgroundStart` starts), the real runner is its child 13732; `is_run_by_this_process` is false for it because 48372 is alive and is not its own pid, so it records a second run over the first:
```
{'latest': ('18:11:30.542', 'running', 48372), 'previous': ('16:11:30.358', 'failed', 18624)}
{'latest': ('18:11:31.010', 'running', 13732), 'previous': ('18:11:30.542', 'running', 48372)}
...at the end:
{'latest': ('18:11:31.010', 'failed', 13732), 'previous': ('18:11:30.542', 'running', 48372)}
```
- The real previous result (failed, pid 18624) is pushed out of the record by the launcher's entry.
- The finished run has `"is_new_failure": true` although the tier's run before it also failed, so the chat raises the "new failure" toast again on every failing run.
- The launcher's entry stays `"outcome": "running"` in the file for ever (its process is gone).
`_live_elsewhere` already treats the parent process as this run (`os.getppid()`); `_started` does not.

## Tier that should catch it
heavy - only a real `BackgroundStart` from inside a job that refuses breakaway gives the launcher-and-child pair; test_runs_spec.py has a context for "recorded by the id of this process's parent" but checks only that the run does not wait, not that it records one run.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). The report's `cadence.py` is not in the report; I ran its one line, `TestCadence(main_checkout(repo), TestRunRecord(home)).start_due()`, from a command my chat ran, with heavy recorded as failed two hours ago (pid 18624). The record went: latest running pid 38412 with previous the failed 18624; 0.47 s later latest running pid 13512 with previous running 38412; at the end latest `failed`, pid 13512, `is_new_failure: true`, previous still `running` 38412.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestCadence._started` with `TestRun.is_run_by_this_process`: the cadence records the launcher's pid, and the runner it starts does not take that record as its own.
- Shares its cause with: rivet-04 (the pid in the record is not the process that runs the tier)
