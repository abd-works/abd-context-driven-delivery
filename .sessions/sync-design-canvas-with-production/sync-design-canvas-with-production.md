# Sync Design Canvas With Production

Session `claud_design_enhancements`. Analysis and planning only: nothing here is implemented. This increment is one of the design canvas increments in the thin slice, which sets their order, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to; approaches, options and recommendations sit on the feature they decide.

| Increment | Epic → feature on the story map | Depends on | First slice |
|---|---|---|---|
| **11: Sync Design Canvas With Production** | Build Design Canvas Screens → Reuse Production Assets On The Canvas, with its four sub-features: Trace Canvas Files To Production (Phase 1), Install Production Design System On The Canvas (Phase 2), Mount Production Views As Screens (Phases 0, 3, 5), Redesign A Screen By Detaching It (Phase 4) | Nothing; comes before every other design canvas increment | Phase 0 spike on the multi-line canvas's first screens: add a line, add another line, check the cart |

The other design canvas increments: [Integrate Stories With The Canvas Explorer](integrate-stories-with-the-canvas-explorer.md), [Draw Linked Models On The Canvas](draw-linked-models-on-the-canvas.md).

**Outcome:** a design canvas shows production as it is: every file is proven against the product repo by hash, styles and assets come from one pinned Design System package, each screen mounts the real view, hosted edits come back before the next version, and a screen being redesigned is detached and marked diverged until its change reaches production.

| Phase | Feature |
|---|---|
| 0. Spike on one screen | Mount Production Views As Screens (its gates) |
| 1. Manifest, no behaviour change | Trace Canvas Files To Production |
| 2. Design System package | Install Production Design System On The Canvas |
| 3. Mounted screens | Mount Production Views As Screens |
| 4. Detach and re-attach | Redesign A Screen By Detaching It |
| 5. Guidance | Mount Production Views As Screens (Generate Attached Screens Without Markup) |

## Epic: Build Design Canvas Screens

### Feature: Reuse Production Assets On The Canvas (the asset reuse plan)

#### Recommendation

**Package production as a pinned Design System, and mount it.** Do not link files.

1. The product repo builds one derived package: its real CSS, images and fonts in their original layout, plus an esbuild bundle of its real React views and the story fixtures.
2. That package is published once as a **Design System artifact**. Each canvas version takes it through a server-side copy into `project/ds/<product>/`, so nothing is re-uploaded or kept in the session folder.
3. Each `.dc.html` screen shrinks to a generated shell of about 30 lines that mounts the real view: `<x-import component-from-global-scope="Paradise.SelectPlanView">`.
4. A `sources.json` manifest records every packaged file's repo path, sha256 and git commit. A check fails when a file no longer matches, and the same data gives a traceability percentage for each version.
5. To redesign a screen, you **detach** it: the production view is rendered once to editable markup, the manifest marks it as diverged, and it is re-attached once the change lands in production.

Links cannot do this job, for one structural reason: **a published canvas is a sandbox that only sees its own `project/` files.** There is no path back to the repo, so every link stops working at publish. Symlinks also fail on this machine today (see the rejected options below). "Almost 100 percent the same" therefore has to mean *built from the source and proven by hash*, not *pointing at the source*.

This depends on one spike, because mounting real views in the canvas runtime has not been tried. If it fails, the fallback still removes every CSS and asset copy (see Phase 0 under Mount Production Views As Screens).

#### How the canvas works today

Evidence comes from the only real canvas on this machine, `C:\dev\pml-web\.sessions\design-system-setup\design-canvas\design-system-setup\project`, published as `https://claude.ai/artifact/9BXn2up1cvrirpSM9b587H`.

