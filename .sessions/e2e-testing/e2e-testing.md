# e2e-testing

Taken from the backlog item `.sessions/_backlog/review-end-to-end-screens-against-the-previous-run.md`, and fitted to the end-to-end phases the TDD supplement already has (`cdd_guidance/practices/tdd/tdd.md`).

## What already exists

TDD already sets the end-to-end phases:

- **Flow A, steps 1–2:** run a new boundary end to end directly (the AI drives the real app, or the person does), iterate until it works, and a person verifies it.
- **Flow A, step 3 / Flow B, step 4:** capture that path in an e2e or heavy test and see it pass against the real stack.
- **Cadence:** e2e runs every day, before every release, and at the end of work that touches a browser or an agent (`e2e-run-within-the-day`, `release-follows-a-green-e2e`; the daily run is `harness/diagnostics/test_runs.py`).

This ticket does not change those phases. It adds what they lack: a **screen record for every scenario step, and an AI review of those screens**, so each phase is checked against the one before it. The main gap is regression: today an e2e run only proves the assertions someone wrote, and a screen can break in ways no assertion checks (a field missing, a label changed, a layout collapsed, a notice no longer shown). A person sees that at once in the screenshot, so the AI looks at the screenshots too.

## What each phase gains

Every step of every scenario records a screenshot and its result, keyed by story › scenario › step, whether the AI walked it by hand or a Playwright test ran it.

| TDD phase | Screens compared | Question the AI answers |
|---|---|---|
| Flow A 1–2: run it for real | The scenario text and the manual walk's screens | Does each screen show what its Given/When/Then means? |
| Flow A 3 / Flow B 4: capture in e2e | The accepted manual walk and the new e2e run | Does the automated test reach the same screens the person accepted? |
| Every later e2e run (the main gap) | The last accepted e2e run and this one | Did anything revert or change without a reason? |

### Run it for real: the walk gets a report

While the AI walks a scenario by hand, it screenshots each Given, When and Then and judges it against the step text: the Given's state is visible, the When's action took effect, the Then's outcome is shown with the right values, labels and messages. Each step gets **meets the intent** or **misses the intent** with what is wrong. The walk ends in a report the person reviews, which is how Flow A's "a person verifies the result" is done. When the person accepts it, the walk is the reference for the e2e test.

### Capture in e2e: compare with the walk

The new or extended e2e test records the same steps, and the AI compares each with the accepted walk. A different screen means the test sets up different data, takes a different path, or the code differs; the AI fixes the test or the code, and when it cannot tell which is right it walks that step by hand again. When every pair matches, or the person accepts the explained differences, this run is the first regression baseline.

### Regression: every later e2e run

Every later e2e run, during ticket work, by hand, or scheduled, compares each step with the last accepted e2e run. A run is not finished until its screens have been reviewed.

1. **Filter by pixels first.** Only pairs that changed go to the AI. A cheap block diff (pml-web's 8px block check) keeps the AI from reading hundreds of identical screens.
2. **The AI judges each changed pair** using both screenshots, the step's Given/When/Then text, and the stories and code changed since the baseline (this ticket's changes, or for a scheduled run the commits on main since then). The verdict is one of:
   - **intended:** the change follows from one of those story or code changes, and the AI cites which one.
   - **regression caught:** a test already fails for it, so fix the code.
   - **missed by the tests:** the screen is wrong and nothing failed.
   - **noise:** timing, animation, or a value the system mints. The AI makes the harness deterministic instead of accepting the noise.
3. **For each "missed by the tests":** add the test at the layer that owns the behaviour (story markdown and the domain story test for a rule or value, the screen story for a control or label, CSS only for pure look). See it fail, fix the code, and rerun.
4. **Repeat** until every changed pair is "intended". The person reviews the report, and accepting it makes this run the new baseline.

## Report

One report shape for all three comparisons, one page per sub-epic plus a story map page over them all, laid out like pml-web's `compare.html`:

- Story › Scenario › each Given/When/Then step, with its two screens side by side.
- The test result and the AI's verdict on each step, with its reason, and a filter that shows only changed or missed steps.
- The pass, changed, and missed counts for each story and sub-epic.
- A history of earlier runs, without images.

