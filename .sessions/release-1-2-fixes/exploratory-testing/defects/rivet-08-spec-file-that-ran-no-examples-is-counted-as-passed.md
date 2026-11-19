# A spec file that ran no examples is counted as passed: a file in a folder whose name has a space is never run, and neither is noticed

- **Charter:** Round 1 - the test runner and its cadence as two chats starting tiers on one checkout
- **Tester:** Rivet
- **Story:** no scenario covers this
- **Module and class:** scripts/test.ps1 - `Start-SpecBatch` (`Start-Process -ArgumentList ($Arguments + $Relatives)` joins the paths with spaces, unquoted), `Get-FailedFiles` (a batch fails only on a non-zero exit or a `Failure/Error:` line)
- **Severity:** wrong result

## Steps
1. `git clone C:\dev\_et\rivet\work\repo "C:\dev\_et\rivet\work\repo with space"` (the sandbox of rivet-01, with a copy of scripts/test.ps1).
2. Add `my specs/space_heavy_spec.py` and `my specs/space_spec.py`, each one example that always fails (`assert False, "space spec ran"`), and commit.
3. `python -m harness.diagnostics.test_runs heavy "C:\dev\_et\rivet\work\repo with space" "C:\dev\_et\rivet\cdd home 2"`
4. `powershell -File "C:\dev\_et\rivet\work\repo with space\scripts\test.ps1"` (unit tier)
5. In the first sandbox, add `broken/empty_heavy_spec.py` holding only a comment and run the heavy tier.

## Expected
Every spec file the run counts is run, and "N/N files passed" means each of them ran its examples and none failed (tdd.md: the tiers are what say the code works; test.ps1: "A run that stopped before counting its files proved nothing, so it fails").

## Actual
The always-failing files are counted as passed, because Mamba was handed `my` and `specs/space_heavy_spec.py` as two paths, found neither, ran nothing and exited 0:
```
[my specs .. my specs] 1 files, 0.8 s
0 examples ran in 0.0000 seconds
...
3/4 files passed
FAILED specs/fail_heavy_spec.py        <- the planted failure in specs/, not the one in "my specs"
```
Unit tier: `Mamba specs (3)`, only the two files outside "my specs" print examples, `2/3 files passed`, and the one failure listed is the slow example, not the space spec.
The empty spec file (step 5) is likewise `0 examples ran` and counted in the passed total.
The checkout's own path may hold spaces: that worked, and so did a record folder with a space. No spec path in the CDD repository holds a space today (`git ls-files` finds none), so this bites a project that uses test.ps1's pattern, or the first folder someone names with a space.

Smaller, seen in the same runs: a heavy spec file that fails to import is reported as `FAILED broken .. broken`, its batch's folder range and not its file name, so two such files give two identical lines.

## Tier that should catch it
heavy - a real test.ps1 over a folder with a space and a file with no examples; nothing runs test.ps1 itself against a planted layout.
