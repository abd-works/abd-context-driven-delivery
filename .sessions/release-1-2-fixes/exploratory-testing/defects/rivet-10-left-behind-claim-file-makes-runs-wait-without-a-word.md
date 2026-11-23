# A test-runs.claim file left behind makes a run wait without printing anything: a minute when it is fresh, for ever when its date is ahead of the clock

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestRunRecord.claimed`, `TestCadence._started` (prints only when another run is live), `TestCadence.start_due`
- **Severity:** misleading message

## Steps
Sandbox as in rivet-01, RIVET_SLEEP=0 so a heavy run takes about four seconds. No run is live.
1. Create `C:\dev\_et\rivet\cdd_home\test-runs.claim` (as a process killed between taking the claim and releasing it leaves it). `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`
2. Set the claim file's date ahead of the clock (`touch -d 2027-01-01`), as a clock correction or a file copied from another machine gives. Run the same command, then `cadence.py` (which calls `start_due()`).

## Expected
"A claim older than a minute was left by a process that died holding it, and is taken over"; while it waits, the run says what it is waiting for, as it does for a live run.

## Actual
1. The run prints nothing for 63 seconds, then runs and passes (`took 63 s`). Nothing says a claim is held or by whom.
2. The run prints nothing and never starts (stopped by hand after 85 s). `start_due()` answers `None` every time, so the cadence starts no tier again until someone deletes the file; the health report shows nothing wrong (`due: []`).
The claim file holds no process id, so a claim whose holder is dead cannot be told from a held one except by its age, and age fails when the date is ahead.

## Tier that should catch it
unit - `claimed()` over a claim file with a date ahead of the clock, and `_started` with a held claim and no live run; the spec covers a stale claim and a fresh one, not what the waiting run prints.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). With an empty `test-runs.claim` just made, the run printed nothing for the first 20 s and took 62 s in all; its output never mentions a claim. With the claim file's date set to 2027-01-01 the run had printed nothing and was still going after 80 s, when I stopped it, and `start_due()` answered `None`.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestRunRecord.claimed`: a claim is taken over only when `time.time() - claim.stat().st_mtime` is over a minute, which a date ahead of the clock never is; the file holds no process id, and whoever waits on it prints nothing.
- Shares its cause with: rivet-05 (a wait with no end and no word on how to get out)