| Part | Files | Bytes | How it relates to production | Finding |
|---|---:|---:|---|---|
| `shots/` | 183 | 13,460,396 | Copied screenshots | Only 115 are unique (8,689,018 bytes). I found no PNG originals elsewhere in pml-web |
| `screens/` | 29 | 657,945 | **Hand-ported from TSX** | 46% of the 28 product screens' text is `DCLogic` (241,907 of 523,967 characters) |
| `fixtures/` | 1 | 561,953 | Built from real stories and domain | Already the right model |
| `assets/` | 33 | 342,654 | Copied | **33 of 33 byte-identical** to `packages/my-paradise/assets` |
| `context/` | 28 | 153,643 | Derived from the story model | Legitimate, but need not be stored |
| `styles/` | 2 | 107,819 | Copied with an edit | Differs from production only by 8 `url('./assets` → `url('../assets` rewrites |
| `Main.dc.html`, `canvas.json` | 2 | 93,671 | Derived from the story model | Legitimate, but need not be stored |

The three findings that matter are placed on the stories they drive: the duplicated screens under Mount Production Views As Screens, the fixture bundle under Bundle Product Views For The Canvas, and the drifted copies under Pull Hosted Edits Back Before Next Version.

#### Constraints from the canvas runtime

From the Design type's own `SKILL.md`, `format.md`, `design-system-components.md` and `dc-runtime.js`, read from the published artifact.

| Constraint | Consequence |
|---|---|
| A canvas serves only its own files under `project/` | Nothing outside `project/` resolves once published |
| A path holding `..` "never names a file" | Relative references to the repo are out |
| No network except a Google Fonts `css2` link and uploaded asset URLs | Production `fetch` calls cannot reach a server |
| No `<iframe>`, `<object>` or `<embed>` | Cannot embed the running app |
| Canvas limits: 512 files and 256 MB. One call holds 16 MB per `SKILL.md` (the Artifact tool states 64 MB per publish and 255 files) | This canvas has about 278 files of its own under `project/`, 183 of them screenshots. The artifact lists 300 with the type's files. Plan to the lower limits |
| The runtime loads React **18.3.1** as `window.React` | pml-web is on React **19** (`^19.3.0`) |
| `<x-import component-from-global-scope="Ns.Export">` mounts real components from a design system bundle | **The sanctioned way to run real code** |
| Design system files install under `project/ds/<folder>/`, by server-side copy, with a `designSystems` record holding the version | A pinned, hosted reference with provenance |
| Guidance: "screens, layout and copy stay markup", and components you define yourself can't be selected or edited | Mounting a whole screen **goes against this guidance on purpose**. See the trade-off under Redesign A Screen By Detaching It |

#### Options compared

| Option | Works when published? | Works on this Windows machine? | Fidelity | Verdict | Where it lands |
|---|---|---|---|---|---|
| **A. Direct relative reference** (`../../packages/...`) | No: outside `project/`, `..` refused | Yes, locally only | 100% locally, broken published | Reject | — |
| **B. Symlink** | No: must become bytes at publish | **No**: fails today | 100% locally | Reject | — |
| **C. Junction** (folders) | No | Yes, verified | 100% locally | Reject: same publish gap, folders only | — |
| **D. Hard link** | No | Yes, verified | Silent breakage | **Reject: dangerous** | — |
| **E. Copy plus hash check** | Yes | Yes | Bytes yes, screens no | Keep the hash check, drop stored copies | Trace Canvas Files To Production |
| **F. Bundler reference** (esbuild) | Yes, built output is in `project/` | Yes, in use today | Same source, build-time seams only | **Adopt for all code** | Bundle Product Views For The Canvas |
| **G. Design System install** | Yes, server-side copy, pinned version | Yes | Same bytes as F's output | **Adopt as the delivery route** | Install Production Design System On The Canvas |
| **H. `/_blob` uploads** | Yes, but per canvas | Yes | Same bytes | Reject: existing rule `each-version-carries-its-files` explains why | — |
| **I1. Fragment by cutting source text** (line ranges, markers) | Yes | Yes | Fragile: TSX is not HTML | Reject | — |
| **I2. Fragment by export** (entry re-exports only the views wanted) | Yes | Yes | 100% of what is included | **Adopt: this is the right way to cut a repo file** | Bundle Product Views For The Canvas |
| **I3. Fragment by render** (`renderToStaticMarkup`, or capture DOM at a step) | Yes | Yes | Exact at capture, then a copy | **Adopt, only for detach** | Detach A Screen To Editable Markup |
| **J. Own local surface** (a Vite app like `harness/graph/app`) | Not a canvas at all | Yes | 100%: direct imports | Keep as a last resort: loses editing, comments, sharing | — |

