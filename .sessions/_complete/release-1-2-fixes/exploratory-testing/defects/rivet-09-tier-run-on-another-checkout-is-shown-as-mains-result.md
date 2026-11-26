# A tier run by hand on any other checkout is recorded as the cadence's result for main, and puts off main's next run

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `main()` (takes any checkout, default record folder is the cdd home), `TestRunRecord` (keeps tier and commit, not the checkout), `TestCadence.due`
- **Severity:** wrong result (or question: is a hand run meant for the main checkout only? `main()` does not refuse another one)

## Steps
Two sandbox checkouts with different commits: `C:\dev\_et\rivet\work\repo` (main at fe4bdcca3; its last heavy run FAILED) and its clone `C:\dev\_et\rivet\work\repo with space` (12d14d59c). CDD_HOME=C:\dev\_et\rivet\cdd_home.
1. `python -m harness.diagnostics.test_runs heavy "C:\dev\_et\rivet\work\repo with space"` - passes.
2. `python C:\dev\_et\rivet\due.py C:\dev\_et\rivet\work\repo C:\dev\_et\rivet\cdd_home` - the cadence of the first checkout, as its health report reads it.

## Expected
The health report's heavy result is for main ("One run of a tier on one commit of main"; "heavy every hour and e2e every day, each on main"). A run on a ticket's worktree or another repository is kept apart, or refused.

## Actual
```
heavy passed on 12d14d59c
health report states: [('heavy', 'passed', 42960), ('e2e', 'passed', 1)] due: []
```
Main's failed heavy result is replaced by a pass on a commit main does not have, and heavy is not due on main for another hour. In the other direction a failing run in a worktree raises the "new failure" toast for main. While such a run is live, main's cadence starts nothing and a run on main waits for it, though the two share no folder.

## Tier that should catch it
unit - `run_now` on a checkout other than the cadence's, then `due()` and `latest_runs` for main; the spec always uses one checkout.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). The report's `due.py` is not in the report; I wrote its two lines from rivet-04's description. Main's heavy run failed on 85abe0689. The report says the run on the other checkout passes but not how, since the clone holds main's planted failing spec; I removed that spec in the clone with a commit of its own. `heavy passed on 22d250553` there, and main's read then answered `health report states: [('heavy', 'passed', ...), ('e2e', 'passed', 1)] due: []`, the failed run pushed to previous. Main does not have commit 22d250553.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `main()` takes any checkout and records into the cdd home by default, and `TestRunRecord` keeps the tier and the commit, not the checkout.
- Shares its cause with: rivet-01
