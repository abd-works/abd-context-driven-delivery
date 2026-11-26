---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Run Test Tiers One At A Time

Story map: [Run Test Tiers One At A Time](../../../.context/story-map.md#e-run-test-tiers-one-at-a-time). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the test runner today (`harness/release/test_runs.py`) and is tested by `harness/release/test_runs_spec.py` and `harness/release/test_runs_heavy_spec.py`. Asked for on 2026-11-23 (closing choice 12 of the release-1-2-fixes exploratory testing: whether the test runner gets a story on the map). No story test file runs them: the specs drive the runner, the cadence and `scripts/test.ps1` directly.

### Domain terms

- ++test runner++ — `python -m harness.release.test_runs <tier>`, which runs one tier on a commit of the main checkout and keeps the run in the [record of test runs](../../../harness/release/.context/release-model.md#testrunrecord) ([TestRunner](../../../harness/release/.context/release-model.md#testrunner)).
- ++cadence++ — what starts a tier that is due, when the health report asks ([TestCadence](../../../harness/release/.context/release-model.md#testcadence)).
- ++test run++ — one run of one tier on one commit: running, passed, failed or abandoned ([TestRun](../../../harness/release/.context/release-model.md#testrun)).

> In steps: ++example++ names an example in a table below.

## Examples

### tier runs

| run | tier | started by | on |
| --- | --- | --- | --- |
| ++heavy run by test.ps1++ | heavy | `scripts/test.ps1 -Suite heavy`, in the main checkout's own folder | the checkout's files as they are |
| ++e2e run by the runner++ | e2e | `python -m harness.release.test_runs e2e` | main's commit |
| ++killed heavy run++ | heavy | the runner, killed while its tier worked | commit abc123 |
| ++noon heavy run++ | heavy | the cadence, recorded as running at noon | main's commit |

## Story: Run Test Tier

#### Scenario: Run a tier while another runs on the checkout

> Test: unit: harness/release/test_runs_spec.py 'that scripts/test.ps1 runs in the checkout's own folder' ('should keep a run by hand waiting until it ends'); heavy: harness/release/test_runs_heavy_spec.py 'a tier started with scripts/test.ps1' ('should keep a run the runner starts beside it waiting until it ends').

*Given* scripts/test.ps1 runs the heavy tier in the main checkout's own folder, as ++heavy run by test.ps1++
*When* the Person starts `python -m harness.release.test_runs heavy` on the same checkout
*Then* the [test runner](../../../harness/release/.context/release-model.md#testrunner) says it waits for the heavy run process of test.ps1, and starts its tier once that run ends

#### Scenario: Start test.ps1 while another tier runs on the checkout

> Test: unit: harness/release/test_runs_spec.py 'that another process is running the other tier' ('should run nothing until that run ends').

*Given* the [test runner](../../../harness/release/.context/release-model.md#testrunner) runs the e2e tier of the main checkout, as ++e2e run by the runner++
*When* the Person starts scripts/test.ps1 -Suite heavy in the main checkout's folder
*Then* test.ps1 says it waits for the e2e run process, and runs its specs once that run ends

#### Scenario: Keep the cadence from starting beside a tier run by hand

> Test: unit: harness/release/test_runs_spec.py 'that scripts/test.ps1 runs in the checkout's own folder' ('should keep the cadence from starting a tier'); heavy: harness/release/test_runs_heavy_spec.py 'a tier started with scripts/test.ps1' ('should keep the cadence from starting a tier while it runs').

*Given* scripts/test.ps1 runs the heavy tier in the main checkout's folder, as ++heavy run by test.ps1++
*And* the e2e tier last started a day ago
*When* the health report asks the [cadence](../../../harness/release/.context/release-model.md#testcadence) what is due
*Then* the cadence starts nothing until test.ps1 ends

## Story: Record Test Run

#### Scenario: Run a tier again after a killed run

> Test: unit: harness/release/test_runs_spec.py 'that a process that was killed left running on this commit'; heavy: harness/release/test_runs_heavy_spec.py 'that is killed while its tier works' ('should record a run of its own, the killed run before it recorded as abandoned').

*Given* a heavy run on commit abc123 was killed while its tier worked, as ++killed heavy run++
*When* the Person runs the heavy tier again on abc123
*Then* the [record of test runs](../../../harness/release/.context/release-model.md#testrunrecord) holds the new run as the latest heavy run, and the killed run before it as abandoned

#### Scenario: Finish the run the cadence started

> Test: unit: harness/release/test_runs_spec.py 'run to its end' ('should finish the run the cadence started, not a new one') and 'that the cadence recorded under the process it started, which started this one'.

*Given* the [cadence](../../../harness/release/.context/release-model.md#testcadence) recorded a heavy run as running at noon and started a process to run it, as ++noon heavy run++
*When* that process runs the tier to its end
*Then* the [record of test runs](../../../harness/release/.context/release-model.md#testrunrecord) holds one heavy run started at noon, with its result

#### Scenario: Keep a tier run by hand out of the results

> Test: unit: harness/release/test_runs_spec.py 'that scripts/test.ps1 runs in the checkout's own folder' ('should not be the tier's latest result').

*Given* scripts/test.ps1 ran the heavy tier on uncommitted edits and passed, as ++heavy run by test.ps1++
*When* the release checks the latest heavy run
*Then* the latest heavy run is the one the [test runner](../../../harness/release/.context/release-model.md#testrunner) recorded on a commit, not the test.ps1 run
