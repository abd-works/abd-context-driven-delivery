# Every e2e-review tool is refused on a pinned runtime, and the refusal says only Node's version

- **Charter:** supervisor, found by the regression run (comparing the e2e tier's screens), after exploratory testing closed.
- **Tester:** Bolt (regression run resumed in chat d0e9c5f2).
- **Story:** Review End-To-End Screens > Capture End-To-End Steps > Compare An E2E Run With The Accepted Walk. No scenario covered running the review from a pinned runtime.
- **Module and class:** `harness/e2e_review/e2e_review.py`, `ReportTool.run`: it ran `npx tsx review.ts` in `harness/e2e_review/report/`, which a runtime pinned from a checkout holds without `node_modules` (git keeps none, and the report tool is no app that `app.install` installs); its refusal kept the last line Node printed.
- **Severity:** blocks work (the regression run's screen review cannot run on the dev lane; `e2e-review.changed_pairs`, `record_verdict`, `judge_step` and `accept` are all refused).
- **Steps:**
  1. Pin the dev lane from this worktree (`python scripts/install.py --ide Claude --pin-runtime`).
  2. Call `e2e-review.changed_pairs` with a run folder the e2e tier wrote, such as `.sessions/local/e2e-test-results/move-work-forward-on-session-board/maintain-tickets/2026-11-27-03-09-12`.
- **Expected:** the run's changed pairs; or, if the tool cannot run, a refusal that says why.
- **Actual:** `E2eReviewRefused: Node.js v24.19.0`. Node had failed with `ERR_MODULE_NOT_FOUND: Cannot find package 'tsx'`; `~/.cdd/dev/runtime/harness/e2e_review/report/` (and `cdd_guidance/practices/stories/app/`) hold no `node_modules`.
- **Tier that should catch it:** heavy, a spec that runs the report tool for real from a folder with no packages.

## Triage

- **Status:** confirmed. Reproduced by running `node --import tsx review.ts summary <run>` in the dev runtime's report folder.
- **Severity:** blocks work.
- **Triaged by:** Bolt; reporter and fixer are the same robot here, since the regression run found it after the testers had closed.

## Fix

- **Flow A:** run for real first: `ReportTool` on a copy of the report folder with no `node_modules` installed its packages and answered the maintain-tickets run's summary (72 steps); then captured in the heavy spec below.
- **Scenario:** Compare a run from a runtime whose report tool holds no packages (`story_tests/review-end-to-end-screens/capture-end-to-end-steps/capture_end_to_end_steps_story.test.md`).
- **Test (heavy):** `harness/e2e_review/e2e_review_heavy_spec.py`.
- **Fix:** `ReportTool` installs its packages with `npm ci` the first time it runs in a folder that holds none, refused with the folder named when npm fails, and a refusal names the line of the command's output that names its error.
- **Not changed:** `cdd_guidance/practices/stories/app/` has no packages in the runtime either; nothing in this regression run used it.
- **Commit:** see git log for this file.
