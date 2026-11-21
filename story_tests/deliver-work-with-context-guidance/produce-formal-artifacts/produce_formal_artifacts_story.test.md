---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Produce Formal Artifacts

Story map: [Produce Formal Artifacts](../../../.context/story-map.md#e-produce-formal-artifacts). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the Generate and Render actions today (`cdd_guidance/actions/generate`, `cdd_guidance/actions/render`, `harness/guidance_actions/guidance_actions.py`). They were written after exploratory testing round 1 (defects widget-01, 02, 06, 07, 09) showed the behaviour had no scenario.

### Domain terms

- ++slug++ — the word a call names a practice or a fidelity by, such as `stories` or `stories-story-map` (`PracticeSet.slugs`).
- ++guidance mapping++ — guidance sent as `{toolset, fidelity}`; its toolset names the practice by slug or by a `module:Class` ref (`GuidanceArgument`).
- ++saved file++ — the file a render to drawio, whiteboard or markdown saves beside its source (`RenderedFile`).
- ++session's root++ — the folder the session works in; a path a call names is read under it (`SessionFiles.from_root`).

> In steps: the bookshop project and its files are the examples below.

## Examples

### guidance a call names

| guidance | read as |
| --- | --- |
| ++stories-story-map++ | the story map fidelity of Stories |
| ++stories_story_map++ | no slug: underscores where the slug has hyphens |
| ++wibble-wobble++ | no slug |
| ++write the story map++ | prose, run once as text |
| ++{toolset: stories, fidelity: story_map}++ | the story map fidelity of Stories |
| ++{foo: bar}++ | a mapping that names no toolset |

### files of the bookshop project

| file | holds |
| --- | --- |
| ++.context/story-map.md++ | the story map: Sell Books, Take Orders, Place Order |
| ++.context/story-map.drawio++ | the story map's drawing, with Place Order moved by a person |
| ++.context/story-map.whiteboard++ | the story map's whiteboard |
| ++.context/returns.md++ | another story map: Manage Returns, Accept Return, Return Damaged Book |
| ++.context/empty.md++ | nothing |
| ++../outside/story-map.md++ | a story map in a folder beside the project |

## Story: Generate Fidelity Artifact

### Evidence

| Source | Note |
|--------|------|
| `harness/guidance_actions/guidance_actions.py` `GUIDANCE_PARAMETER` | "Any other string is text this action runs once" |
| `harness/guidance_actions/guidance_actions.py` `UnknownGuidance` | a listed word that is no slug is refused, listing the slugs there are |
| Defects widget-01, widget-02 | a misspelt slug sent alone ran as text with no rules; a mapping whose toolset was a slug was refused as an unknown slug |

#### Scenario: Refuse a misspelt slug sent alone

Observed.

*Given* the bookshop session works on Stories
*When* Claude Code generates with guidance ++stories_story_map++
*Then* the call is refused, saying no practice or fidelity has the slug ++stories_story_map++
  *And* the refusal lists ++stories-story-map++ among the slugs there are

#### Scenario: Run prose once as text

Observed.

*Given* the bookshop session works on Stories
*When* Claude Code generates with guidance ++write the story map++
*Then* the answer holds ++write the story map++

#### Scenario: Work on the practice a mapping names by its slug

Observed.

*Given* the bookshop session works on Stories
*When* Claude Code generates with the guidance mapping ++{toolset: stories, fidelity: story_map}++
*Then* the answer holds the rules of ++stories-story-map++

#### Scenario: Refuse a mapping that names no toolset

Observed.

*Given* the bookshop session works on Stories
*When* Claude Code generates with the guidance mapping ++{foo: bar}++
*Then* ++{foo: bar}++ is refused, saying a mapping names its practice in toolset
  *And* the refusal lists ++stories-story-map++ among the slugs there are

## Story: Render Artifact Into Another Format

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/actions/render/render.py` `Render.render` | a render of paths "is saved beside the first path ... keeping the layout people gave a drawing already there" |
| `cdd_guidance/actions/validate/validate.py` `Validate.validate` | "A path that is not there, or not under the session's root, is refused" |
| Defects widget-06, widget-07, widget-09 | any markdown file's render replaced story-map.drawio; a path outside the project was rendered and saved there; a whiteboard file with no source failed with a traceback |

#### Scenario: Save another file's drawing under that file's own name

Observed.

*Given* ++.context/story-map.drawio++ holds the story map's drawing, with Place Order moved by a person
  *And* ++.context/returns.md++ holds another story map
*When* Claude Code renders ++.context/returns.md++ to drawio at ++stories-story-map++
*Then* the saved file is .context/returns.drawio, which draws Return Damaged Book
  *And* ++.context/story-map.drawio++ is as the person left it

#### Scenario: Refuse to render an empty file

Observed.

*Given* ++.context/story-map.drawio++ holds the story map's drawing
  *And* ++.context/empty.md++ holds nothing
*When* Claude Code renders ++.context/empty.md++ to drawio at ++stories-story-map++
*Then* the call is refused, naming ++.context/empty.md++ as empty
  *And* ++.context/story-map.drawio++ is as it was

#### Scenario: Refuse a path outside the session's root

Observed.

*Given* ++../outside/story-map.md++ holds a story map in a folder beside the project
*When* Claude Code renders ++../outside/story-map.md++ to drawio at ++stories-story-map++
*Then* ++../outside/story-map.md++ is refused as not under the session's root
  *And* no drawing is saved beside ++../outside/story-map.md++

#### Scenario: Read a file's format from its name when no source is named

Observed.

*Given* ++.context/story-map.whiteboard++ holds the story map's whiteboard
*When* Claude Code renders ++.context/story-map.whiteboard++ to drawio at ++stories-story-map++, naming no source
*Then* the saved file is ++.context/story-map.drawio++, which draws Place Order

#### Scenario: Draw a thin slice as its increments

Observed for what the drawing holds (`cdd_guidance/practices/stories/thin_slice_render_spec.py`), for drawio and whiteboard. Observed for the saved name (`harness/guidance/declared_outputs_spec.py`, `cdd_guidance/actions/render/render_saves_beside_source_heavy_spec.py`): `stories.md` declares `.context/thin-slice.drawio` and `.context/thin-slice.whiteboard` for the thin slice, and a file declared in an output named for what it holds is saved as the file that same output declares in the format (defects r3-sparky-01, widget-06).

*Given* ++.context/story-map.md++ holds the story map
  *And* `.context/thin-slice.md` holds two increments that name stories of the story map
*When* Claude Code renders `.context/thin-slice.md` to drawio at ++stories-story-map++
*Then* the drawing holds one lane for each increment, with the stories it delivers under their sub-epics
  *And* no heading of the thin slice is drawn as an epic
  *And* the saved file is `.context/thin-slice.drawio`
  *And* ++.context/story-map.drawio++ is as the person left it

#### Scenario: Save one drawing of every module where the modules fidelity declares it

Observed (`cdd_guidance/actions/render/render_spec.py`, `render_saves_beside_source_heavy_spec.py`). Written after exploratory testing round 3 (defect r3-widget-01): the drawing of all the modules was saved in the first module's own `.context` folder. `clean_engineering.md` declares `.context/modules.drawio` for the modules fidelity.

*Given* `src/catalogue/.context/module-context.md` and `src/ordering/.context/module-context.md` each hold a module card
*When* Claude Code renders both cards to drawio at ++clean-engineering-modules++
*Then* the saved file is `.context/modules.drawio` in the project's root, which draws both modules
  *And* no drawing is saved in `src/catalogue/.context`

#### Scenario: Read a markdown file as markdown at a fidelity that works in code

Observed (`cdd_guidance/actions/render/render_spec.py`, `render_saves_beside_source_heavy_spec.py`). Written after exploratory testing round 3 (defects r3-widget-05, widget-09): a `.md` path with no source named was read in the fidelity's own format, Python, and refused as Python that does not parse. Render's description says to omit source "for a file whose extension says its format".

*Given* `src/ordering/.context/ordering-model.md` holds a class model with the class Cart
*When* Claude Code renders `src/ordering/.context/ordering-model.md` to drawio at ++clean-engineering-model++, naming no source
*Then* the saved file is `src/ordering/.context/ordering-model.drawio`, which draws Cart

#### Scenario: Answer a render that saves nothing with its content and where the fidelity declares it

Observed (`cdd_guidance/actions/render/render_spec.py`). Written after exploratory testing round 3 (defects r3-bolt-06, r3-sparky-07, r3-rivet-08): a render to code answered one text with no word of where it goes, and a realization rendered from a saved graph was saved as `graph.md` beside the graph. Render's description says a render other than drawio, whiteboard or markdown "returns its content"; whether a render to code should save one file for each aggregate or story itself waits for the person's decision.

*Given* `.context/domain-model.md` holds a domain model
*When* Claude Code renders `.context/domain-model.md` to python at ++ddd-model++
*Then* the answer holds the code and names no saved file
  *And* the answer names `{bounded_context}/{aggregate}/{aggregate}.py` as where the fidelity declares its Python

#### Scenario: Leave a realization rendered from a saved graph for the agent to name

Observed (`cdd_guidance/actions/render/render_spec.py`). Written after exploratory testing round 3 (defect r3-rivet-08). `bdd.md` tells the agent to write the result to `.context/{scope}-bdd-realization.md`, and only the agent knows the scope.

*Given* `graphs/graph.json` holds a saved graph
*When* Claude Code renders `graphs/graph.json` to markdown at ++bdd-realization++ with source graph
*Then* the answer holds the realization and names `.context/{scope}-bdd-realization.md` as where the fidelity declares it
  *And* no `graph.md` is saved beside `graphs/graph.json`

#### Scenario Outline: Save a story test for each story where the fidelity declares it

Observed (`cdd_guidance/practices/stories/stories_render_saves_heavy_spec.py`, `cdd_guidance/practices/stories/model/code_story_behaviours_spec.py`). Written after exploratory testing round 3 (defect r3-sparky-07): every Stories render to code in a session was refused, because the story formats named their files `tests/{epic}/{sub_epic}_story.test` while the fidelities declare one file for each story under `story_tests`.

*Given* the Pack Orders project holds the stories Pack Order and Cancel Order as markdown scenarios under the sub-epic Pack Orders
*When* Claude Code renders `story_tests` to <format> at <fidelity>
*Then* render saves `pack_order_story.test` and `cancel_order_story.test`, each in a folder of the story's own under `story_tests/fulfil-order/pack-orders`
  *And* a render to TypeScript or JavaScript saves the step library at `story_tests`
  *And* the result names the saved files and answers no code

| format | fidelity |
| --- | --- |
| python | stories-scenarios |
| typescript | stories-acceptance-tests |
| javascript | stories-acceptance-tests |

#### Scenario: Import the step library by the path from the folder a JavaScript story test is saved in

Observed (`stories_render_saves_heavy_spec.py`, `cdd_guidance/practices/stories/model/javascript/javascript_story_model_spec.py`).

*Given* the Pack Orders project holds the story Pack Order as markdown scenarios
*When* Claude Code renders `story_tests` to javascript at ++stories-acceptance-tests++
*Then* `pack-order/pack_order_story.test.js` imports the step library from `../../../story-test.js`

#### Scenario: Write a story test only for the stories the named file holds

Observed (`stories_render_saves_heavy_spec.py`, `cdd_guidance/practices/stories/scenarios_code_render_spec.py`). Written after defect r3-sparky-07: a render of one shared story file wrote a story test for every story of the map.

*Given* the Pack Orders project holds its story tests in TypeScript, the story Cancel Order in `pack-orders.story.shared.ts`
*When* Claude Code renders `pack-orders.story.shared.ts` to python at ++stories-acceptance-tests++
*Then* render saves `cancel-order/cancel_order_story.test.py`
  *But* no story test for Pack Order, which that file does not hold

#### Scenario: Save a scenarios file for each story of a folder of story tests

Observed (`stories_render_saves_heavy_spec.py`, `scenarios_code_render_spec.py`). Before, a render of a folder of story tests to markdown made one text no declared path could place, and was refused.

*Given* the Pack Orders project holds its story tests in TypeScript
*When* Claude Code renders `story_tests` to markdown at ++stories-scenarios++
*Then* render saves `pack_order_story.test.md` and `cancel_order_story.test.md` in `story_tests/fulfil-order/pack-orders`, as the scenarios fidelity declares them
