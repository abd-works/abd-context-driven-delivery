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

#### Scenario: Save a class model drawn from code under the name the model fidelity writes markdown to

Observed (`cdd_guidance/actions/render/render_spec.py`, `harness/guidance/declared_outputs_spec.py`). Written after exploratory testing (defect widget-15): a class model rendered from code to markdown was saved beside the code under the code's own name, `src/order.md`. `clean_engineering.md` declares `{module}/` for the model's code and `{module}/.context/{module}-model.md` for its markdown; the module is the folder holding the code.

*Given* `src/ordering/cart.ts` holds the class Cart, in the module folder `src/ordering`
*When* Claude Code renders `src/ordering/cart.ts` to markdown at ++clean-engineering-model++
*Then* the saved file is `src/ordering/.context/ordering-model.md`, which holds Cart
  *And* no `src/ordering/cart.md` is saved beside the code

#### Scenario: Refuse a fidelity that declares no file in the format rendered to

Observed (`cdd_guidance/actions/render/render_spec.py`). Written after exploratory testing (defect widget-16): one render of ++.context/story-map.md++ to drawio at the story map and the scenarios wrote the scenarios' drawing over the story map's, though `stories.md` declares no drawing for the scenarios. Each fidelity saves under its own declared name for a format.

*Given* ++.context/story-map.md++ holds the story map
*When* Claude Code renders ++.context/story-map.md++ to drawio at ++stories-story-map++ and ++stories-scenarios++ in one call
*Then* the call is refused, naming ++stories-scenarios++ and drawio as a format it declares no file for
  *And* no drawing is saved for either fidelity

#### Scenario: Refuse to render a finished spec to a format that holds no test body

Observed (`cdd_guidance/actions/render/render_spec.py`, `cdd_guidance/practices/bdd/model/spec_trip_spec.py`). Written after exploratory testing round 3 (defect r3-rivet-11): a finished Mamba spec rendered to markdown and back came back as signatures, its imports, setup and test bodies gone, and nothing said so. A describe tree in markdown or a sketch holds names only.

*Given* `src/cart_spec.py` is a finished spec whose test should total its lines asserts the cart's total
*When* Claude Code renders `src/cart_spec.py` to markdown at ++bdd-realization++
*Then* the call is refused, naming should total its lines as a test whose body would be lost
  *And* `src/cart_spec.py` is as it was

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

Observed (`stories_render_saves_heavy_spec.py`, `cdd_guidance/practices/stories/model/javascript/javascript_story_map_spec.py`).

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

#### Scenario Outline: Write changed scenarios onto a story test already there, losing nothing

Observed (`cdd_guidance/practices/stories/model/reshaped_story_file_spec.py`, run for Python, TypeScript and JavaScript; `cdd_guidance/practices/stories/stories_render_saves_heavy_spec.py` through the Render action). The person's answer of 2026-11-21: "render should match files to the new shape, but existing code, comments, whatever exists only in one shape must be preserved".

*Given* the Pack Order story test holds code in each step, and a comment and a helper between its two scenarios
  *And* the scenarios of Pack Order now have <change>
*When* Claude Code renders the scenarios to the story test's language
*Then* every line the story test held is still in it, the comment and the helper where they were
  *And* <what the story test gains>
  *And* the result names <what to migrate>

| change | what the story test gains | what to migrate |
| --- | --- | --- |
| a step more | the step in its scenario, with no code yet | the step as added |
| a step fewer | a line above the step saying it is no longer in the model | the step as kept |
| a step under new words | the step under its new words with no code yet, and the line above the step under its old words | one step kept and one added |
| a scenario more | the scenario after the scenarios the story had, its steps with no code yet | the scenario as added |

#### Scenario: Change nothing when the same scenarios are rendered onto a story test again

Observed (`reshaped_story_file_spec.py`).

*Given* the scenarios of Pack Order were rendered onto its story test, which gained a step and a marking line
*When* Claude Code renders the same scenarios onto the story test again
*Then* the story test is as the first render left it

#### Scenario: Leave a step library a person changed as it is

Observed (`reshaped_story_file_spec.py`). Before, a render onto a project's own `story-test.ts` wrote the seeded step library and set the 68 lines only the project's file held apart as comments.

*Given* a project's `story-test.ts` holds helpers the seeded step library does not
*When* Claude Code renders scenarios to typescript in that project
*Then* `story-test.ts` is as it was

#### Scenario Outline: Hand what the source no longer holds to the agent to decide

Observed (`render_result_spec.py`, `kept_document_spec.py`, `render_spec.py`; Align in `format_alignment_heavy_spec.py`). The person's ruling of 2026-11-22: no rule tells what a render drew from what a person added, in any format; what the source no longer holds goes to an AI pass that decides by reading both. Their example: an operation removed from a class in the class model's markdown, rendered onto code that already implements it, may have been merged into another operation or may be no longer needed, and only an agent reading both can tell.

*Given* <file> holds <leftover>, which <source> no longer holds
*When* Claude Code renders <source> onto <file>
*Then* <file> still holds <leftover> where it was
  *And* the result lists <leftover> as migrate, with <file> and what the render added that may have replaced it
  *And* the result tells the agent to decide each entry by reading it against what <source> now holds: moved somewhere, so move it there and take the leftover out; merged into something else, so fold it in and take the leftover out; no longer needed, so remove it; or still wanted with the source behind, so put it back in the source
  *But* who added or removed <leftover> plays no part, the agent asks the person where reading does not tell, and <leftover> stays where it is until it is decided

| source | file | leftover |
| --- | --- | --- |
| the class model's markdown, without `Cart.total` | `ordering.py` | `Cart.total` and the code that implements it |
| ++.context/story-map.md++ | ++.context/story-map.drawio++ | a note on the drawing |
| ++.context/story-map.md++ | ++.context/story-map.whiteboard++ | a note on the board |
| the domain model drawn as a drawing | its markdown | a section the drawing does not hold |

#### Scenario: Leave a story the drawing still holds out of the markdown it was removed from, for the agent to decide

Observed (`format_alignment_heavy_spec.py`). Before, Align rendered the markdown from the drawing and the removed story was back in the markdown with no decision made.

*Given* Change Cart Line Quantity was removed from ++.context/story-map.md++ alone, and ++.context/story-map.drawio++ still draws it
*When* the person aligns the session's formats
*Then* ++.context/story-map.md++ is as it was
  *And* the diagnosis names the story the drawing still holds and tells the agent to decide it by reading it against the story map
