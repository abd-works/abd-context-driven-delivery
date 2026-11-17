# Integrate End-To-End Compare Runs And Reports Into CDD

Generalise pml-web's legacy-compare tier (`C:/dev/paradise-mobile/pml-web/test-utils/legacy-compare`, `scripts/end-to-end.mjs`, `playwright.legacy-compare.config.ts`) into CDD guidance and code, so any project can run its stories end to end against a reference and get the same per-sub-epic report. Today the strategy lives only in `skills/stories-legacy-compare/SKILL.md` and `agents/new-feature.md`. The installer does not publish either one, and nothing under `cdd_guidance/` mentions `e2e-test-results`, `compare.html` or `end-to-end.mjs`.

## What exists

- **Guidance:** `skills/stories-legacy-compare/SKILL.md`, a 9-step checklist (render, step bodies, screen readers, write mappings, validate, announce, run, open the trace, report). It also defines six checks every Then makes, the assert log columns, and the watched and fast run modes. All of it is written for pml-my and pml-web.
- **Code, all in pml-web, about 2,750 lines of TypeScript:** `story-legacy-compare.ts` is the step recorder for each system (readings, writes, ARIA, screenshots, assert log). `report.ts` writes `compare.html`, `story-map.html` and the history with `summary.md`. `release-baseline.ts` picks the release to compare against, `end-to-end-paths.ts` holds the result paths, `setup.ts` backs up and restores the stores, and `pml-my.ts` starts the reference app. `scripts/end-to-end.mjs` runs one sub-epic at a time and restarts a stalled run.
- **CDD:** `harness/diagnostics/test_runs.py` starts CDD's own e2e tier daily on main and shows its pass or fail in server health. It has no per-story results. The TDD supplement says only that e2e runs go to the background.
- **Related:** `.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md` wants these same results (`.sessions/<release>/e2e-test-results`) shown on the explorer tree.

## Strategy

### 1. Guidance: a Stories supplement, "end-to-end compare"

Put it in `cdd_guidance/practices/e2e_compare/e2e_compare.md` (name to decide), a `PracticeSupplement` like TDD with `supplements: { stories: acceptance_tests }`. Pick it per ticket as an overlay, not `always_apply`, because only some projects have a reference to compare against.

- **Guidance section:** the 9-step process, with pml-my and pml-web replaced by the terms **reference system** and **system under test**. Keep the rule that a step failing on the reference means the story is wrong, and a step failing only on the system under test means the code is wrong.
- **Rules:** one per check, each with a failing and a repaired example in `rules/rule_examples.py`:
  - `step-bodies-system-blind`: a step body never branches on the system.
  - `then-reads-through-screen-reader`: a Then reads a screen through a screen reader.
  - `writing-step-has-write-mapping`: every step that writes has a write mapping.
  - `serial-journey-seeds-once`: a journey loads its examples once and runs in map order.
  - `harness-owns-timing`: timing is never accepted as noise.
  - `every-miss-adds-a-lower-tier-test`: each miss first gets a test at the layer that owns the behaviour.
  - Validate judges these at first. Add graph rules only after the story graph can load the compare tier (it does not load `*.story.legacy-compare.ts` today).
- **TDD supplement:** add the compare tier to the tier table in `tdd.md`: e2e tier, run in the background, results kept per release.
- **Stories acceptance tests:** add one line that, when the overlay is selected, points to the supplement and names the `*.story.compare.ts` file kind.
- **Templates:** the compare file, a screen reader, a write mapping, and `approach.md` and `watch-list.md` starters.
- `_examples/`: a small worked example: one sub-epic with two systems and one write mapping.
- **References:** move the report reading guide (check kinds, Failures-only filter, which side to fix) to `cdd_guidance/references/` so the installer publishes it.

### 2. Code: split it into what CDD owns and what the project owns

**CDD ships it as a TypeScript runtime package that the installer deploys.** Follow the language adapter precedent in `patterns/cdd_web_domain_access`, where the installer already writes TypeScript beside the skills. It goes under `<install path>/e2e-compare/` or into a published npm workspace package.

- **Generic, so it moves to CDD:**
  - `report.ts` (row model, check kinds, `compare.html`, `story-map.html`, history, `summary.md`), with branding a parameter (`catalog_apply_brand` brands)
  - `end-to-end-paths.ts`
  - `release-baseline.ts`
  - the runner loop in `end-to-end.mjs` (one sub-epic at a time, the stall watch and one retry, the lock so one session runs it per checkout)
  - the checks inside `story-legacy-compare.ts`: readings, write diff, page text, fonts, colours and sizes, the 8px block look diff, the ARIA info row, the settle waits
- **Per project, so it stays in the project, written from templates:**
  - starting the reference system and the system under test, and loading examples (`pml-my.ts`, `my-paradise.ts`)
  - the store backup used by the write diff (lowdb today; an interface `StoreSnapshot.before()` and `after()`)
  - the list of epics (read it from the story map instead of `EPICS = [...]`)
  - the Playwright config
- **Python seam:** an `E2eCompareRun` toolset in `space/` with `run(target, mode)`, `report(target)` and `open_trace(target)` as MCP tools. They start the runner in the background through `harness/process` and record each sub-epic's result in the session.
- **Server health:** extend `test_runs.py` so a project's e2e compare run is listed beside heavy and e2e, with pass and fail counts per sub-epic and a link to `story-map.html`. A sub-epic that fails after passing raises the toast that exists today.
- **Results format:** make each sub-epic's rows a stable `results.json` (key, system, check kind, checked, seen, result, screenshot). The reports, the health report and the canvas explorer increment all read that file, so they never parse HTML.

### 3. Order of work (Flow A, a new boundary)

1. Move `report.ts` and its spec into CDD unchanged, have pml-web import it from the deployed package, and run pml-web's e2e for one sub-epic. Check that the person sees the same `compare.html`.
2. Write the supplement markdown and the rules from `SKILL.md`, install it, and delete `skills/stories-legacy-compare/` and the duplicate wording in `agents/new-feature.md` in the same change (`no-legacy-api-after-refactor`).
3. Move the runner and the checks, behind the store snapshot interface and the system-start interface. Re-run pml-web, a heavy spec in pml-web.
4. Add the `results.json` contract, the toolset, and the server health line.
5. Add a second, small project as the example, to prove nothing pml-specific remains.

## Done means

- Selecting the overlay on a ticket gives the agent the compare process and rules through the installed guidance, with no root `skills/` folder.
- pml-web runs `npm run e2e` on the CDD-deployed runner and report, keeps only its adapters, and its `compare.html` looks the same as before.
- The server health report lists the latest compare result for each sub-epic.

## Open questions

- Name: "end-to-end compare", "reference compare" or "legacy compare"?
- Should a project with no reference system use the same report as a plain story run report, with only the system under test, so every project gets per-step screenshots?
- Package delivery: deployed by the installer under the install path, or a versioned npm package?