#### Why the rejected link options fail

**Symlinks (B).** Tested here: `New-Item -ItemType SymbolicLink` and `os.symlink` both fail with `WinError 1314`. Developer Mode is off, the session is not elevated, and `core.symlinks` is `false` in this repo and pml-web. Even with those fixed:

- `CanvasVersions.start_next` uses `shutil.copytree(base, target)`, which by default follows links and copies their contents, so every new version silently becomes copies. My own test of this did not run because the link could not be created; this is Python's documented default.
- `DesignCanvas.write` uses `target.write_text`, which writes **through** a link into the production file.
- The Artifact tool treats links specially for asset uploads and limits sources to the working directory and scratchpad. Publishing through `files` is untested.
- A symlink git stores with `core.symlinks=false` checks out as a small text file.

**Hard links (D).** These do work here, which is the trap. `write_text` would overwrite the production file with no warning. Meanwhile anything that replaces a file by rename, such as `git checkout` and many editors, breaks the link silently and leaves a stale copy that looks fine.

#### Target shape

```
product repo                         local canvas version           hosted
--------------                       --------------------           ------
packages/my-paradise/*.css, assets ┐
src/**/*.tsx (views)               ├─> ds package ──> Design System ──> server-side copy
tests/**/*.story.shared.ts         │   + sources.json   artifact        into project/ds/paradise/
                                   ┘
stories + ux.json ──────────────────> Main, explorer, context, thin screens ──> project/
                                      (regenerated, not stored as source)
detached screens ───────────────────> stored: the only hand-edited files
```

A version folder keeps only `sources.json`, `canvas.json` and detached screens, so `start_next` becomes cheap.

| Measure | Today (pml-web) | Target |
|---|---|---|
| Generator lines per product | ~3,700 | One generic `thin_screen()` in `harness/design_canvas/` |
| Screen text | 523,967 chars | ~30 lines × 28 |
| Bytes proven identical to source | 342,654 (2.2%) | All assets, CSS and bundle, by hash |
| Duplicate shots | 68 | 0, named by content hash |
| Files under `project/` | ~278 | Well under 512 |

Where code lands: generic parts in `harness/design_canvas/` (`CanvasSources` for the manifest and check, the thin-screen helper), LERN-specific build in `patterns/lern_domain_driven/practices/stories/model/claude_design/`. The MERN pattern has no `claude_design` folder, so it gets none of this until one is added.

#### Risks

| Risk | Note |
|---|---|
| Format dependency | The `.dc.html` contract is Anthropic's (`0.2.47` on this canvas). Keeping real code in a plain bundle limits exposure, since only the thin shell knows the format |
| Standalone Claude Design closes by 14 December 2026 | Stated in the `DesignSync` tool description. This canvas is already a `claude.ai/artifact` Design artifact, so I expect it to be unaffected, but that is **unverified**. Confirm before Phase 2 |
| Bundle size | 16 MB per call should be fine at current bundle sizes; a chunking plan is needed only if screens grow |
| Package is a snapshot | A canvas shows production as of its pinned version. The check reports staleness; it does not auto-update, which is the correct behaviour for a design review |

#### What is verified and what is not

| Status | Claim |
|---|---|
| **Run here** | Symlink failure and its causes, junction and hard link success, `core.symlinks` values, hash comparison of assets, CSS diff, shot duplicates, class-name check, runtime React version |
| **Read in source** | Everything cited from `harness/design_canvas`, `cdd_guidance`, pml-web and the Design type files |
| **Reasoned, not run** | React 19 elements failing on 18, the `define` seam, the route stand-in, all Phase 0 gates, `copytree` following links |
| **Not checked** | Publishing a link through the Artifact tool, why local and published files differ, CSS isolation in the explorer, whether mounted views stay usable in the editor |
| **Limit of evidence** | One real canvas exists on this machine, so the figures describe pml-web only |

---

#### Sub-feature: Trace Canvas Files To Production (Phase 1: manifest, no behaviour change)

Keeps option E's hash check and drops the stored copies. **Done:** a version reports its traceability percentage, and an edited CSS file fails the check.

