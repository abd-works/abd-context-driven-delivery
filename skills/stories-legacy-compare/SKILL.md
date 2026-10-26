---
name: stories-legacy-compare
description: >-
  Compares pml-web with legacy pml-my story by story, so pml-web looks and behaves exactly like pml-my on the public
  surface. Copies a sub-epic's shared stories into a `*.story.legacy-compare.ts` tier, runs every step on pml-my (backend
  stubbed at its own edge) and then on pml-web (lowdb), and compares what each screen shows and what each step writes.
  Use when a sub-epic's stories are built and need checking against pml-my, or when the user asks to compare with
  legacy, check against pml-my, or run the legacy-compare tier.
---

# Stories legacy compare

pml-my is the reference.
- A step that fails on pml-my means the story is wrong: fix the story and its shared twin.
- A step that passes on pml-my and fails on pml-web means pml-web is wrong: fix pml-web.

Compare only the public surface and what each step writes. Never run or change the mid-tier, the back office, or pml-my's code.

Write this tier the way `practices-stories-stories-acceptance-tests` and `patterns-lern-domain-driven` say to write any test tier.

## Terms

- **pml-my**: the legacy app, `C:/Users/jeffa/OneDrive - abd.works/personal/paradise-mobile/pml-my`. It runs under the sandbox Vite overlay `pml-domainmodel/app-sandbox/my/vite.config.stub.ts`. Its backend calls are answered by the overlay's `tests/stubs/midtier/midtier.proxy.ts`, with `VITE_MIDTIER_URL` set to pml-my's own origin.
- **pml-web**: the new app (`tests/my-paradise.ts` starts it), saving to lowdb.
- **system**: the binding the host sets to `pml-my` or `pml-web` for a run. Step bodies read it; they never branch on it.
- **screen reader**: a function that returns what one screen tells the customer, as plain values.
- **write mapping**: the expected write for one step, from the pml-my request to the pml-web lowdb record.

## Files

The tier sits beside the existing tiers. There is no new folder.

```
playwright.legacy-compare.config.ts        testMatch **/*.story.legacy-compare.ts; projects pml-my, then pml-web (no dependency, so pml-web runs even when pml-my fails); outputDir legacy-compare-results
tests/story-legacy-compare.ts              host: binds system and one live page per system; records readings, writes, ARIA, screenshots; writes the assert log
tests/pml-my.ts                            starts pml-my under the overlay; loads examples into its edge stub through the overlay's sandbox-only seed hook
tests/legacy-compare-setup.ts              keeps pml-web's committed lowdb stores out of the run; writes the assert log after it
tests/<epic>/<sub-epic>/<snake>.story.legacy-compare.ts   copied stories, step bodies, screen readers
tests/<epic>/<sub-epic>/examples/          existing examples (loaded into both systems) plus the write mappings
```

## Workflow

Before each sub-epic, read `.sessions/legacy-compare/watch-list.md`: the mistakes already made and corrected. Check the work against it before each run and before reporting. Add every new correction to it.

Copy this checklist and tick it off for each sub-epic:

```
- [ ] 1 Render the shell, every label verbatim
- [ ] 2 Write the step bodies once, for both systems
- [ ] 3 Write a screen reader per screen
- [ ] 4 Write a write mapping per step that writes
- [ ] 5 Validate until it passes
- [ ] 6 Announce the run and wait for yes
- [ ] 7 Run pml-my, then pml-web
- [ ] 8 Open the trace viewer for the user
- [ ] 9 Report, publish the log, fix, rerun
```

1. **Render.**
   - Run `actions-render` (format `typescript`) on the sub-epic's `*.story.shared.ts` and `*_story.test.md`. The output is `<snake>.story.legacy-compare.ts`.
   - Copy every story, scenario (outline rows included), and Given/When/Then label verbatim. Import nothing from the shared story.
   - When rendering shows front-end behaviour the stories miss, add that scenario to the shared story and its markdown too.
2. **Step bodies.** Write each body once, using only what a customer sees: roles, labels, copy, URL path. Per-system code (start, reset, load examples) lives only in `tests/pml-my.ts` and `tests/my-paradise.ts`.
3. **Screen readers.**
   - Write one reader per screen the stories reach, in the sub-epic's legacy-compare file.
   - Use roles and labels so one reader fits both systems. Add a pml-my variant only where its markup differs.
   - Example output from a port screen: `{ portNumber: '4415550123', provider: 'One', accountType: 'Individual', userType: 'Owner' }`.
4. **Write mappings.**
   - For every step that writes, add the expected write to the sub-epic's `examples/`.
   - Example: pml-my `POST /mv/customer { email }` maps to a new pml-web `customer-profile.json` record with `account_email` equal to that email.
5. **Validate.**
   - Run the graph rules and `actions-validate` on the legacy-compare file, fix every violation, and repeat. The story graph does not load `*.story.legacy-compare.ts`, so the AI validate pass against the acceptance-test rules carries this tier.
   - Continue only when validation passes. Add no graph rules for this tier.
6. **Announce.**
   - Tell the user the sub-epic, its stories and scenarios, both systems, the examples loaded, and whether the run is watched or fast.
   - Run nothing until the user says yes.
