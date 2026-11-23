# test-runs.json read while another process writes it reads as "no run has ever run", and writes by two processes are not held against each other

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestRunRecord._read` (any OSError or ValueError answers `{}`), `TestRunRecord.save` (`write_text` over the live file; `run_now` saves the finished run outside `claimed()`; `self.lock` is a thread lock, one per process)
- **Severity:** wrong result
- **Also see:** sparky-01 and sparky-03, the same pattern in the prompt queue's file

## Steps
1. `python C:\dev\_et\rivet\race.py write C:\dev\_et\rivet\cdd_home` - calls `TestRunRecord.save(run)` in a loop for six seconds.
2. At the same time `python C:\dev\_et\rivet\race.py read C:\dev\_et\rivet\cdd_home` - calls `record.latest(TestTier.HEAVY)` in a loop.
3. Separately: empty the file, or cut it to its first 150 bytes, then run `due.py` and a heavy run.

## Expected
A reader sees the run that is recorded, the one before or the one after the write; a damaged record is reported, not taken for an empty one.

## Actual
```
reads 31476 read as no run at all: 3836
saves 9258
```
One read in eight saw no heavy run at all while one was recorded as running throughout. `TestCadence.due()` and `_live_elsewhere()` build on that read, so a health report read that meets a write finds every tier due and no run live, and starts a tier beside the live one; a finishing run's read-then-write (not under the claim) that meets the cadence's write drops one of the two.

With the file emptied or truncated, `due.py` prints `health report states: [] due: ['e2e', 'heavy']` and the next run writes a fresh file over it without a word: the earlier results, and whether the last run failed, are gone, so the next failure is called new.

Shown: the empty read under a real concurrent write, and the silent overwrite. Not shown end to end: a second tier started by it (the window is a few milliseconds per write).

## Tier that should catch it
heavy - two real processes on one file; the unit spec uses one process, where the thread lock does hold.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run on a sandbox repository of my own built as rivet-01 describes, a copy of `scripts/test.ps1` and three heavy specs, with CDD_HOME in the sandbox (`C:\dev\_et\sparky\confirm\rivet\rv.py`). The report's `race.py` is not in the report; I wrote the two loops it describes. In six seconds: `reads 51055 read as no run at all: 5789`, `saves 11008`, about one read in nine. With the file emptied, and cut to its first 150 bytes: `health report states: [] due: ['e2e', 'heavy']`, and the next run wrote a fresh record over it with no word, its failure marked `is_new_failure: true`.
- Cause, if you found it: `harness/diagnostics/test_runs.py` `TestRunRecord._read` answers an empty record for any `OSError` or `ValueError`, which is what a read meeting a write, an empty file and a truncated file all give; `save` then writes over it.
- Shares its cause with: rivet-07 (the record is read with no check of what it holds); sparky-01 and sparky-03 (the prompt queue's file read as empty and written over, the same way)