##### Story: Record Packaged Files In Sources Manifest

- Add `sources.json` beside `CanvasVersions`, recording every packaged file's repo path, sha256 and git commit.

##### Story: Fail Check When A Packaged File Drifts

- Add a drift check beside `CanvasVersions` that fails when a file no longer matches its manifest entry; an edited CSS file fails it.

##### Story: Report Version Traceability Percentage

- The manifest gives each version its share of bytes proven identical to source. Today that is 342,654 bytes (2.2%); the target is all assets, CSS and bundle.

##### Story: Store Each Screenshot Once By Content Hash

- Dedupe shots by content hash: 183 shots hold only 115 unique ones, so 68 duplicates become 0.
- Decide where originals live, because none were found outside the canvas folder; e2e output under `.sessions/<release>/e2e-test-results` holds JSON, not PNGs.

##### Story: Report What Has Not Reached Production

- Each version lists its diverged screens, including screens with no production view yet, and its drifted files, each with the repo path it must reach.
- A canvas edit to a packaged file (CSS, image, font) shows here until the repo holds it, the Design System package is rebuilt, and its hash matches again.
- A version kept as a release must report none, or name each one as accepted.

##### Story: Find Screen Files Through The Manifest

Thin screens break these existence checks, so they read the manifest instead of the version folder:

| Code | Why it breaks |
|---|---|
| `_fixture_scripts` (`nodes.py:341`) | Checks the file exists in the version; a manifest entry would be silently dropped |
| `_blank` (`nodes.py:359`) | Stats the shot on disk; a missing file reads as not blank, so blank captures return |
| `_stylesheets` (`nodes.py:346`) | Regex-reads `<link>` lines from each screen; move to the manifest |

#### Sub-feature: Install Production Design System On The Canvas (Phase 2: Design System package)

Option G is the delivery route. **Done:** CSS and assets are byte-identical to the repo on the published canvas.

##### Story: Package Product Styles And Assets In Their Production Layout

- Mirror the `packages/my-paradise` layout under `ds/paradise/`; remove `copy_styles`.
- Layout solves the CSS problem: `ds/paradise/paradise.css` beside `ds/paradise/assets/` matches `packages/my-paradise`, so the 8 URL rewrites disappear and the CSS is byte-identical.

##### Story: Publish Product Package As Design System Artifact

- Publish one Design System artifact per product.

##### Story: Record Installed Design Systems In Canvas File

- `_canvas_json` hard-codes `"designSystems": []` (`canvas.py:67`), so that must become data: populate `designSystems` in `canvas.json`.
- Files copied this way are pinned ("a copy never changes by itself"), and one publish can draw on at most 4 source versions.

##### Story: Derive Publish List From Sources Manifest

- Replace `pub_*.json` with a publish list derived from the manifest.

##### Story: Pull Hosted Edits Back Before Next Version

- Add pull-back of hosted edits before `start_next`.
- Why: local and published copies have already drifted. The published artifact lists `canvas-fixtures.js` at 548,799 bytes and `refresh-alt-icon.svg` at 529; the local files are 561,953 and 532. I did not determine why. Separately, `start_next` copies the *local* folder (`versions.py:63`), and I found no code that pulls hosted edits back. People's edits on a published canvas may therefore be missing from the next version, despite the `never-overwrite-a-published-canvas` rule.

#### Sub-feature: Mount Production Views As Screens (Phases 0, 3 and 5)

**The real duplication is the screens.** About 3,700 lines of generators and patch scripts sit in `pml-web/.sessions/design-canvas/tools`. They are outside CDD, session-bound, and hard-code `C:/dev/paradise-mobile/pml-web` (`paradise_screens.py`, `render_pml_canvas.py`). They re-state markup and behaviour that already exist in 44 production `.tsx` files. A substring check of `select-plan.dc.html` found 41 of its 42 class names in the matching TSX, so the port is faithful today. Nothing keeps it that way.

**Phase 0: spike on the first multi-line screens (decides everything else).** Use pml-web's new multi-line canvas (`ux/prototype/multi-line-domain`, ported by `port_multiline_screens.py`), on a scratch canvas, and take only its first few screens, enough to test: **add a line**, **add another line**, and **check the cart** (the `add-line-to-cart` story's *Add the first line* and *Add one more line* scenarios, then the cart they open).