7. **Run.**
   - Watched (the config's default: headed, `slowMo`): `npx playwright test -c playwright.legacy-compare.config.ts`.
   - pml-my's recordings are saved per journey in `legacy-compare-results/baseline/pml-my/`. pml-my runs only journeys with no saved recording; each pml-my journey with no failing row is saved on its own, and setup copies the saved ones into every run. Set `LEGACY_COMPARE_REFRESH=1` (narrowed to a sub-epic with a file filter) to rerun saved journeys, and only when pml-my, its stubs, or the examples change. Never rerun pml-my for a harness change.
   - Keep the config's reporters (do not pass `--reporter`): they write the HTML report the trace step opens.
   - Fast: the same command with `LEGACY_COMPARE_FAST=1` set.
   - Load the examples once at the start, then never seed again. One page per system runs the stories in map order (`test.describe.serial`), and each scenario starts where the last one left the app.
   - Alternate flows run inside the journey. A flow gets its own short journey, with its own example load, only when it would leave the app stuck.
8. **Open the trace.** Every journey records a Playwright trace (`trace: 'on'`). After the run, open the trace viewer on the journeys so the user can replay each one: a tree of journey › story › scenario › step marked green or red, with the page as it was at every step.
   - One journey: `npx playwright show-trace legacy-compare-results/<run-id>/playwright/<journey-folder>/trace.zip` (one trace per viewer; open the pml-my and pml-web folders of a journey as two viewers).
   - The whole run, with every journey's trace one click away: `npx playwright show-report legacy-compare-results/<run-id>/report`.
   - Start it in the background so the session is not blocked, and tell the user which journeys failed so they know where to look.
9. **Report.**
   - For each scenario and step, give: pml-my pass/fail, pml-web pass/fail, reading match, write match, structure match.
   - Say which side to fix for each failure. Publish the assert log, fix, then go back to step 6 for the rerun.
   - **Every miss is a missing test on another layer.** Before fixing pml-web code for a failure, add the test that should have caught it, at the layer that owns the behaviour, then fix the code until that test and the compare both pass:
     - Domain behaviour (rules, refusals, messages, stored values): the story markdown, then the shared story (run by the domain and server specs).
     - HTTP-only results (status, cookies, redirects): the server spec.
     - Screen-only interaction or display (a control, a label, a carried notice): a scenario in the sub-epic's existing Playwright screen story.
     - Pure look (fonts, sizes, spacing): CSS only; the legacy-compare look and style checks are its spec.
     - One miss can need more than one layer: when a screen shows data or a rule the domain owns, add the shared story test for the behaviour and the Playwright scenario for the screen.
     - When pml-my contradicts a story, the story is wrong: change the markdown and every tier with it, and record the evidence ("observed: pml-my …").
   - To watch a single system live instead of replaying it, Playwright's UI mode works on this tier as is: `npx playwright test -c playwright.legacy-compare.config.ts --ui`.

## Run modes

- **Watched (default).** Headed, with `slowMo`. A banner on the page shows the system (**LEGACY · pml-my** or **NEW · pml-web**, in different colours) and the step as it runs, and the tab title starts with the system. Use it for the first runs of every epic.
- **Fast,** only when the user says so (for example "go at your own speed"). Headless and unpaced; report when the run ends. Stay fast until the user asks to watch again, and switch back to watched for each new epic's first runs.

## What every Then checks, on both systems

1. **Same information (the gate).** The screen reader's values must be equivalent.
   - Values from the examples must be equal after normalising case, spacing, and phone and currency formats.
   - Values each system mints (ids, temporary numbers, dates) must be present and well-formed.
2. **Same writes.**
   - Record pml-my's requests to its edge stub during the step (Playwright request capture).
   - Diff pml-web's lowdb JSON stores before and after the step, and record its `/api/…` requests.
   - Apply the write mapping: the mapped values must be equal. A write on one side with nothing on the other fails the step.
3. **Structure (information).** Record the ARIA snapshot of the page and log any difference from pml-my as an `info` row. It does not fail the step: the bar is that pml-web looks and behaves like pml-my, and pml-web keeps its own semantics (headings, banner, lists, alt text) where pml-my's MUI markup has none.
4. **Same fonts, colours, and sizes.** On every outcome step, record each visible text and control: font family, font size, weight, colour, letter spacing, line height, background, corners, and its box (left, top, width, height). For each text both systems show, every property must match pml-my. Font size may differ by 0.5px, box sizes by 2px, and places by 4px. Report each difference as `text: property pml-my → pml-web`.
5. **Same look.** Cut both screenshots into 8px blocks. A block has changed when its average grey moves more than 6 levels. More than 1% of blocks changed fails the step: the same pml-my screen changes at most 0.2% between runs. Report the changed page bands and write a diff image with the changed blocks tinted red. Hide the watched-run banner while taking screenshots.
6. **Same page text.** Every outcome step also diffs the page's visible text. Ignore zero-width spaces and normalise minted phone numbers.

## Assert log

Write `legacy-compare-results/<run-id>/assert-log.md` with exactly these columns, one row per assertion:

```
| story › scenario › step | system | checked (reader field, mapping, or locator + expected) | seen | result | screenshots |
```

Publish the log as a page and give the user its link. Background and decisions are in `.sessions/legacy-compare/approach.md`.
