# Design canvas backlog

Follow-on work after the asset reuse plan, [design-canvas-asset-reuse-plan.md](design-canvas-asset-reuse-plan.md), which comes first. Each item below can be picked up on its own once its dependencies are met. Nothing here is implemented.

The items are organised by the story map, [harness/.context/stories/story-map.md](../../../harness/.context/stories/story-map.md): epic, then feature, then story, with each requirement under the story it belongs to. The increments are in [thin-slice.md](../../../harness/.context/stories/thin-slice.md).

| # | Item | Epic → feature on the story map | Depends on | Recommended first slice | Thin slice increment |
|---|---|---|---|---|---|
| 1 | Test button | Build Design Canvas Screens → Check Screens Against Their Scenarios | Plan Phase 0 for slice C | Show existing end-to-end results on the explorer tree | 14: Check Screens Against Their Scenarios |
| 2 | story-ui and canvas authoring | Connect Sessions Across Channels And Apps → Change Stories From Canvas And Story UI | Comments check | Comment on a story, an agent updates the story code | 15: Change Stories From Canvas And Story UI |
| 3 | All diagrams on the canvas | Build Design Canvas Screens → Draw Linked Models On The Canvas | None | Bounded context map as linked artboard | 16: Draw Linked Models On The Canvas |

---

# Epic: Build Design Canvas Screens

## Feature: Check Screens Against Their Scenarios (item 1)

**Goal.** A person on the canvas presses Test and sees, per scenario, whether what they are looking at behaves as the specs say.

**Done means.** Pressing Test on a scenario shows pass or fail per step with the failing assertion's message, a detached screen is tested against the same story as production, and stale results are labelled.

### What exists

- pml-web has 9 sub-epics, each with `.story.shared.ts`, `.story.playwright.ts`, `.story.server.spec.ts` and `.story.legacy-compare.ts`. There are no `.spec.tsx` component tests.
- The canvas already carries the stories. `canvas-fixtures.ts` installs a story host that **records Givens only**: `it()` records and discards the body, and `build-canvas-fixtures.mjs` replaces vitest's `expect` with a no-op. Thens never run on the canvas today.
- `check_screen.cjs` (pml-web session tools) runs a screen's logic on each scenario in Node. It is useful but lives outside CDD.
- End-to-end output exists at `.sessions/<release>/e2e-test-results` (94 JSON, 13 JSONL, plus an HTML story map).
- `scripts/end-to-end.mjs` takes around 20 to 30 minutes per sub-epic, by its own comments, so it cannot sit behind a button.
- Shared Whens mostly act on domain objects: `when('the Customer opens My Paradise', () => { catalog = repositories.plans.list(); })`. Only the Playwright tier drives UI. That file mixes UI steps with node repositories, so it does not run in a browser as it stands.

### The key insight

What needs testing depends on the screen's state from the asset reuse plan:

- **Attached** screens run the same code Playwright already tested. Re-testing proves little; the useful question is "does this bundle's hash match a passing run?"
- **Detached** screens are the real risk, because their behaviour differs from production by design.

### Options

| Slice | What it proves | Where it runs | Effort | Stories |
|---|---|---|---|---|
| **A. Results overlay** | Latest pass or fail per scenario, tied to bundle hash | Published with the canvas, no run needed | Small | Package End-To-End Results With The Canvas; Mark Each Explorer Scenario Passed Or Failed; Label Stale Test Results |
| **B. Run Thens in the canvas** | The packaged domain and fixtures still satisfy the specs | Browser, on press | Small to medium | Run A Scenario's Thens On The Canvas |
| **C. Play the UI steps** | A screen, including a detached one, responds as the story says | Browser, on press | Large | Play A Story's UI Steps On A Screen |
| **D. Local runner** | Full Playwright against a canvas | Local command, results published back | Medium | Check Screen Logic Against Scenarios From A Command |

**Recommendation: A, then B, then C.** Add D only if C proves too limited.

### Limits

A canvas cannot start local processes, so the button can only run what is in the page. Page state does not persist, so results vanish on reload unless written to the `db` capability, whose rule on this canvas is `write: admin`. Whether a viewer's page can write there is unverified.

**Open question.** The story map moves the story explorer into the Story UI app (epic Explore Stories In Story UI). The Test button is planned on the canvas explorer; if the explorer moves first, the button moves with it.

### Story: Package End-To-End Results With The Canvas

Slice A.
- Read the end-to-end JSON at package time into a `results.json`, tied to the bundle hash of the run.

### Story: Mark Each Explorer Scenario Passed Or Failed

Slice A.
- Show a pass mark, a fail mark or "no result" on each explorer scenario.

### Story: Label Stale Test Results

Slice A.
- A result is stale if the bundle hash differs from the run's, and is labelled so.

### Story: Run A Scenario's Thens On The Canvas

