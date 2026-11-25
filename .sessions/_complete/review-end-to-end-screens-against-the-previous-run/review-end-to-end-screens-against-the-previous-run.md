# Review End-To-End Screens Against The Previous Run

Add guidance and code so every end-to-end run records a screenshot for each story test step, and the AI compares it with the same step's screenshot from the previous run. This is **visual regression testing**: the run checks that what the screens show has not changed without a reason. The baseline is the last good run of the same system, not another system.

The end-to-end tests are expected to pass. Passing only proves the assertions someone wrote, and a screen can break in ways no assertion checks: a field missing, a label changed, a layout collapsed, a notice no longer shown. A person sees that at once in the screenshot, so the AI looks at the screenshots too. When the AI sees a change the tests did not catch, it adds the assertion that would have caught it, reruns the tests, and fixes the code until that assertion passes.

This review happens on **every** end-to-end run, not just some: a run during ticket work, a run someone starts by hand, and the daily e2e run the cdd server schedules (`harness/diagnostics/test_runs.py`). An end-to-end run is not finished until its screens have been reviewed.

## The loop

1. **Run the end-to-end tests** for the area changed (a sub-epic, an epic, or all). Each step of each scenario records a screenshot and its result, keyed by story › scenario › step.
2. **Find the baseline:** the same step's screenshot from the previous good run (the last run on main, or the previous release). **On the first run there is no baseline**, so the AI checks every step's screenshot against the scenario itself: does the screen actually do what the scenario means? It reads the Given/When/Then text and asks whether a person looking at this screen would agree the step happened (the Given's state is visible, the When's action took effect, the Then's outcome is shown, with the right values, labels and messages). Each step gets a verdict: **meets the intent**, or **misses the intent** with what is wrong, handled like "missed by the tests" in step 5. A step's screenshot becomes part of the first baseline only when it meets the intent and the person accepts the run. A step added to a scenario later gets the same check on its first run.
3. **Filter the pairs by pixels first.** Only pairs that changed go to the AI. A cheap block diff (pml-web's 8px block check) keeps the AI from reading hundreds of identical screens.
4. **The AI judges each changed pair** using both screenshots, the step's Given/When/Then text, and the stories and code changed since the baseline (this ticket's changes, or for a scheduled run the commits on main since then). The verdict is one of:
   - **intended:** the change follows from one of those story or code changes, and the AI cites which one.
   - **regression caught:** a test already fails for it, so fix the code.
   - **missed by the tests:** the screen is wrong and nothing failed.
   - **noise:** timing, animation, or a value the system mints. The AI makes the harness deterministic instead of accepting the noise.
5. **For each "missed by the tests":** add the test at the layer that owns the behaviour (story markdown and the domain story test for a rule or value, the screen story for a control or label, CSS only for pure look). See it fail, fix the code, and rerun.
6. **Repeat** until every changed pair is "intended". Then the person reviews the report, and accepting it makes this run the new baseline.

## Report

One page per sub-epic, plus a story map page over them all. It is laid out like pml-web's `compare.html`, but compares previous with current:

- Story › Scenario › each Given/When/Then step, with its previous and current screenshots side by side.
- The test result and the AI's verdict on each step, with the AI's reason, and a filter that shows only changed or missed steps.
- The pass, changed, and missed counts for each story and sub-epic.
- A history of earlier runs, without images.

## Guidance

A supplement to Stories acceptance tests and the TDD end-to-end tier, for example `cdd_guidance/practices/visual_review/visual_review.md` (name to decide). It holds the loop above as its process, plus these rules:

- `every-run-reviewed`: every end-to-end run, by ticket, by hand or scheduled, is reviewed against its baseline before its result counts.
- `every-step-captured`: every story test step in the end-to-end tier records a screenshot and result under its story › scenario › step key.
- `first-run-checks-the-intent`: a step with no baseline is judged against its scenario's intent from the screenshot alone, and it joins the baseline only when it meets that intent.
- `baseline-is-previous-good-run`: compare with the last accepted run of the same system.
- `ai-judges-every-changed-pair`: every changed pair gets a verdict and a reason, and "intended" cites the story or code change behind it.
- `missed-change-adds-a-test-first`: a change the tests missed gets a failing test at the owning layer before the code is fixed.
- `noise-is-fixed-in-the-harness`: a pair is never accepted as timing noise.
- `person-accepts-the-baseline`: only the person's acceptance moves the baseline.

The TDD tier table in `tdd.md` gets one line: end-to-end runs record step screenshots and are reviewed against the previous run.

## Code

**CDD owns the general parts**, shipped for TypeScript Playwright story tests (CDD's own `*.story.ui.spec.ts` first, then pml-web's `*.story.playwright.ts`):

- A step capture hook: after each Given/When/Then, wait until the page settles, then take the screenshot and write a row to that run's `results.json` (key, step text, result, screenshot path).
- Run folders: `.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/`, and picking the baseline run (pml-web's `release-baseline.ts` and `end-to-end-paths.ts` already do this). Screenshots are git-ignored, and accepted baselines are kept on a branch, as pml-web does with `e2e-latest`.
- The pixel prefilter, which lists the changed pairs.
- The report writer, adapted from pml-web's `report.ts` (story tree, side-by-side screenshots, filters, history).
- A Python toolset with MCP tools `run(target)`, `changed_pairs(target)`, `record_verdict(step, verdict, reason)` and `accept_baseline(target)`. Long runs go to the background through `harness/process`. The AI reads the image pairs itself and writes its verdicts back through `record_verdict`.
- The scheduled daily e2e run in `test_runs.py` captures screenshots too. When it ends, the cdd server starts the review in a background agent session and raises a toast for any step judged "missed by the tests". The fix happens in a ticket, because a scheduled run on main has no ticket to change.
- A line in the server health report: the latest run, its changed and missed counts, and a link to the story map page.

**Each project keeps** starting its app, loading its examples, and its Playwright config.

## Order of work (Flow A: a new boundary)

1. Add the step capture hook to CDD's own board UI story tests, run them, and check with the person that every step has its screenshot under the right key.
2. Add the baseline choice, the pixel prefilter, and the report. Rerun with one deliberate visual change, and check that only that pair shows up.
3. Write the guidance and rules, and run the AI judging loop on that change.
4. Add the toolset, verdict recording, baseline acceptance, and the health line.
5. Point pml-web's end-to-end runs at the same hook and report.

## Done means

- An end-to-end run shows, for every story step, the previous and current screens side by side with a verdict on each changed one.
- A visual change no test caught ends up as a new failing test, a fix, and a rerun, not as an accepted screenshot.
- The baseline moves only when the person accepts the run.

## Open questions

- Baseline: the last run on main, or the last run the person accepted, whichever branch it was on?
- Should the AI also look at unchanged pairs now and then, to catch a screen that has been wrong since before the baseline?
- Should the report be published as an artifact for sharing, or only opened from the run folder?

## Done 2026-11-24

Built on the e2e-testing ticket (`.sessions/_complete/e2e-testing/`), in commits 9f70a51ff, 946fff3ee and a191cd072, as steps 1 to 5 of its order of work: the walk report, the step capture hook, the compare report, the baseline, the pixel check, the regression review, the TDD and Stories rules, the `e2e-review` toolset, the daily run's review, and the server health line. The story map's Review End-To-End Screens epic names the code behind each story.

- Not built: the run history. `writeHistoryReport` in `harness/e2e_review/report/report.ts` writes the page without images and the `summary.md` section, but no run calls it; the story *Read Earlier E2E Runs* stays Intended.
- Dropped by the person on 2026-11-24: step 6, pointing pml-web's end-to-end runs at the same recorder.
- Built otherwise than written here: the accepted baseline is named in each sub-epic folder's `baseline.json`, not kept on a branch; the supplement's rules went into `cdd_guidance/practices/tdd/tdd.md` rather than a practice of their own.
