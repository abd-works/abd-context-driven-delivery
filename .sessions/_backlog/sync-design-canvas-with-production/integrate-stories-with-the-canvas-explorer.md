# Integrate Stories With The Canvas Explorer

Session `claud_design_enhancements`. Analysis and planning only: nothing here is implemented. This increment is one of the design canvas increments in the thin slice, which sets their order, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to; approaches, options and recommendations sit on the feature they decide.

| Increment | Epic → feature on the story map | Depends on | First slice |
|---|---|---|---|
| **12: Integrate Stories With The Canvas Explorer** | Build Design Canvas Screens → Check Screens Against Their Scenarios; Connect Sessions Across Channels And Apps → Change Stories From Canvas And Story UI | Phase 0 for playing UI steps; the comments check for story changes | Show existing end-to-end results on the explorer tree; comment on a story, an agent updates the story code |

The other design canvas increments: [Sync Design Canvas With Production](sync-design-canvas-with-production.md), [Draw Linked Models On The Canvas](draw-linked-models-on-the-canvas.md).

**Outcome:** a person tests a screen against its scenarios from the explorer, and changes stories from the canvas or story-ui with the map updating, both ending in the same story code.

## Epic: Build Design Canvas Screens

### Feature: Check Screens Against Their Scenarios

**Goal.** A person on the canvas presses Test and sees, per scenario, whether what they are looking at behaves as the specs say.

**Done means.** Pressing Test on a scenario shows pass or fail per step with the failing assertion's message, a detached screen is tested against the same story as production, and stale results are labelled.

#### What exists

- pml-web has 9 sub-epics, each with `.story.shared.ts`, `.story.playwright.ts`, `.story.server.spec.ts` and `.story.legacy-compare.ts`. There are no `.spec.tsx` component tests.
- The canvas already carries the stories. `canvas-fixtures.ts` installs a story host that **records Givens only**: `it()` records and discards the body, and `build-canvas-fixtures.mjs` replaces vitest's `expect` with a no-op. Thens never run on the canvas today.
- `check_screen.cjs` (pml-web session tools) runs a screen's logic on each scenario in Node. It is useful but lives outside CDD.
- End-to-end output exists at `.sessions/<release>/e2e-test-results` (94 JSON, 13 JSONL, plus an HTML story map).
- `scripts/end-to-end.mjs` takes around 20 to 30 minutes per sub-epic, by its own comments, so it cannot sit behind a button.
- Shared Whens mostly act on domain objects: `when('the Customer opens My Paradise', () => { catalog = repositories.plans.list(); })`. Only the Playwright tier drives UI. That file mixes UI steps with node repositories, so it does not run in a browser as it stands.

#### The key insight

What needs testing depends on the screen's state from Sync Design Canvas With Production:

- **Attached** screens run the same code Playwright already tested. Re-testing proves little; the useful question is "does this bundle's hash match a passing run?"
- **Detached** screens are the real risk, because their behaviour differs from production by design.

#### Options

| Slice | What it proves | Where it runs | Effort | Stories |
|---|---|---|---|---|
| **A. Results overlay** | Latest pass or fail per scenario, tied to bundle hash | Published with the canvas, no run needed | Small | Package End-To-End Results With The Canvas; Mark Each Explorer Scenario Passed Or Failed; Label Stale Test Results |
| **B. Run Thens in the canvas** | The packaged domain and fixtures still satisfy the specs | Browser, on press | Small to medium | Run A Scenario's Thens On The Canvas |
| **C. Play the UI steps** | A screen, including a detached one, responds as the story says | Browser, on press | Large | Play A Story's UI Steps On A Screen |
| **D. Local runner** | Full Playwright against a canvas | Local command, results published back | Medium | Check Screen Logic Against Scenarios From A Command |

**Recommendation: A, then B, then C.** Add D only if C proves too limited.

#### Limits

A canvas cannot start local processes, so the button can only run what is in the page. Page state does not persist, so results vanish on reload unless written to the `db` capability, whose rule on this canvas is `write: admin`. Whether a viewer's page can write there is unverified.

