# status
fidelity: explore
scope: Story Demo shell — Play dual runner + Interactive (Manage Character Sheet)
primary: this file — sole Story Demo sketch (ce → bdd → ux under each theme)

flow:
  status: in-progress
  recommend: proceed
  next: explore
  note: browser-safe create{Story}Story exports (story-test-core + soft-assert); mount loads them for Play.
  open: []
  done:
    - pass #lock-play-interactive
    - pass #primary-story-runner-sketch
    - pass #story-demo-ux-submodule-naming
    - pass #impl-story-test-split
    - pass #impl-story-steps
    - pass #impl-collect-return
    - pass #impl-story-demo-html-shell
    - pass #impl-ux-model-story-demo-control
    - pass #impl-ux-generated-playable
    - pass #impl-browser-story-exports

// Reading order = user journey: land on surface → Play next through story → Interactive When
// Lens order under each theme: ce → bdd → ux
// Locks: Play = dual runner + expose paint; Interactive = whenStep.fn via story_steps (not helper.given*);
//   story owns domain; Stories mode as is (create{Story}Story(mode))
// Modules: PlayDualRunner + StoryDemo* ⊂ UX story-demo/ (runner in play-dual-runner/)
//   (vanilla Page / Control stay product UX — no story_steps / bound_field)

=========
# theme: Story demo HTML surface  (module)
---------
## ce:
// What the user sees and triggers. Maps to UX Screen → Region → Control; one HTML page.
// Story Demo types wrap/extend vanilla UX — product pages/controls stay vanilla.

StoryDemoPage                         // one HTML document (mockup+spec channel)
  storyDemoFrame                      // LEFT — product UI (StoryDemoFrame)
  explorerFrame                       // RIGHT — epic → story → scenario → steps
  mode                                // Play | Interactive

  load()
    -> PlayDualRunner.collect(create{Story}Story, mode)
    -> explorerFrame.bindStoryTree(story)
  selectScenario(scenarioIndex)
    -> PlayDualRunner.start(story, scenarioIndex)
    -> explorerFrame.highlightStep(current)
    -> storyDemoFrame.clearEmphasis()

  ----
 StoryDemoFrame                       // LEFT pane (was MockupFrame)
  controls[]                          // StoryDemoControl[]
  bind(snapshot)
    -> for each StoryDemoControl: StoryDemoControl.show(snapshot via bound_field)
  emphasize(step)
    -> StoryDemoControl.emphasize()   // story_steps match step.kind + step.label
    // never shows GWT step prose — steps live only in ExplorerFrame
  tintFailed(result)
    -> StoryDemoControl.tint()

  ----
 ExplorerFrame                        // RIGHT pane
  storyTree
  playNextControl                     // [ Play next ] — chrome only (StoryDemoControl)
  resetControl
  messageArea

  bindStoryTree(story)
    -> show scenarios and step labels (kind + label)
  highlightStep(step)
    -> mark › current step ‹ in the tree
  showMessage(message) / clearMessage()
  markStep(step, ok)

  playNextControl.interactions[]
       Interaction
         trigger                      // eg click
         -> PlayDualRunner.playNext() // only place Play is invoked from the page
  // product StoryDemoFrame controls are NOT invoked during Play

  ----
 StoryDemoControl : Control           // button | field | list row | … (story demo only)
  name
  bound_field                         // expose() path to show on bind — display only
  story_steps                         // bind ↔ GWT kind+label
                                      // Play: emphasize only (not invoked)
                                      // Interactive: which When step.fn to run
                                      // HTML render: data-story-steps
  show(value)
  emphasize() / clearEmphasis()
  tint()
  // vanilla Control has no bound_field / story_steps / emphasize / tint
---
## bdd:
a story returned from collect
  -> story = PlayDualRunner.collect(create{Story}Story, mode)
  that has been collected
    it should keep its name
      -> expect(story.name).to equal "Create Character"
    it should hold the scenarios declared inside create{Story}Story
      -> expect(story.scenarios.length).to be >= 1

a story demo page
  -> page = StoryDemoPage.load(create{Story}Story, mode)
  -> // frames: storyDemoFrame (left), explorerFrame (right)
  that has loaded a story
    it should show the story tree in the explorer frame
      -> expect(page.explorerFrame.shows(story.name)).to be true
    it should show step labels in the explorer frame
      -> expect(page.explorerFrame.showsStepLabels()).to be true
  that the user selects a scenario
    -> page.selectScenario(0)
    it should start that scenario for play
      -> // PlayDualRunner.start
---
## ux:
product — create character          (left pane)
  └─ [action] Create Character ────→ Interactive: whenStep.fn → bind
                                     Play: «emph» only (not invoked)

