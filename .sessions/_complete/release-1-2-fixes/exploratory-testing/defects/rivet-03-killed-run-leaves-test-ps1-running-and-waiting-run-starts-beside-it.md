# Killing a tier run leaves its test.ps1 running, and a run that was waiting starts its own beside it on the same checkout

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestRunner.run` (starts powershell as a plain child), `TestRun.is_live`, `TestCadence._live_elsewhere`
- **Severity:** wrong result

## Steps
Sandbox as in rivet-01, RIVET_SLEEP=30 (the sleeping heavy spec takes 30 s).
1. Chat one: `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`
2. Five seconds later, chat two: the same command. It prints `waiting for the heavy run process 30288 ... to end`.
3. Kill chat one's run: `taskkill /F /PID 30288` (the pid in test-runs.json), as stopping the command in a chat or closing its terminal does.
4. Ten seconds later list the processes whose command line names the sandbox.

## Expected
One tier at a time on a checkout: "Every run of a tier works in the one main checkout ... so a second run started beside a live one fails on what the first holds" (`_started` docstring); handoff: "Never start a tier while another chat runs one on the same checkout".

## Actual
The killed python's `powershell.exe ... test.ps1 -Suite heavy` (pid 8624, parent 30288) keeps running its specs, and the waiting run, seeing pid 30288 dead, starts a second test.ps1 (pid 35720) in the same folder:
```
 8624  30288  powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\dev\_et\rivet\work\repo\scripts\test.ps1 -Suite heavy
46252   6476  python.exe -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo
35720  46252  powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\dev\_et\rivet\work\repo\scripts\test.ps1 -Suite heavy
```
Liveness is judged by the recorded python process alone; the tier itself runs in its child, which outlives it. On the real checkout that is two heavy or e2e tiers on one port and one folder, each failing on what the other holds.

## Tier that should catch it
heavy - needs real processes: a run killed while its test.ps1 child lives. The unit spec's fake runner has no child process.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). RIVET_SLEEP=30. Chat two printed `waiting for the heavy run process 42380 ... to end`. Twelve seconds after `taskkill /F /PID 42380`, two `powershell.exe ... test.ps1 -Suite heavy` were running on the one repository: pid 44448, whose parent is the killed 42380, and pid 6948, started by the run that had been waiting.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestRunner.run` starts powershell as a plain child, which outlives it, and `TestRun.is_live` asks only whether the recorded python process is alive.
- Shares its cause with: rivet-04, rivet-05 (a run's liveness is one recorded process id and nothing else)