**Open question.** The story map moves the story explorer into the Story UI app (epic Explore Stories In Story UI). The Test button is planned on the canvas explorer; if the explorer moves first, the button moves with it.

#### Story: Package End-To-End Results With The Canvas

Slice A.
- Read the end-to-end JSON at package time into a `results.json`, tied to the bundle hash of the run.

#### Story: Mark Each Explorer Scenario Passed Or Failed

Slice A.
- Show a pass mark, a fail mark or "no result" on each explorer scenario.

#### Story: Label Stale Test Results

Slice A.
- A result is stale if the bundle hash differs from the run's, and is labelled so.

#### Story: Run A Scenario's Thens On The Canvas

Slice B.
- Add a second story host that runs `beforeEach` and `it` bodies rather than recording them.
- Swap the no-op `expect` for a real one in a test build. `@vitest/expect` looks suitable but is unverified in the browser.
- Add a Test button to the explorer panel, per scenario and per story.
- Show pass or fail per step with the failing assertion's message.
- Keep the no-op for the normal bundle if size matters.

#### Story: Play A Story's UI Steps On A Screen

Slice C.
- Build a small `page` facade over the DOM (`getByRole`, `getByLabel`, `click`, `fill`, `expect(locator)`), with `@testing-library/dom` underneath.
- Alias `@playwright/test` to the facade at bundle time.
- The hard part is that Playwright files seed through `*-node` repositories and `startMyParadise`. They must be split so UI steps can run alone. This may mean changing how those files are written, which needs its own decision.
- The same driver solves the open `one-scenario-list` problem of typing values into mounted views (Type Scenario Values Into A Mounted Screen, [Sync Design Canvas With Production](sync-design-canvas-with-production.md)), so build it once.
- A detached screen is tested against the same story as production.

#### Story: Check Screen Logic Against Scenarios From A Command

Slice D, only if C proves too limited.
- Promote `check_screen.cjs` into `harness/design_canvas/` as a generic command, and optionally drive a canvas with Playwright.
- A hosted canvas needs a signed-in claude.ai session, so this is awkward to automate unattended.
- Thin screens no longer carry the `text/x-dc` logic `check_screen.cjs` extracts (Generate Attached Screens Without Markup, [Sync Design Canvas With Production](sync-design-canvas-with-production.md)), so the command must read the mounted view instead.

## Epic: Connect Sessions Across Channels And Apps

### Feature: Change Stories From Canvas And Story UI

**Goal.** Add a story, epic and so on from the canvas or from story-ui, comment on a story, and have the map update.

**Done means.** A comment on a story results in a changed story and an updated map with a reply on the thread. A story added in story-ui appears on the next map refresh. Both paths end in the same story code.

#### What exists

`C:\dev\story-ui` **is not on this machine.** I read `abd-works/story-ui` (private, last pushed 2026-08-28) through the GitHub API without cloning: the file tree, `stories-server.ts` routes, exports from `stories.ts`, an outline of `stories-client.tsx`, `session.ts`, the IA document and the latest handoff. It was not run.

| Fact | Detail |
|---|---|
| Stack | React 19, Express, MongoDB (`story_maps` collection), zod |
| Commands | More than 30 REST operations: add, remove, reorder and move across epics, sub-epics, stories, increments, scenarios, steps, examples |
| Seam | `StoryMapRepository` interface with `findById` and `save`; Mongo adapter behind it |
| Drag and drop | Dependency-free HTML5, shared `makeDragHandlers`, with its own stories for preview and reflow |
| Tests | Handoff of 2026-08-05 reports 171 tests in 51 files, all green. Not re-run |
| Comments | **None.** "comment" does not appear in the client, domain or server files |
| Authoring depth | Scenarios, steps and examples are editable, beyond what the canvas shows |

The story-ui editing stories themselves are already on the map under the epic Author Story Maps; Author Story Changes With AI (Request AI Story Change, Apply AI Change To Story Map) is the nearest feature to the comment path here.

#### Constraints from CDD