product — update ability rank       (left pane)
  ├─ [action] select Ability row ──→ selection only
  └─ [action] Update Rank ─────────→ Interactive: whenStep.fn → bind
                                     Play: «emph» only (not invoked)

Nav tags: [Quick Action] · [secondary nav] · [action] · [system]

[ product — create character ]                    sidebar   (left pane)
  ┌────────────────┬────────────────────────────┐
  │ ▼ Characters   │ Abilities                  │
  │   (empty)      ├────────────────────────────┤
  │                │ ability · rank             │
  │                │ (none until create)        │
  │                │                            │
  │                │ [ Create Character ] «emph»│
  └────────────────┴────────────────────────────┘
  Stories (~1): Create Character
  Domain terms: Character · Ability · Rank · handbook abilities · initiative
  key:
    tree · list · [ btn ]
    «emph» when current explorer step matches this button's story_steps
    Play: not invoked · Interactive: → BDD interactive when control · after: sheet filled from expose

[ product — update ability rank ]                 sidebar   (left pane)
  ┌────────────────┬────────────────────────────┐
  │ ▼ Characters   │ Abilities                  │
  │   › Hero ‹     ├────────────────────────────┤
  │                │ ability · rank · debil.    │
  │                │ › strength · 5 ‹ «emph»    │
  │                │ stamina · 0                │
  │                │ … (eight handbook names)   │
  │                │ [ Update Rank ] «emph»     │
  └────────────────┴────────────────────────────┘
  Stories (~1): Update Ability Rank
  Domain terms: Character · Ability · Rank · debilitated
  key:
    tree · list · [ btn ] · ›sel‹
    «emph» / «tint» when story_steps match current step (Play); Interactive: → BDD interactive when control
    chrome: same sidebar as product — create character
    Given may pre-paint Character + Abilities before When
=========

# theme: Play dual runner  (module)
---------
## ce:
// PATTERN (Stories + CE — as today)

// file {family}.{ext}
I{Type}
{Type} : I{Type}

// file {type}_example_factory.{ext}
{Type}ExampleFactory
  {example_method}({ mode })
    // examples[{example_key}] -> I{Type}, …
    // Fake | Isolated | Production = modes, not subtypes — no Fake{Type} subclasses

// file {epic}-helper.{ext}
{Epic}Helper
  {type}ExampleFactory
  given{ExampleKey}({ mode })
    -> {type}ExampleFactory.{example_method}({ mode })
  // called only from story step fn bodies — never from StoryDemoControl.Interaction
  // Stories mode wiring as is — no Session.init / helper.init(mode)

  ----
 Story
  // create{Story}Story(mode) — same as Stories exploration/engineering
  name
  declare(mode)
    -> scenario(...) { given / when / then / expose }
    -> // invariant: story does not push steps[] or import PlayDualRunner / HTML

Scenario domain variables
  {domainRef}                        // private variable — I{Type}
  {bundle}                           // factory return

  given / when / then fn bodies      // run later via Play or node:test
    -> helper.given{ExampleKey}({ mode })
    // or mutate I{Type} fields; assert on interfaces only

  expose
    // expose(() => ({ {domainRef}, {bundle}, … }))
    // registered while declaring; read after step.fn() for StoryDemoFrame.bind

  ----
 PlayDualRunner                       // UX story-demo/play-dual-runner
  collect(create{Story}Story, mode)
    -> create{Story}Story(mode)
    -> given/when/then(label, fn)
         steps.push({ kind, label, fn })
    -> expose(getter) registered on scenario
    -> returns story { name, scenarios[] }
    // invariant: collect owns steps[] / expose (story-test extended)
  start(story, scenarioIndex)
    -> scenario = story.scenarios[scenarioIndex]
    -> index = 0
  playNext
    -> step = scenario.steps[index]
    -> result = step.fn()             // product controls not invoked
    -> index = index + 1
    -> PaintReflect.apply(scenario.expose())
    -> ExplorerFrame.highlightStep(step)
    -> StoryDemoFrame.emphasize(step) // story_steps ↔ kind+label
    -> if step.kind == then: ThenFeedback.apply(result)
  // invoked only by explorer playNextControl Interaction
  // node:test path: same collect; before/it instead of playNext

  ----
 PaintReflect
  apply snapshot
    -> StoryDemoFrame.bind(snapshot)  // controls read via bound_field
    // invariant: domain → controls only — no new {Type}(); no ThenFeedback

  ----
 ThenFeedback
  apply result
    -> ExplorerFrame.markStep(result.step, result.ok)
    -> if result.ok: ExplorerFrame.clearMessage()
    -> if not result.ok: ExplorerFrame.showMessage(result.message)
    -> if not result.ok: StoryDemoFrame.tintFailed(result)
    // invariant: peer to PaintReflect — Then steps only
