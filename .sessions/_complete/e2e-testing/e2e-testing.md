# e2e-testing

Taken from the backlog item `.sessions/_backlog/review-end-to-end-screens-against-the-previous-run.md`, and fitted to the end-to-end phases the TDD supplement already has (`cdd_guidance/practices/tdd/tdd.md`).

## What already exists

TDD already sets the end-to-end phases:

- **Flow A, steps 1–2:** run a new boundary end to end directly, iterate until it works, and a person verifies it.
- **Flow A, step 3 / Flow B, step 4:** capture that path in an e2e or heavy test and see it pass against the real stack.
- **Cadence:** e2e runs every day, before every release, and at the end of work that touches a browser or an agent (`e2e-run-within-the-day`, `release-follows-a-green-e2e`; the daily run is `harness/diagnostics/test_runs.py`).

This ticket does not change those phases. It adds what they lack: **a screenshot for every scenario step, a report of them, and an AI review of the screens**, so each phase is checked against the one before. The main gap is regression: an e2e run only proves the assertions someone wrote, and a screen can break in ways no assertion checks (a field missing, a label changed, a layout collapsed, a notice no longer shown).

## The steps

New text is in **bold**; the rest is TDD as it stands.

### Flow A: a new boundary

1. **Run it end to end, directly.** Drive it through the real stack yourself, or ask the person to. Record every failure as it happens. **Screenshot each Given, When and Then as you go, keyed story › scenario › step.**
2. **Iterate until it works for real.** **Judge each step's screenshot against its step text: the Given's state is visible, the When took effect, the Then shows the right values, labels and messages. Fix and walk again until every step meets it. Write the walk report (below).** A person verifies the result **by reviewing that report; accepting it makes this walk the reference.**
3. **Capture it in an e2e or heavy test** and see it pass against the real stack. **The e2e test records the same step screenshots; compare each with the accepted walk. Where they differ, fix the test or the code; when it is unclear which is right, walk that step again. When they all match, this run is the first baseline.**
4. **Then write the stubbed and mocked unit tests** (unchanged).

### Flow B: a known area

Steps 1–3 unchanged. Step 4 (heavy and e2e tests in a sub-task) **ends with a screen review of that e2e run against the baseline** (below).

### Reviewing e2e screens: every e2e run (new; the regression part)