- **Three sources of truth compete.** LERN loads stories from TypeScript story code (`TypeScriptStoryModel`). The canvas rule `map-mirrors-drawio` says the latest drawio wins. story-ui keeps its own Mongo copy. Choosing one is the first decision.
- `cdd_guidance/practices/stories/model/AGENTS.md` says **"Do not sync an edited diagram back into the story map."** `ClaudeDesignStoryModel.parse` raises `NotImplementedError` accordingly. A canvas must therefore send **commands** ("add story X under Y"), never a diff of the picture. story-ui's REST operations already have this shape.
- A published canvas has no network, so it cannot call story-ui or localhost directly.
- `never-overwrite-a-published-canvas` means "auto-update the map" currently implies a whole new version.

#### Options

| Option | Strength | Weakness |
|---|---|---|
| **A. Comment-driven**: comment anchored to a node, an agent applies it | Works within the sandbox, keeps an audit trail, handles vague requests | Asynchronous; needs an agent watching |
| **B. story-ui as editor**, canvas as reader | 171 tests and rich editing already exist | Separate tool, Mongo, separate data |
| **C. Custom drag and drop built in `.dc.html`** | Everything in one place | Rebuilds story-ui by hand, the same duplication Sync Design Canvas With Production removes. Canvas drag moves pictures, not model nodes |
| **D. Mount story-ui's `StoryHierarchyView` in the canvas** | Real, tested drag and drop inside the canvas, using Sync Design Canvas With Production's mounting mechanism | Needs a data route out of the sandbox; React 19 on 18; may not be feasible |

**Recommendation: A now, then B with a file-backed repository, then D if the mechanism allows. Do not build C.** The canvas stays the place to review and comment; story-ui is the power editor; both go through one command path.

#### Decision before any story: the source of truth

Slice 1. Recommend story code for LERN: tests already run from it and the drawio is a rendering. This changes `map-mirrors-drawio` and needs a CDR. It is a decision, not a story, so it sits on this feature.

#### Story: Give Each Map Card A Stable Node Id

Slice 2. Everything below needs it.
- Add `data-node` to each card in `box()` and the explorer entries, derived from the story path.

#### Story: Comment On A Story Card

Slice 3.
- The canvas declares `comments` with `composer_only: true, customAnchors: true`.
- Whether a page can open a composer anchored to a node id needs testing.

#### Story: Change Story Code From A Canvas Comment

Slice 3.
- `ArtifactComments` reads comments for an agent.
- An agent turns a comment into a story code change, replies on the thread, and regenerates.

#### Story: Refresh Map Artboard From A Data File

Slice 4.
- Draw `Main.dc.html` from a `project/data/story-map.json` so an update publishes one data file instead of a whole new version.
- Trade-off: cards drawn by `sc-for` cannot be dragged individually in the editor (`diagrams.md`). Decide whether people hand-edit the map; if they do not, this is a clear win.

#### Story: Save Story Map To Story Files

Slice 5.
- Add a `StoryMapRepository` adapter over the CDD story graph in place of Mongo.
- Map between the two schemas, which differ: story-ui uses node ids and increments, CDD uses `Step` nodes and `ands`.
- A story added in story-ui appears on the next map refresh.

#### Story: Comment On A Story In Story UI

Slice 5.
- Add comments to story-ui as a new feature, keyed by the same node ids as the canvas.
- Requested (2026-11-10, "native claude markup panel": "annotate on the story editor app with notes and have a canvas like experience, eg comments sent directly to claude for processing; then potentially reuse that for a bespoke class editor and realization editor"): a comment goes straight to Claude for processing.

#### Story: Rearrange Stories Inside The Canvas

Slice 6, option D.
- Only after Phase 0 in [Sync Design Canvas With Production](sync-design-canvas-with-production.md).
- Needs a transport standing in for REST; the `db` capability is the candidate, unverified.
- React 19 on 18 is the same question as Phase 0 gate 2.

---

## Epic: Author Story Maps

### Feature: Author Story Changes With AI

The markup experience in the Story UI editor: notes on the map and comments sent straight to Claude (Comment On A Story In Story UI, above). Requested (2026-11-10, "native claude markup panel"): "then potentially reuse that for a bespoke class editor and realization editor"; those editors are not on the story map yet.

#### Story: Place Notes On The Story Map

- A person places notes anywhere on the Story UI editor's map, as on a canvas, beside the nodes they are about.