The multi-line canvas, from the pml-web built features chat on 2026-11-25:

| What | Where |
|---|---|
| Canvas | `C:/dev/paradise-mobile/pml-web/ux/design-canvas/version-6/project/` (`Main.dc.html`, `screens/`, `canvas.json`); versions in `ux/design-canvas/versions.json`. Published as `https://claude.ai/artifact/1zLwTyxmspnoJZcgAAE82o` (private; play links `#play-screens-add-line-to-cart` and `#play-screens-view-cart`); read only, the pml-web chat may republish it to the same link. version-5 (`https://claude.ai/artifact/VnncHtBz97QjjdjWDhtqjw`) ignores scenarios, so do not use it |
| Screens | `screens/display-plans.dc.html` (catalog), `screens/add-line-to-cart.dc.html` (*Add the first line*, *Add one more line*), `screens/view-cart.dc.html` (*View the cart with several lines*). Each wraps `screens/flow.dc.html`, Leo's prototype, at the story's state from `ux/prototype/multi-line/story-screens.json` |
| What the screens run | The prototype's markup over the real domain bundle `project/pml-domain.js` (`window.PMLDomain`), `multiline.js` and `ds/pmlapp` |
| Production views | `src/revenue/cart/plan-catalog.tsx` (`PlanCatalogView`, still single-line, takes `onSignUp`), `select-plan.tsx` (`SelectPlanView`), `checkout.tsx` (`CheckoutView`). The domain is built (`Cart`/`Line` in `cart.ts`; `CartClient.addLineToCart`/`removeLine` in `cart-client.tsx`) |
| Build | `.sessions/design-canvas/tools/port_multiline_screens.py`, then `render_pml_canvas.py`, with the CDD venv, cwd `abd-context-driven-delivery`, `PYTHONPATH=".;cdd_guidance;cdd_guidance/practices"`. The `LernCanvasFixtures` step (`node build-canvas-fixtures.mjs`) fails today; these screens do not use it |

**Finding that changes the spike:** no production view renders the multi-line cart yet (the lines list with add and remove). The add-a-line and cart screens exist only in the prototype, so there is nothing in production to mount for them. The spike therefore splits:

- **Mount gates (1, 2, 4, 5, 6)** run on the catalog in front of them, `PlanCatalogView`, the one production view these screens reach.
- **Data gate (3)** runs add a line, add another line, and check the cart through the real domain: `CartClient.addLineToCart` and `Cart`/`Line`, answered from fixture routes, which the prototype already exercises through `window.PMLDomain`.
- **Add a line and check the cart as mounted screens** wait until pml-web builds their views. Until then they stay prototype screens, marked as having no production view: the detached state of Redesign A Screen By Detaching It. Each gate has a pass test, and each gate is the first check of the story named beside it.

| Gate | Question | Pass | Story |
|---|---|---|---|
| 1. Mount | Does `x-import` resolve a bundle global from `project/ds/`? | The add-a-line view renders in a published canvas, and adding a second line and opening the cart work on it | Mount Production View In A Thin Screen |
| 2. React | Does React 19 source run on 18.3.1 with classic JSX? | Renders and handles clicks. A grep found no `use(`, `useActionState`, `useOptimistic`, `useFormStatus` or `forwardRef`; ref-as-prop was not checked | Bundle Product Views For The Canvas |
| 3. Data | Can the real routes run in the browser? | `createCartRoutes` takes its repositories as parameters, which suits a small router stand-in, but `*-node` is stubbed today and those routes call `CartNode.fromRequest`. Pass: a real route answers a fixture. Otherwise fall back to a thin fetch table over the in-memory repositories | Answer Screen Requests From Fixture Routes |
| 4. Navigation | Does the `define` seam hold? | `followStepIfNeeded` moves the explorer through `go`, and the artboard stays put | Keep Explorer Navigation Inside The Artboard |
| 5. Isolation | Does `.paradise` CSS stay inside the screen in the explorer? | The `sm-` panel is unaffected | Keep Product Styles Inside The Screen |
| 6. Editing | What can people actually do with a mounted view? | Written down, to confirm the trade-off | Redesign A Screen By Detaching It |