---
## bdd:
a scenario told with given when and then
  that has been collected by the dual runner
    -> story = PlayDualRunner.collect(create{Story}Story, mode)
    -> session = story.scenarios[0]
    it should keep an ordered steps list
      -> expect(session.steps.map(s => s.kind))
           .to equal ["given", "when", "then", …]
      -> expect(session.steps[0].label)
           .to equal "no Character yet"
  that is started for play
    -> PlayDualRunner.start(story, 0)
  that is stepped via play next
    with play next advancing one step
      -> result = PlayDualRunner.playNext()
      it should run that step's fn once
        -> expect(result.step.label).to equal "no Character yet"
        -> expect(session.index).to equal 1
      it should leave domain variables mutated for later expose
    with play next on a then step that fails an assertion in the browser
      -> result = PlayDualRunner.playNext()
      it should soft-fail without aborting play
        -> expect(result.ok).to be false
  that exposes domain for the page to display
    with expose registered while the scenario was collected
      -> expose(() => ({ …domain variables }))
      it should return the same domain variables after playNext
        -> snapshot = session.expose()
        -> expect(snapshot).to be the scenario domain variables
  that is proven under node tests
    it should run givens and whens before thens
    it should use the same step fns as play
  that is stepped in the browser without node test
    it should load collect+play without importing node test

a story demo page
  that the user activates play next on the explorer
    -> page.explorerFrame.playNextControl.trigger("click")
    -> // only explorer chrome invokes Play — not StoryDemoFrame product controls
    it should advance one story step
      -> // PlayDualRunner.playNext → step.fn()
    it should paint expose data onto story demo controls via bound_field
      -> snapshot = session.expose()
      -> expect(page.storyDemoFrame.shows(snapshot)).to be true
    it should highlight the current step only in the explorer
      -> expect(page.explorerFrame.currentStepHighlighted()).to be true
    it should emphasize matching story demo controls or fields
      -> expect(page.storyDemoFrame.emphasizedFor(session.currentStep)).to be true
      -> // story_steps match kind+label; product controls not invoked
  that a then step fails
    -> page.explorerFrame.playNextControl.trigger("click")
    it should show a failure message in the explorer
      -> expect(page.explorerFrame.messageVisible()).to be true
    it should tint failed values on the story demo frame
      -> expect(page.storyDemoFrame.hasTint()).to be true
---
## ux:
story demo shell — Play
  ├─ [secondary nav] select Create Character ──→ product — create character
  ├─ [secondary nav] select Update Ability Rank → product — update ability rank
  ├─ [Quick Action] Play next ─────────────────→ (same shell; one GWT step)
  ├─ [Quick Action] Reset ─────────────────────→ (same shell; clear session)
  └─ [action] expand / collapse explorer node ─→ (same shell; tree only)

[ story demo shell — Play ]                       split-screen
  ┌──────────────────────────────┬────────────────────────────┐
  │ STORY DEMO (left)            │ EXPLORER (right)           │
  │ ┌──────────────────────────┐ │ [ Reset ]                  │
  │ │ product pane             │ │ ▼ Manage Character Sheet   │
  │ │ (create / update)        │ │   ▶ Create Character       │
  │ │                          │ │     › scen: handbook… ‹    │
  │ │  «emph» pane / control / │ │       Given no Character…  │
  │ │  field for current step  │ │       › When the Player… ‹ │
  │ │  (no step text here)     │ │         ↑ current step     │
  │ │                          │ │       Then a Character…    │
  │ │  «tint» failed field     │ │       Then And each…       │
  │ │  (after Then fail)       │ │   ▶ Update Ability Rank    │
  │ └──────────────────────────┘ │     scen: …                │
  │                              ├────────────────────────────┤
  │                              │ [ ▶▶ Play next ]           │
  │                              │ ! Then failed: …           │
  └──────────────────────────────┴────────────────────────────┘
  Stories (~2): Create Character · Update Ability Rank
  Domain terms: Character · Ability · Rank · Player
  key:
    split-screen · tree · [ btn ] · ›sel‹ · ▼/▶ · «emph» · «tint» · ! message
    RIGHT: GWT steps live only here; ›step‹ = current step highlighted
    LEFT: «emph» pane / control / field only — never list step prose
    on [ Play next ] (explorer only) → CE playNext
      (visible: ›step‹ · bind fields · «emph» · ! / «tint» if Then fail)
    on select scenario → tree + empty / Given story demo frame
    on [ Reset ] → clear cursor / story demo frame / message / «emph»
    // product Create / Update Rank: «emph» in Play; Interaction only in Interactive