Slice B.
- Add a second story host that runs `beforeEach` and `it` bodies rather than recording them.
- Swap the no-op `expect` for a real one in a test build. `@vitest/expect` looks suitable but is unverified in the browser.
- Add a Test button to the explorer panel, per scenario and per story.
- Show pass or fail per step with the failing assertion's message.
- Keep the no-op for the normal bundle if size matters.

### Story: Play A Story's UI Steps On A Screen

Slice C.
- Build a small `page` facade over the DOM (`getByRole`, `getByLabel`, `click`, `fill`, `expect(locator)`), with `@testing-library/dom` underneath.
- Alias `@playwright/test` to the facade at bundle time.
- The hard part is that Playwright files seed through `*-node` repositories and `startMyParadise`. They must be split so UI steps can run alone. This may mean changing how those files are written, which needs its own decision.
- The same driver solves the plan's open `one-scenario-list` problem of typing values into mounted views (plan story Type Scenario Values Into A Mounted Screen), so build it once.
- A detached screen is tested against the same story as production.

### Story: Check Screen Logic Against Scenarios From A Command

Slice D, only if C proves too limited.
- Promote `check_screen.cjs` into `harness/design_canvas/` as a generic command, and optionally drive a canvas with Playwright.
- A hosted canvas needs a signed-in claude.ai session, so this is awkward to automate unattended.
- Thin screens no longer carry the `text/x-dc` logic `check_screen.cjs` extracts (asset reuse plan, Generate Attached Screens Without Markup), so the command must read the mounted view instead.

---

## Feature: Draw Linked Models On The Canvas (item 3)

**Goal.** Domain model, class model and bounded context map sit beside the story map, linked to each other, so the canvas is a navigable surface over the whole model.

**Done means.** From any story you can reach its screen, its classes and its bounded context by clicking, and back. Every diagram matches its drawio layout, and a changed drawio shows on the next generation.

### What exists

| Asset | Detail |
|---|---|
| Diagrams | pml-web has `src/.context/bounded-context-map.drawio` (85 cells), `domain-model.drawio` (125), and 11 module diagrams such as `subscription.drawio` (46) |
| Parsers and renderers | `DrawIOBoundedContextMap`, `drawio_aggregate_model`, `DrawIOCleanEngineeringModel`, `MiroCleanEngineeringModel`. There is **no `claude_design` format** for ddd or clean_engineering; only stories and ux have one |
| Links between practices | `harness/graph/schema_edges.py` lists `shownOn`, `specifiedBy`, `specifies`, `demonstrates`, `invokes`, `uses`, `dependsOn` and others. pml-web's `.context/graph.json` is 19.7 MB across 5 practices |
| Canvas parts | `box()` for cards, `artboard(zoomable=True)`, `LINK_KEY` keeps link hashes the canvas drops |
| Graph app | `harness/graph/app` is a React 18 Vite explorer with a `GraphView`. It depends on a Python server and Monaco, so it will not mount on a canvas as it is. Parts such as `kind-mark.tsx` may |

Related stories already on the map: Display Drawio File As Diagram (Graph app) and Trace Story Through Artifacts (Chat Bar) reach the same models from other surfaces.

### Canvas rules that shape this

- A diagram is built from separate placed elements, not one `<svg>`, so each box can be selected.
- One small `<svg>` per straight arrow segment, with exact formulas in `diagrams.md`.
- **Arrows do not follow cards.** A person who moves a box must redo its arrows, so these diagrams are for reading and linking, not rearranging.
- `one-map-artboard` warns that many live artboards render hatched and slow. Mark diagrams `is_interactive` only if they need it.

### Options

| Option | Strength | Weakness |
|---|---|---|
| **A. Literal elements from drawio geometry** | Selectable, linkable, same layout as the source, reuses parsers | Needs an arrow renderer and routing from drawio waypoints |
| **B. Export drawio to SVG** | Exact picture | One block in the editor; needs the draw.io CLI; links harder |
| **C. Embed a drawio viewer** | Native | No `<iframe>`, no network; would need a bundled viewer |
| **D. Auto-layout from the graph** | No drawio needed | Throws away human layout, contrary to `map-mirrors-drawio` |

**Recommendation: A.** It follows the rule that made the story map work: mirror the drawio exactly. Diagrams are derived from models, not production assets, so generating them does not conflict with the asset reuse plan.

### Unknowns

- How many artboards before the canvas slows. Test with the 13 pml-web diagrams at slice 3.
- Whether drawio waypoints are clean enough to reuse, or whether some edges need rerouting.
- Whether the file limit stays comfortable. It should once the asset plan removes duplicate shots.

### Story: Draw Arrows From Drawio Waypoints

Slice 1.
- Add `arrow()` to `harness/design_canvas/canvas.py` from the `diagrams.md` formulas, splitting drawio waypoints into straight segments, one small `<svg>` per segment.
- Spec it on one card pair.

### Story: Draw Bounded Context Map As An Artboard

Slice 2. The smallest diagram with the highest orientation value.
- Add a `claude_design` format to the ddd practice (`ddd.py` formats, `model/claude_design/`).

### Story: Draw Domain Model As An Artboard

