# A test-runs.json that is valid JSON with one unexpected value stops every tier run and every read of the runs with a raw traceback, until someone deletes the file

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** harness/diagnostics/test_runs.py - `TestRun.from_json`, `TestRunRecord._run`, `TestRun.is_due`
- **Severity:** misleading message (and blocks tier runs until the file is removed)

## Steps
Write each of these to `C:\dev\_et\rivet\cdd_home\test-runs.json`, then run `python C:\dev\_et\rivet\due.py <repo> <home>` (reads `latest_runs` and `due()` as the health report does) and `python -m harness.diagnostics.test_runs heavy C:\dev\_et\rivet\work\repo`:
1. `[]`
2. `{"heavy": {"latest": {"tier": "heavy", "outcome": "done", "started_at": "2026-11-19T10:00:00+00:00"}}}`
3. `{"heavy": {"latest": {"tier": "heavy", "outcome": "passed", "started_at": "yesterday"}}}`
4. `{"heavy": {"latest": {"tier": "heavy", "outcome": "passed", "started_at": "2026-11-19T10:00:00"}}}` (no UTC offset)
5. `{"heavy": {"latest": {"tier": "heavy", "outcome": "running", "pid": "abc", "started_at": "2026-11-19T10:00:00+00:00"}}}`
6. `{"heavy": "x"}`

## Expected
An unreadable file is already treated as no record (`_read` answers `{}` for text that is not JSON), so an unreadable entry would be treated the same way, or refused with a message naming the file and the value.

## Actual
1, 2, 3, 5, 6: both commands end in a traceback and the tier does not run; the file is left as it was, so it fails the same way every time:
```
AttributeError: 'list' object has no attribute 'get'
ValueError: 'done' is not a valid RunOutcome
ValueError: Invalid isoformat string: 'yesterday'
ValueError: invalid literal for int() with base 10: 'abc'
AttributeError: 'str' object has no attribute 'get'
```
4: the run by hand works, but `due()` fails with `TypeError: can't subtract offset-naive and offset-aware datetimes` (from `is_due`) on every read while that entry is the tier's latest.

None of the messages names test-runs.json. An entry written by a later CDD version with a new outcome or tier name would do the same to an older server reading the same cdd home.

## Tier that should catch it
unit - `TestRunRecord` over a file with each bad entry; test_runs_spec.py has no example for a record it cannot read.