=========

# theme: Interactive when control  (module)
---------
## ce:
// StoryDemoPage.mode = Interactive
// Given already applied (Play background or load)

StoryDemoControl : Control
  interactions[]                      // Interactive — not Play next
       Interaction
         trigger                      // click | hover | drag | change | …
         effect
         -> whenStep = scenario.stepMatching(story_steps, kind="when")
         -> whenStep.fn()             // same fn Play would run
         -> PaintReflect.apply(scenario.expose())
         -> StoryDemoFrame.bind(snapshot)
         // helper.given* stays inside When fn (Stories) — control never calls it

  ----
 StoryDemoPage
  onControlTrigger                    // product StoryDemoControl.Interaction
    -> whenStep = scenario.stepMatching(control.story_steps, kind="when")
    -> whenStep.fn()
    -> PaintReflect.apply(scenario.expose())
    -> StoryDemoFrame.bind(snapshot)
    // invariant: run bound When via story_steps — no ThenFeedback; no playNext
    // invariant: do not call helper.given* from the control
---
## bdd:
a story demo page in interactive mode
  that has given already applied
    with the user activating a when control on the story demo frame
      -> page.storyDemoFrame.controlFor(whenLabel).trigger("click")
      -> // or drag / hover / change — per Interaction.trigger
      it should run the when step fn bound by story_steps
        -> // same fn Play would run — not helper.given* from the control
      it should paint expose data onto story demo controls via bound_field
      it should not run then feedback
      it should not call play next
---
## ux:
story demo shell — Interactive
  ├─ [secondary nav] (same product panes as Play)
  ├─ [action] Create Character / Update Rank ──→ whenStep.fn via story_steps → bind
  └─ [Quick Action] (optional) back to Play ───→ story demo shell — Play

[ story demo shell — Interactive ]                split-screen
  ┌──────────────────────────────┬────────────────────────────┐
  │ STORY DEMO (left)            │ EXPLORER (right)           │
  │ ┌──────────────────────────┐ │ (same tree; no step cursor │
  │ │ product pane             │ │  required)                 │
  │ │ When controls (any       │ │ Given already applied      │
  │ │ trigger)                 │ │ (Play background or load)  │
  │ └──────────────────────────┘ │                            │
  │                              │ [ Play mode ] (optional)   │
  └──────────────────────────────┴────────────────────────────┘
  Stories (~2): Create Character · Update Ability Rank
  Domain terms: Character · Ability · Rank
  key:
    chrome: same split as Play
    on product control trigger → BDD interactive when control
      it should run the when step fn bound by story_steps
      it should paint expose · not ThenFeedback · not playNext
      (visible: bind; no ! / «tint»)
=========

## Mode vs collect (Stories as is)

| | `create{Story}Story(mode)` + collect | StoryDemoControl Interaction (Interactive) |
|---|---|---|
| When | Declaring the story (list steps) | User triggers product control |
| What | Runner fills `steps[]` + expose | `whenStep.fn()` from `story_steps`, then bind |
| Who | PlayDualRunner (UX story-demo) | StoryDemoControl → scenario When (same fn as Play) |

Play next (explorer) always advances `steps[index]` — not “the bound control.”

## Where examples live

Product types and concrete factories: `sandbox/play-core-mechanics` / `sandbox/character`.
Domain / example outcomes stay in Create Character (etc.) story tests — page behaviors assert “shows snapshot,” not handbook ranks.
HTML page imports `story-test-core` only (not `node:test`).
Locks / connected notes: `contexts/cdd/.context/connected-contexts.md`
Invariants (prose): `ux-context.md` · Control model: `ux-model-sketch.md`

## log
- explore / Story Demo shell / Play dual runner / pass #lock-play-interactive
- explore / Story Demo shell / primary artifact / pass #primary-story-runner-sketch
- explore / Story Demo shell / UX submodule naming / pass #story-demo-ux-submodule-naming
- explore / Story Demo shell / play-dual-runner module / pass #impl-story-test-split
- explore / Story Demo shell / StoryDemoControl + data-story-steps / pass #impl-story-steps
- explore / Story Demo shell / collect returns story tree / pass #impl-collect-return
- explore / Story Demo shell / story-demo.html shell / pass #impl-story-demo-html-shell
- explore / Story Demo shell / ux_model StoryDemoControl + HTML attrs / pass #impl-ux-model-story-demo-control
- explore / Story Demo shell / mockup_shell + mount-generated-mockup / pass #impl-ux-generated-playable
- explore / Story Demo shell / browser-safe create{Story}Story / pass #impl-browser-story-exports
