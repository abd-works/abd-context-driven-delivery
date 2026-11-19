# A tier run is recorded under the commit it started on, though its specs ran on a later commit

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this (known open item: main handoff-20261118T173207.md, Outstanding 1)
- **Module and class:** harness/diagnostics/test_runs.py - `TestCadence._started` records `_head()` once; `TestRunner.run` runs `scripts/test.ps1` in the live checkout folder
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\rivet\work\repo` (main, with a copy of scripts/test.ps1 and three `*_heavy_spec.py`: fast, failing, and one that sleeps 20 s then prints `git rev-parse HEAD` and whether `marker.txt` exists). CDD_HOME=C:\dev\_et\rivet\cdd_home, PYTHONPATH=C:\dev\abd-cdd-release-1-2-fixes.
1. HEAD is 0ec500c. `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`
2. Nine seconds later, while the sleeping spec runs: `echo x > marker.txt; git add marker.txt; git commit -m "moved during run"` (HEAD becomes fe4bdcc).
3. Read `cdd_home\test-runs.json` when the run ends.

## Expected
The record names the commit whose files the specs ran on (TestRun: "One run of a tier on one commit of main"); the handoff's fix is to run each tier in a detached worktree at the commit it records.

## Actual
The record and the closing line blame 0ec500c (`heavy failed on 0ec500cae`, `"commit": "0ec500caef0a..."`), while the same run's own output, kept in its summary, shows the spec ran on the later commit:
```
HEAD at end of sleep: fe4bdcca39a34c6d377ad1c12e89ec0edd38c203
marker file present: True
```
A spec file added, changed or deleted by the later commit is run (or not run) under the earlier commit's name.

## Tier that should catch it
heavy - it needs a real git checkout that moves while a real test.ps1 runs; test_runs_spec.py stubs the runner and git, so the folder the specs really run in is never looked at.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). RIVET_SLEEP=20, a commit made nine seconds into the run. Closing line `heavy failed on 2aeedc6e7` and the record's commit are the commit the run started on; the run's own summary says `HEAD at end of sleep: a61cd6bda...` and `marker file present: True`.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestCadence._started` records `_head()` once, and `TestRunner.run` runs `scripts/test.ps1` in the checkout's live folder.
- Shares its cause with: rivet-09 (the record says which commit, not which files or which checkout the specs ran on)
