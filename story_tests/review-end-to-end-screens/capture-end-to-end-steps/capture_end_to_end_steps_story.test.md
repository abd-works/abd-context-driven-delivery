---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Capture End-To-End Steps

Story map: [Capture End-To-End Steps](../../../.context/story-map.md#e-capture-end-to-end-steps). Session ui-fixes-as-i-use-it.

**Evidence mode.** The scenario here is *Observed*: it holds for the e2e review today (`harness/e2e_review/e2e_review.py`, *ReportTool*) and is tested by `harness/e2e_review/e2e_review_heavy_spec.py`. Found by the hardening regression run of 2026-11-26 (`.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/bolt-5-e2e-review-refused-on-pinned-runtime.md`). No story test file runs it: the heavy spec drives the report tool directly.

### Domain terms

- ++report tool++ — `harness/e2e_review/report/`, the TypeScript that compares a run's screens with the accepted run and keeps its summary, run with tsx (*ReportTool*).
- ++pinned runtime++ — the copy of a checkout the cdd server serves from (`~/.cdd/runtime`, or `~/.cdd/dev/runtime` for the dev lane), which holds the checkout's files and no `node_modules`, since git keeps none.

## Story: Compare An E2E Run With The Accepted Walk

#### Scenario: Compare a run from a runtime whose report tool holds no packages

> Test: heavy: harness/e2e_review/e2e_review_heavy_spec.py 'the e2e review's report tool' › 'in a folder that holds no packages' ('should answer the run's summary', 'should leave its packages installed for the next command'); › 'with a command that fails' ('should be refused with the line that names the error, not Node's version').

*Given* the cdd server serves from a ++pinned runtime++ whose ++report tool++ holds no packages
*When* the agent lists the changed pairs of a sub-epic's run with `e2e-review.changed_pairs`
*Then* the ++report tool++ installs its packages from its package-lock and answers the run's changed pairs
  *And* the next command finds the packages installed and installs nothing
  *And* a command that fails is refused with the line of Node's output that names the error, never only Node's version
