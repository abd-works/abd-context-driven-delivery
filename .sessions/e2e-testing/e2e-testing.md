# e2e-testing

Taken from the backlog item `.sessions/_backlog/review-end-to-end-screens-against-the-previous-run.md`, widened from regression only to the whole of end-to-end testing.

Add guidance and code so end-to-end testing is done in three phases, and every phase records a screenshot for each story test step, keyed by story › scenario › step. The screens are what tie the phases together: the AI compares each step's screen with the same step's screen from the phase before, and a change no test explains is a defect.

Passing tests only prove the assertions someone wrote, and a screen can break in ways no assertion checks: a field missing, a label changed, a layout collapsed, a notice no longer shown. A person sees that at once in the screenshot, so the AI looks at the screenshots too.

## The three phases

| Phase | Who drives the app | Compared with | Question it answers |
|---|---|---|---|
| 1. Manual test | The AI, following the scenarios by hand | The scenario text | Does the system do what each scenario means? |
| 2. Automated tests | The new or extended Playwright story tests | The manual run (phase 1) | Do the automated tests reach the same screens the manual run accepted? |
| 3. Regression | The automated tests, on a later run | The last accepted automated run | Has anything reverted or changed without a reason? |

### 1. Manual test: follow the scenarios with the AI

The first test of a new or changed scenario is manual. The AI drives the running app through each scenario step by step, as a person would, and takes a screenshot after every Given, When and Then.

For each step it reads the Given/When/Then text and asks whether a person looking at the screen would agree the step happened: the Given's state is visible, the When's action took effect, the Then's outcome is shown with the right values, labels and messages. Each step gets a verdict: **meets the intent**, or **misses the intent** with what is wrong.

When a step misses, the AI fixes the code (or raises the scenario as wrong with the person) and walks it again. The phase ends with a report of every step's screen and verdict. When the person accepts it, the manual run is the reference the automated tests must match.

### 2. Automated tests: build, compare, validate, fix

The AI then writes or extends the automated story tests for those scenarios. Each automated step records its screenshot the same way, and the AI compares it with the same step from the accepted manual run:

- **Same screen:** the automated test reaches what the manual run reached.
- **Different screen:** the test sets up different data, takes a different path, or asserts too little. The AI fixes the test, or the code, and reruns.
- **Unsure which is right:** go back to phase 1 and walk that step manually again, then compare once more.

The report for this phase shows manual and automated screens side by side with a verdict on each changed pair. When every pair matches (or the change is explained and the person accepts it), the automated run becomes the first regression baseline.

### 3. Regression: did anything revert?

Every later automated run (during ticket work, by hand, or the daily e2e run the cdd server schedules in `harness/diagnostics/test_runs.py`) compares each step with the last accepted automated run. A run is not finished until its screens have been reviewed.

1. **Filter by pixels first.** Only pairs that changed go to the AI. A cheap block diff (pml-web's 8px block check) keeps the AI from reading hundreds of identical screens.
2. **The AI judges each changed pair** using both screenshots, the step's Given/When/Then text, and the stories and code changed since the baseline (this ticket's changes, or for a scheduled run the commits on main since then). The verdict is one of:
   - **intended:** the change follows from one of those story or code changes, and the AI cites which one.
   - **regression caught:** a test already fails for it, so fix the code.
   - **missed by the tests:** the screen is wrong and nothing failed.
   - **noise:** timing, animation, or a value the system mints. The AI makes the harness deterministic instead of accepting the noise.
3. **For each "missed by the tests":** add the test at the layer that owns the behaviour (story markdown and the domain story test for a rule or value, the screen story for a control or label, CSS only for pure look). See it fail, fix the code, and rerun.
4. **Repeat** until every changed pair is "intended". The person reviews the report, and accepting it makes this run the new baseline.

## Report

One report shape for all three phases, one page per sub-epic plus a story map page over them all, laid out like pml-web's `compare.html`:

- Story › Scenario › each Given/When/Then step, with the two screens side by side: scenario intent and manual screen (phase 1), manual and automated (phase 2), previous and current automated (phase 3).
- The test result and the AI's verdict on each step, with the AI's reason, and a filter that shows only changed or missed steps.
- The pass, changed, and missed counts for each story and sub-epic.
- A history of earlier runs, without images.

## Guidance

A supplement to Stories acceptance tests and the TDD end-to-end tier, for example `cdd_guidance/practices/visual_review/visual_review.md` (name to decide). It holds the three phases as its process, plus these rules:

- `manual-run-first`: a new or changed scenario is first walked manually by the AI, step by step, before automated tests are written for it.
- `every-step-captured`: every step, manual or automated, records a screenshot and result under its story › scenario › step key.
- `manual-run-checks-the-intent`: each manual step is judged against its scenario's Given/When/Then, and the manual run becomes the reference only when every step meets that intent and the person accepts it.
- `automated-matches-manual`: each automated step's screen is compared with the accepted manual screen, and a difference is fixed in the test or the code, or walked manually again, never accepted unexplained.
- `every-run-reviewed`: every automated run, by ticket, by hand or scheduled, is compared with its baseline before its result counts.
- `baseline-is-last-accepted-run`: regression compares with the last accepted automated run of the same system.
- `ai-judges-every-changed-pair`: every changed pair gets a verdict and a reason, and "intended" cites the story or code change behind it.
- `missed-change-adds-a-test-first`: a change the tests missed gets a failing test at the owning layer before the code is fixed.
- `noise-is-fixed-in-the-harness`: a pair is never accepted as timing noise.
- `person-accepts-the-reference`: only the person's acceptance makes a manual run the reference or an automated run the baseline.

The TDD tier table in `tdd.md` gets one line: end-to-end work runs manual, then automated, then regression, each reviewed screen by screen against the phase before.

## Code

**CDD owns the general parts**, shipped for TypeScript Playwright story tests (CDD's own `*.story.ui.spec.ts` first, then pml-web's `*.story.playwright.ts`):

- A manual walk recorder: the AI drives the app through the browser, and each step's screenshot and verdict are written under the same key and folder layout the automated tests use, so the two runs can be compared.
- A step capture hook for the automated tests: after each Given/When/Then, wait until the page settles, take the screenshot, and write a row to that run's `results.json` (key, step text, result, screenshot path, and whether the run was manual or automated).
- Run folders: `.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>/`, and picking the run to compare with: the accepted manual run for phase 2, the last accepted automated run for phase 3 (pml-web's `release-baseline.ts` and `end-to-end-paths.ts` already do the latter). Screenshots are git-ignored, and accepted references and baselines are kept on a branch, as pml-web does with `e2e-latest`.
- The pixel prefilter, which lists the changed pairs between any two runs.
- The report writer, adapted from pml-web's `report.ts` (story tree, side-by-side screenshots, filters, history).
- A Python toolset with MCP tools `walk(target)` for the manual run, `run(target)` for the automated one, `changed_pairs(target, against)`, `record_verdict(step, verdict, reason)` and `accept(target)`. Long runs go to the background through `harness/process`. The AI reads the image pairs itself and writes its verdicts back through `record_verdict`.
- The scheduled daily e2e run in `test_runs.py` captures screenshots too. When it ends, the cdd server starts the regression review in a background agent session and raises a toast for any step judged "missed by the tests". The fix happens in a ticket, because a scheduled run on main has no ticket to change.
- A line in the server health report: the latest run, its changed and missed counts, and a link to the story map page.

**Each project keeps** starting its app, loading its examples, and its Playwright config.

## Order of work (Flow A: a new boundary)

1. Walk one sub-epic of CDD's own board UI manually with the AI, recording each step's screenshot and verdict under the right key, and build the report. Check it with the person.
2. Add the step capture hook to that sub-epic's automated story tests, compare with the manual run, and fix until they match.
3. Add the baseline choice, the pixel prefilter, and regression review. Rerun with one deliberate visual change, and check that only that pair shows up.
4. Write the guidance and rules, and run the AI judging loop on that change.
5. Add the toolset, verdict recording, acceptance, and the health line.
6. Point pml-web's end-to-end runs at the same recorder, hook and report.

## Done means

- A new scenario is walked manually first, with a screen and verdict for every step, and the person accepts that walk.
- Its automated tests reach the same screens as the manual walk, shown side by side.
- Every later automated run shows the previous and current screens side by side, with a verdict on each changed one.
- A visual change no test caught ends up as a new failing test, a fix, and a rerun, not as an accepted screenshot.
- The reference and the baseline move only when the person accepts a run.

## Open questions

- Baseline: the last run on main, or the last run the person accepted, whichever branch it was on?
- Should the AI also look at unchanged pairs now and then, to catch a screen that has been wrong since before the baseline?
- Should the report be published as an artifact for sharing, or only opened from the run folder?
- Is phase 1 needed again when a scenario only changes slightly, or does the existing automated test plus the regression compare cover it?