**Spike results, 2026-11-25** (throwaway; build in this chat's scratchpad, scratch canvas `https://claude.ai/artifact/4wi7YbbNQ28EzYQ774qGwX`, artboard `#play-screens-mounted-plan-catalog`; version-6 and pml-web untouched):

| Gate | Result | Evidence |
|---|---|---|
| Build | **Pass, with a workaround** | pml-web's views import `@my-paradise/paradise-shell` and `@my-paradise/assets/*`, but `packages/my-paradise` was deleted in `eb529d2` (2026-11-18), and `src/revenue/cart/*.tsx` and `src/inventory/plans/*` are uncommitted: `tsc` reports 2,082 errors and production cannot build these views today. The spike aliased `@my-paradise` to the package as of `eb529d2^`. esbuild IIFE `Paradise` (`PlanCatalogScreen`, `PlanCatalogView`), 333 KB JS + 345 KB CSS with assets inlined, `@ds-bundle` header as `ds/pmlapp` uses |
| 1. Mount | **Published, not yet seen** | `screens/mounted-plan-catalog.dc.html` mounts `<x-import component-from-global-scope="Paradise.PlanCatalogScreen">` from `ds/paradise/`. The browser pane is not signed in to claude.ai, so a person must look |
| 2. React | **Pass** | On React 18.3.1 (UMD from cdnjs) the real `PlanCatalogView` renders 5 plan cards, no errors. `react/jsx-runtime` is answered by a shim over `window.React.createElement`, so React 19's automatic JSX runs unchanged |
| 3. Data | **Pass (fetch table)** | The real `CartClient.loadPlans()` and `addLineToCart()` run unchanged; a build-time `fetch` table answers `GET /api/onboarding/state`, `GET /api/plans` (from `plans.json`) and `POST /api/onboarding/lines/add`. Sign up now twice: the cart holds 2 lines, Atlas and Ace. Real routes (express, `CartNode`) were not tried |
| 4. Navigation | **Not exercised** | `window.location` is redefined at build time to a stand-in that raises `canvas-go`; `PlanCatalogView` never calls it, so the seam is untested until a view that navigates is mounted |
| 5. Isolation | Open | Needs the published canvas looked at beside the explorer |
| 6. Editing | Open | Needs a person to try editing the mounted artboard |

**If gates 1 to 3 fail:** keep Phases 1 and 2 (assets, CSS, shots) and move screens to I3 render-to-markup, with `DCLogic` calling domain code as it does now. Screens remain copies, but generated and hash-pinned to the TSX, and the hand-written generators still go.

**Phase 3 task, not a story:** migrate the 28 screens, then delete the pml-web generators. **Done:** all 28 are attached and every explorer path works.

##### Story: Bundle Product Views For The Canvas

- Add a `canvas-components` bundle: export views by name (I2), plus `CanvasRoot` for scenario, remount and `go`.
- **The fixture bundle already proves the right pattern.** `LernCanvasFixtures.build` (`fixtures.py`) and `build-canvas-fixtures.mjs` pull real source through esbuild and stub the node tier at build time. Screens are the part that never got this treatment.
- Option F extends a build that already runs. Three seams must move:
  - `jsx: 'automatic'` in `build-canvas-fixtures.mjs` would pull in React 19's JSX runtime. React 18 is unlikely to accept those elements. Use classic `React.createElement` and resolve `react` to `window.React`.
  - `fetch` needs a build-time replacement. Ten client modules call it.
  - `window.location` is used at 16 sites, and `assign` would navigate the artboard away. esbuild `define` can redirect it at build time with **no production code change**.
- The reasoning here is from the code; none of it has been run.

##### Story: Mount Production View In A Thin Screen

- Add the generic thin-screen generator, driven by `ux.json`, replacing the hard-coded `prototype()` map. Each screen is a shell of about 30 lines that mounts the view with `<x-import component-from-global-scope="Paradise.SelectPlanView">`.
- `DesignCanvas.files` and `write` are text only (`Dict[str, str]`, `write_text`), so they cannot carry binary or source entries; they must change for thin screens.

##### Story: Answer Screen Requests From Fixture Routes

- Phase 0 gate 3: a real route answers a fixture, or a thin fetch table over the in-memory repositories stands in.

##### Story: Keep Explorer Navigation Inside The Artboard

- Phase 0 gate 4: the `define` seam holds, `followStepIfNeeded` moves the explorer through `go`, and the artboard stays put.

##### Story: Keep Product Styles Inside The Screen

- Phase 0 gate 5: `.paradise` CSS stays inside the screen; the explorer's `sm-` panel is unaffected. Not yet checked.

##### Story: Type Scenario Values Into A Mounted Screen

- The `one-scenario-list` rule types values through `fromFixture(...).entered`; mounted views own their state, so typing needs a driver. The same driver plays UI steps in Play A Story's UI Steps On A Screen ([Integrate Stories With The Canvas Explorer](integrate-stories-with-the-canvas-explorer.md)), so build it once.

##### Story: Generate Attached Screens Without Markup

Phase 5, guidance. **Done:** an agent following guidance generates no screen markup for an attached screen.

- Rewrite the rules in `claude_design.md` that thin screens break: `from-fixture`, `real-domain-logic`, `prototype-is-a-file`, `each-version-carries-its-files`.
- Rewrite `ux.md` step 10, which tells agents to "port each story's screen".
- `check_screen.cjs` extracts the `text/x-dc` logic, which thin screens no longer have; see Check Screen Logic Against Scenarios From A Command in [Integrate Stories With The Canvas Explorer](integrate-stories-with-the-canvas-explorer.md).
- Update the specs (`design_canvas_spec.py`, `claude_design_story_model_spec.py`).

#### Sub-feature: Redesign A Screen By Detaching It (Phase 4: detach and re-attach)

**The trade-off to accept.** A mounted view runs real code, but the editor sees it as one element: people cannot click into its text and retype it. Hand-ported markup is fully editable but is a copy. Since the goal is production-identical design, **attached is the default and detach is the explicit step**:

| State | Screen file | Editable on canvas | Traceable | When |
|---|---|---|---|---|
| **Attached** | Thin mount | Props and fixtures only | 100% | Every screen that exists in production |
| **Detached** | Rendered from production once (I3), leaf components still mounted | Yes | Marked diverged | A redesign in progress |

This keeps a clear answer to "is this what production does?" for every screen. Phase 0 gate 6 writes down what people can actually do with a mounted view, to confirm this trade-off. **Done:** a detached screen is editable and visibly marked; re-attaching clears the mark.

##### Story: Detach A Screen To Editable Markup

- Add `detach(screen)` using render-to-markup (I3: `renderToStaticMarkup`, or capture DOM at a step).

##### Story: Keep Leaf Components Mounted In A Detached Screen

- Leaf components such as `PlanCardView` and `ParadiseShell` take props and can stay mounted inside a detached layout; `SelectPlanView` owns its state and client calls, so it mounts whole.

##### Story: Mark Detached Screen As Diverged

- Add diverged marking on the map and explorer; the manifest marks the screen as diverged.

##### Story: Reattach A Screen Once Its Change Reaches Production

- A detached screen shows as diverged until the change lands in the TSX, then it re-attaches and the mark clears.

##### Story: Check A Redesign Against Production Before Reattaching

- When a diverged screen's view changes in the product repo, render the new view at the same scenario state and compare it with the detached markup: the elements, classes and text it shows, and a screenshot difference.
- A match reattaches the screen and clears the mark. A mismatch keeps it diverged and lists what differs, so a redesign is never marked as reaching production when it hasn't.
- Without this, the mark clears when the TSX changes at all, and nothing proves production matches what was designed.

## From Fully Integrated App Flow

Moved here on 2026-11-23: keeping a canvas version as a release.

### Feature: Publish And Release A Canvas Version

#### Story: Remove Older Versions When Keeping A Release

*Agent*. Intended (`claude_design.md` release-a-version): when a version is kept as a release the older versions are removed; `release` in `versions.py` only renames.
