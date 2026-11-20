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

Observed for what the drawing holds (`cdd_guidance/practices/stories/thin_slice_render_spec.py`), for drawio and whiteboard. Intended for the saved name: `stories.md` declares `.context/thin-slice.drawio` and `.context/thin-slice.whiteboard` for the thin slice, and the name a render saves under is still the story map's; evidence still missing is `DeclaredOutputs.file_name_beside` naming the file declared beside the source (defects r3-sparky-01, widget-06).

*Given* ++.context/story-map.md++ holds the story map
  *And* `.context/thin-slice.md` holds two increments that name stories of the story map
*When* Claude Code renders `.context/thin-slice.md` to drawio at ++stories-story-map++
*Then* the drawing holds one lane for each increment, with the stories it delivers under their sub-epics
  *And* no heading of the thin slice is drawn as an epic
  *And* the saved file is `.context/thin-slice.drawio`
  *And* ++.context/story-map.drawio++ is as the person left it