Slice 3.
- One artboard per diagram on a new `Models` page.

### Story: Draw Module Class Models As Artboards

Slice 3.
- One artboard per module class model on the `Models` page.
- Add clean_engineering's `claude_design` format, sharing the layout code with the ddd format.

### Story: Follow Links From A Context To Its Models

Slice 4.
- Context → its domain model → module class model, using `<a href>` with `LINK_KEY`.
- Hashes select the target node on arrival.

### Story: See The Classes A Scenario Touches

Slice 5.
- From a scenario in the explorer, show the classes it touches, using `specifiedBy` and `invokes` from the graph.
- Export only the edges needed, since the full graph is 19.7 MB.
- Check which edges are actually populated; I read the edge names, not their contents.

### Story: See The Stories That Exercise A Class

Slice 5.
- From a class, list the stories that exercise it, from the same exported edges.

### Story: Mark Model Nodes That Fail Rules

Slice 6, optional.
- Badge nodes that fail rules, using the graph's `violations: true` filter.

---

# Epic: Connect Sessions Across Channels And Apps

## Feature: Change Stories From Canvas And Story UI (item 2)

**Goal.** Add a story, epic and so on from the canvas or from story-ui, comment on a story, and have the map update.

**Done means.** A comment on a story results in a changed story and an updated map with a reply on the thread. A story added in story-ui appears on the next map refresh. Both paths end in the same story code.

### What exists

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

### Constraints from CDD

- **Three sources of truth compete.** LERN loads stories from TypeScript story code (`TypeScriptStoryModel`). The canvas rule `map-mirrors-drawio` says the latest drawio wins. story-ui keeps its own Mongo copy. Choosing one is the first decision.
- `cdd_guidance/practices/stories/model/AGENTS.md` says **"Do not sync an edited diagram back into the story map."** `ClaudeDesignStoryModel.parse` raises `NotImplementedError` accordingly. A canvas must therefore send **commands** ("add story X under Y"), never a diff of the picture. story-ui's REST operations already have this shape.
- A published canvas has no network, so it cannot call story-ui or localhost directly.
- `never-overwrite-a-published-canvas` means "auto-update the map" currently implies a whole new version.

### Options

| Option | Strength | Weakness |
|---|---|---|
| **A. Comment-driven**: comment anchored to a node, an agent applies it | Works within the sandbox, keeps an audit trail, handles vague requests | Asynchronous; needs an agent watching |
| **B. story-ui as editor**, canvas as reader | 171 tests and rich editing already exist | Separate tool, Mongo, separate data |
| **C. Custom drag and drop built in `.dc.html`** | Everything in one place | Rebuilds story-ui by hand, the same duplication the asset plan removes. Canvas drag moves pictures, not model nodes |
| **D. Mount story-ui's `StoryHierarchyView` in the canvas** | Real, tested drag and drop inside the canvas, using the plan's mechanism | Needs a data route out of the sandbox; React 19 on 18; may not be feasible |

**Recommendation: A now, then B with a file-backed repository, then D if the mechanism allows. Do not build C.** The canvas stays the place to review and comment; story-ui is the power editor; both go through one command path.

### Decision before any story: the source of truth

Slice 1. Recommend story code for LERN: tests already run from it and the drawio is a rendering. This changes `map-mirrors-drawio` and needs a CDR. It is a decision, not a story, so it sits on this feature.

### Story: Give Each Map Card A Stable Node Id

Slice 2. Everything below needs it.
- Add `data-node` to each card in `box()` and the explorer entries, derived from the story path.

### Story: Comment On A Story Card

Slice 3.
- The canvas declares `comments` with `composer_only: true, customAnchors: true`.
- Whether a page can open a composer anchored to a node id needs testing.

### Story: Change Story Code From A Canvas Comment

Slice 3.
- `ArtifactComments` reads comments for an agent.
- An agent turns a comment into a story code change, replies on the thread, and regenerates.

### Story: Refresh Map Artboard From A Data File

Slice 4.
- Draw `Main.dc.html` from a `project/data/story-map.json` so an update publishes one data file instead of a whole new version.
- Trade-off: cards drawn by `sc-for` cannot be dragged individually in the editor (`diagrams.md`). Decide whether people hand-edit the map; if they do not, this is a clear win.

### Story: Save Story Map To Story Files

Slice 5.
- Add a `StoryMapRepository` adapter over the CDD story graph in place of Mongo.
- Map between the two schemas, which differ: story-ui uses node ids and increments, CDD uses `Step` nodes and `ands`.
- A story added in story-ui appears on the next map refresh.

### Story: Comment On A Story In Story UI

Slice 5.
- Add comments to story-ui as a new feature, keyed by the same node ids as the canvas.

### Story: Rearrange Stories Inside The Canvas

Slice 6, option D.
- Only after the plan's Phase 0.
- Needs a transport standing in for REST; the `db` capability is the candidate, unverified.
- React 19 on 18 is the same question as Phase 0 gate 2.