1. **Run the e2e tests.** Each step records its screenshot and result.
2. **Compare each step with the last accepted run, by pixels** (pml-web's 8px block check). Only changed pairs go on.
3. **Give each changed pair a verdict and a reason:**
   - **intended:** cites the story or code change behind it (this ticket's changes, or for a scheduled run the commits on main since the baseline).
   - **regression caught:** a test already fails, so fix the code.
   - **missed by the tests:** go to step 4.
   - **noise:** timing, animation, or a minted value; make the harness deterministic and rerun.
4. **For each miss, write the failing test at the layer that owns it,** see it fail, fix the code, and rerun.
5. **Repeat until every changed pair is intended.** The person reviews the report; accepting it makes this run the new baseline.

**Cadence table, e2e row:** "Every day, before every release, and at the end of browser or agent work. **Its screens are reviewed against the last accepted run before its result counts.**"

## Where the guidance goes

TDD owns **when and in what order**; Stories acceptance tests owns **what a story test is and what a scenario means**. No new practice.

### TDD supplement (`tdd.md`)

| Addition | Where |
|---|---|
| The person verifies the walk by its screen report | Flow A step 2, and a clause in `flow-chosen-before-code` |
| The e2e test is compared screen by screen with the accepted walk | Flow A step 3 |
| Every e2e run is reviewed against the last accepted run before its result counts (`every-run-reviewed`) | The e2e row of the Cadence table, and a rule beside `e2e-run-within-the-day` |
| The verdict loop (intended, regression caught, missed by the tests, noise) | A new "Reviewing e2e screens" subsection under Cadence |
| A missed change gets a failing test before the fix (`missed-change-adds-a-test-first`) | That subsection |
| Noise is fixed in the harness, never accepted (`noise-is-fixed-in-the-harness`) | Beside `no-wait-in-unit-test` |
| Only the person moves the baseline (`person-accepts-the-baseline`) | Cadence rules, beside `release-follows-a-green-e2e` |

### Stories acceptance tests (`stories.md` § acceptance_tests)

| Addition | Where |
|---|---|
| The UI story test records a screenshot after each Given/When/Then, keyed story › scenario › step (`every-step-captured`) | A rule, plus the `story-test.ts` step helpers; the fidelity's `outputs` gains the `*.story.ui.spec.ts` line it is missing |
| How to judge a screen against its step: the Given's state visible, the When took effect, the Then shows the right values | Guidance, "Develop the behaviour" |
| Which layer gets a missed test (domain tier for a rule or value, UI tier for a control or label, CSS for pure look) | Beside `seed-state-at-its-real-owner` |

## Report

### Walk report (Flow A steps 1–2): one run, no compare

Built from pml-web's legacy report writer, `test-utils/legacy-compare/report.ts`, with the legacy compare taken out.

**Kept:** the story › scenario › step grouping and step numbering; screenshots embedded at half size (one self-contained file that opens in Claude's file pane), linked to the full-size file; scenario sections that open by themselves when a step fails; the summary table of pass and fail per story and sub-epic; the story map page over every sub-epic; the no-image history page and `summary.md`; the abd.works styling and page template.

**Dropped:** the second system (`myRows` / `webRows`, the `pml-my` and `pml-web` folders, `REFERENCE_NAME` and its chips); two screenshots per step; the check kinds (reading, write, page text, fonts, look) and their tallies; `scopeToRun` and `uniqueRows`.

**Each step shows:** its Given/When/Then text, its one screenshot, and the AI's verdict (**meets the intent** or **misses the intent**) with its reason.

Each run writes one row per step to its `results.json`: key, step text, verdict, reason, screenshot path, and whether the step was walked by hand or run by a test. That replaces pml-web's `rows-*.jsonl`.

### Compare reports (Flow A step 3, and regression)

The same page and step layout, with the second screenshot added back: filled from two runs (accepted walk vs e2e, or last accepted run vs this one) instead of two systems. Each step shows both screens side by side, the test result, and the AI's verdict and reason, with a filter for changed or missed steps and the pass, changed and missed counts per story and sub-epic.

## Code

**CDD owns the general parts**, shipped for TypeScript Playwright story tests (CDD's own `*.story.ui.spec.ts` first, then pml-web's `*.story.playwright.ts`):

- **Walk report writer:** `report.ts` reduced to one run, as above. Comes first.
- **Walk recorder:** when the AI drives the app by hand, each step's screenshot and verdict go into the run's `results.json` under the same key and folder layout the e2e tests use.
- **Step capture hook** for e2e tests: after each Given/When/Then, wait until the page settles (pml-web's `story-legacy-compare.ts` settle waits), take the screenshot, and write the step's row.
- **Run folders:** `.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>/`, and choosing what to compare with: the accepted walk, or the last accepted e2e run (pml-web's `release-baseline.ts` and `end-to-end-paths.ts` do the latter). Screenshots are git-ignored; accepted baselines are kept on a branch, as pml-web does with `e2e-latest`.
- **Pixel prefilter:** lists the changed pairs between two runs (`lookDifference` in `story-legacy-compare.ts`).
- **Compare report:** the walk report with the second screenshot added.
- **Toolset** with MCP tools `walk(target)`, `run(target)`, `changed_pairs(target, against)`, `record_verdict(step, verdict, reason)` and `accept(target)`. Long runs go to the background through `harness/process`. The AI reads the screenshots itself and writes verdicts back through `record_verdict`.
- **Daily run:** `test_runs.py` captures screenshots too; when it ends, the cdd server starts the regression review in a background agent session and raises a toast for any step judged "missed by the tests". The fix happens in a ticket.
- **Health line** in the server health report: the latest run, its changed and missed counts, and a link to the story map page.

**Each project keeps** starting its app, loading its examples, and its Playwright config.

## Order of work (Flow A: a new boundary)

1. Write the walk report from `report.ts`, minus the compare. Walk one sub-epic of CDD's own board UI by hand, screenshot every step, record verdicts, and build the report. Check it with the person.
2. Add the step capture hook to that sub-epic's e2e story tests, and the compare report; compare with the accepted walk and fix until they match.
3. Add the baseline choice, the pixel prefilter, and the regression review. Rerun with one deliberate visual change, and check that only that pair shows up and gets the right verdict.
4. Write the TDD and Stories additions.
5. Add the toolset, verdict recording, acceptance, and the health line.
6. Point pml-web's end-to-end runs at the same recorder, hook and reports.

## Done means

- A Flow A walk ends in a walk report, a screenshot and verdict for every step, that the person accepts.
- The e2e test that captures it is compared with that walk, side by side.
- Every later e2e run shows the previous and current screens side by side, with a verdict on each changed one.
- A visual change no test caught ends up as a new failing test, a fix, and a rerun, not as an accepted screenshot.
- The baseline moves only when the person accepts a run.

## Open questions

- Baseline: the last run on main, or the last run the person accepted, whichever branch it was on?
- Should the AI also look at unchanged pairs now and then, to catch a screen that has been wrong since before the baseline?
- Should reports be published as an artifact for sharing, or only opened from the run folder?
- Does the walk report writer live in CDD from the start, or first in pml-web beside `report.ts` and then move?