## Guidance

Added to the TDD supplement (its Flow A, cadence and e2e sections), not a new practice, unless the rules grow too many for it. Rules:

- `every-step-captured`: every e2e step, walked by hand or run by a test, records a screenshot and result under its story › scenario › step key.
- `walk-checks-the-intent`: each step of a manual walk is judged against its Given/When/Then, and the walk is the reference only when every step meets it and the person accepts it.
- `e2e-matches-the-walk`: a new e2e test's screens are compared with the accepted walk, and a difference is fixed or walked again, never accepted unexplained.
- `every-run-reviewed`: every e2e run, by ticket, by hand or scheduled, is compared with its baseline before its result counts.
- `ai-judges-every-changed-pair`: every changed pair gets a verdict and a reason, and "intended" cites the story or code change behind it.
- `missed-change-adds-a-test-first`: a change the tests missed gets a failing test at the owning layer before the code is fixed.
- `noise-is-fixed-in-the-harness`: a pair is never accepted as timing noise.
- `person-accepts-the-baseline`: only the person's acceptance makes a walk the reference or a run the baseline.

The tier table and the cadence table in `tdd.md` each get a line: e2e runs record step screenshots and are reviewed against the run before.

## Code

**CDD owns the general parts**, shipped for TypeScript Playwright story tests (CDD's own `*.story.ui.spec.ts` first, then pml-web's `*.story.playwright.ts`):

- A walk recorder: when the AI drives the app by hand, each step's screenshot and verdict are written under the same key and folder layout the e2e tests use.
- A step capture hook for e2e tests: after each Given/When/Then, wait until the page settles, take the screenshot, and write a row to that run's `results.json` (key, step text, result, screenshot path, walked or automated).
- Run folders: `.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>/`, and choosing what to compare with: the accepted walk, or the last accepted e2e run (pml-web's `release-baseline.ts` and `end-to-end-paths.ts` already do the latter). Screenshots are git-ignored, and accepted baselines are kept on a branch, as pml-web does with `e2e-latest`.
- The pixel prefilter, which lists the changed pairs between two runs.
- The report writer, adapted from pml-web's `report.ts`.
- A Python toolset with MCP tools `walk(target)`, `run(target)`, `changed_pairs(target, against)`, `record_verdict(step, verdict, reason)` and `accept(target)`. Long runs go to the background through `harness/process`. The AI reads the image pairs itself and writes its verdicts back through `record_verdict`.
- The daily e2e run in `test_runs.py` captures screenshots too. When it ends, the cdd server starts the regression review in a background agent session and raises a toast for any step judged "missed by the tests". The fix happens in a ticket, because a scheduled run on main has no ticket to change.
- A line in the server health report: the latest run, its changed and missed counts, and a link to the story map page.

**Each project keeps** starting its app, loading its examples, and its Playwright config.

## Order of work (Flow A: a new boundary)

1. Add the step capture hook to CDD's own board UI story tests, run them, and check with the person that every step has its screenshot under the right key.
2. Add the baseline choice, the pixel prefilter, the report, and the regression review. Rerun with one deliberate visual change, and check that only that pair shows up and gets the right verdict.
3. Add the walk recorder, walk one sub-epic by hand, and compare it with that sub-epic's e2e run.
4. Write the TDD additions and rules.
5. Add the toolset, verdict recording, acceptance, and the health line.
6. Point pml-web's end-to-end runs at the same hook, recorder and report.

## Done means

- Every e2e run shows, for every story step, the previous and current screens side by side, with a verdict on each changed one.
- A visual change no test caught ends up as a new failing test, a fix, and a rerun, not as an accepted screenshot.
- A Flow A walk ends in a screen report the person accepts, and the e2e test that captures it is compared with that walk.
- The baseline moves only when the person accepts a run.

## Open questions

- Baseline: the last run on main, or the last run the person accepted, whichever branch it was on?
- Should the AI also look at unchanged pairs now and then, to catch a screen that has been wrong since before the baseline?
- Should the report be published as an artifact for sharing, or only opened from the run folder?
- Do the walk and walk-versus-e2e comparisons belong in this ticket, or should it ship regression first and add them later?
