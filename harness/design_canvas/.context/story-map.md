---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Design Canvas

**Sources / context:** `harness/design_canvas/canvas.py`, `harness/design_canvas/look.py`, `harness/design_canvas/versions.py`, `harness/design_canvas/fixture_bar.py`, `harness/design_canvas/__init__.py`, `harness/design_canvas/design_canvas_spec.py`, `harness/design_canvas/versions_spec.py`; callers `cdd_guidance/practices/stories/model/claude_design/nodes.py`, `claude_design_story_model_spec.py`, `explorer.dc.html`, `claude_design.md`; `cdd_guidance/practices/stories/stories.md` ("Play the map in Claude Design"); `cdd_guidance/practices/ux/model/claude_design/claude_design.md`; `space/work_state.py` (`DESIGN_CANVAS_FOLDER`, `release_folder`).

**Evidence:** **Observed** means the code and specs do it today (name the file); **Inferred** means the code does it but no spec presses it; **Intended** means a source asks for it and the code does not do it yet (name the source).

---

# (E) Play The Product Story On A Design Canvas
## (E) Lay Out The Canvas Files
### (S) Design Canvas --> Place Pages On The Canvas

Observed: `DesignCanvas.add_page` lists each page in `canvas.json` in the order added, and the canvas launches on the first page (`design_canvas_spec.py`).

### (S) Design Canvas --> Place Artboards On Their Pages

Observed: `DesignCanvas.add_board` puts each artboard on its page and keeps the order they were added in `canvas.json` (`design_canvas_spec.py`).

### (S) Design Canvas --> Write The Canvas Into A Project Folder

Observed: `DesignCanvas.write` puts `canvas.json` and every artboard it was given text for under `project/` in the chosen folder, so the folder can be published as it is (`design_canvas_spec.py`).

### (S) Design Canvas --> Name An Imported Screen After Its File

Observed: `stem` and `camel` in `canvas.py` give a screen file's import name and its live flag in camel case, so the explorer can import the screen by name (`design_canvas_spec.py`).

### (S) Design Canvas --> Give Each Prototype Screen Its Own Page

Observed: `ClaudeDesignStoryModel.canvas` puts the story map, the story explorer, and each prototype screen on its own page (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Place A Read-Only Story Panel Beside A Screen

Observed: `_context_panel` in `nodes.py` draws a Stories board to the right of a screen, with the screen's own stories opened to their scenarios and steps and every other story greyed out (`claude_design_story_model_spec.py`).

## (E) Browse The Story Map Artboard
### (S) Design Canvas --> Draw The Whole Story Map On One Artboard

Observed: `_story_map` in `nodes.py` draws every epic, sub-epic, actor and story card on the single `Main.dc.html` artboard, one column per story (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Draw Each Epic Bar Across Its Sub-Epics

Observed: the story map draws each epic bar once, spanning all of its sub-epics (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Draw The Map In The abd Engineering Look

Observed: `LOOK` in `look.py` gives epics, sub-epics, actors and stories their dark cards and orange accent, and `box` in `canvas.py` draws them; the map has no white background (`claude_design_story_model_spec.py`).

### (S) Person --> Zoom The Story Map

Inferred: a zoomable `artboard` in `canvas.py` lets the person zoom the map with a trackpad pinch or ctrl + wheel and its − / % / + buttons, without shrinking the frame.

### (S) Design Canvas --> Show One Screen Thumbnail Under Each Story

Observed: `thumbnail` in `canvas.py` shows the story's main screen under its card, and a story with no screen gets no thumbnail (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Mark A Thumbnail With No Screenshot

Inferred: `thumbnail` in `canvas.py` shows "No screenshot" in place of the picture when the screen has no image.

### (S) Person --> Open The Story Explorer From A Thumbnail

Observed: only the thumbnails link, and each opens the story explorer at its story, scenario and step (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Keep A Clicked Link's Place For The Linked Artboard

Inferred: the zoomable artboard in `canvas.py` stores a clicked link's `#` part in local storage under `design-canvas.link:`, because the canvas opens a linked artboard without it, and the explorer reads it back (`explorer.dc.html`).

## (E) Navigate The Story Explorer Tree
### (S) Person --> Open The Explorer At A Story, Scenario And Step

Inferred: `explorer.dc.html` reads the story, scenario and step from the link, or from the place the map kept, and selects it in the tree.

### (S) Person --> Collapse And Reset The Story Tree

Inferred: the explorer's *Collapse all* and *Reset* buttons close the epic → sub-epic → story → scenario → step tree or return it to the first story (`explorer.dc.html`).

### (S) Person --> Play The Next Story

Inferred: the explorer's *Play next* button moves the selection to the next step or story (`explorer.dc.html`).

### (S) Person --> Hide And Show The Story Panel

Inferred: the » and « buttons hide the story panel so the screen fills the frame, and bring it back (`explorer.dc.html`).

### (S) Person --> Return To The Story Map

Inferred: the panel's **← Story map** link opens `Main.dc.html` again (`explorer.dc.html`).

### (S) Design Canvas --> Keep The Selected Story In View

Inferred: the explorer scrolls the selected entry into view when the selection changes (`explorer.dc.html`).

### (S) Person --> Copy A Request To Open A Story In Its File

Observed: the explorer carries each story's and scenario's `path:line` and offers to copy an open-in-file-viewer request for it (`claude_design_story_model_spec.py`, `copyOpenRequest` in `explorer.dc.html`).

### (S) Person --> Pick An Outline Scenario's Example

Intended (`claude_design.md` outline-rows): an outline scenario lists its examples from the fixtures bundle and picking one loads it on the screen; the explorer does not list them yet.

## (E) Show The Scenario's Screen In The Explorer
### (S) Design Canvas --> Display Live Scenario Screen In Explorer

Observed: `_imports` in `nodes.py` imports each prototype screen into the explorer with the story, scenario and a `go` call, so the selected scenario runs on the real screen (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Choose The Screen For A Step

Observed: a step shows the screen it is shown on, else its scenario's screen, else its story's screen (`_story_entry` and `_screen_of` in `nodes.py`, `claude_design_story_model_spec.py`).

### (S) Design Canvas --> Join A Step Without A Screen To The Next Step

Inferred: `_story_entry` in `nodes.py` groups a step with no screen of its own with the next step that has one, so every entry the person picks shows a screen.

### (S) Design Canvas --> Show A Screenshot When No Screen Runs

Inferred: when no prototype applies, the explorer shows the step's screenshot, skipping blank captures (`_blank` in `nodes.py`).

### (S) Design Canvas --> Keep Each Screen's Own Stylesheets

Inferred: `_stylesheets` in `nodes.py` links every stylesheet the prototype screens use, so a screen drawn inside the explorer keeps its own look.

## (E) Load Scenario Fixtures With The Fixture Bar
### (S) Person --> Load A Scenario Into A Standalone Screen

Inferred: opened on its own, a screen's fixture bar starts on *Load a scenario…* and loads nothing until the person picks a scenario, which loads its fixture and types the values it enters (`fixture_bar.py` `loadFromFixture`).

### (S) Design Canvas --> Load The Explorer's Scenario Into The Screen

Inferred: inside the explorer the screen loads the explorer's scenario as soon as the fixtures bundle is there, and again whenever the explorer moves (`fixture_bar.py` `followExplorer`).

### (S) Person --> Pick Another Scenario From Inside The Explorer

Inferred: picking a scenario on the bar inside the explorer loads it and moves the explorer's tree to it (`fixture_bar.py` `pickScenario`).

### (S) Person --> Paste Dev Seed Data Into A Screen

Inferred: the bar lists dev mode's seed paste for the screen's path, and picking it types each pasted field into the screen (`fixture_bar.py` `pasteSeedData`).

### (S) Person --> Follow A Screen Link To The Next Story

Inferred: a link to the next screen moves the explorer to that story, or opens the next screen when the screen stands alone (`fixture_bar.py` `follow`).

### (S) Person --> Edit A Screen On Its Own Artboard

Inferred: inside the explorer the bar ends with **Edit**, a link to the screen's own artboard, because an edit inside the explorer would change the explorer (`fixture_bar.py` `bar`).

### (S) Design Canvas --> Report Where The Screen's Data Came From

Inferred: the bar's values carry the loaded story and scenario, the pasted seed, or the loading problem (`fixture_bar.py` `barVals`).

## (E) Start A Canvas Version
### (S) Agent --> Start The First Version

Observed: `CanvasVersions.start_next` begins at `version-1` when there are no versions yet (`versions_spec.py`).

### (S) Agent --> Start The Next Version As A Copy

Observed: `start_next` copies the latest version into the next one and leaves the version people edited as it was (`versions_spec.py`).

### (S) Agent --> Write Into The Version Not Yet Published

Observed: `working` keeps returning the latest version while it has no published link, and starts the next one once it does (`versions_spec.py`).

### (S) Agent --> Refuse To Add To A Published Version

Observed: `unpublished` raises `PublishedVersion` when the latest version is already published, so a screen generator never writes over people's edits (`versions_spec.py`).

## (E) Publish And Release A Canvas Version
### (S) Agent --> Title A Published Canvas By Its Version

Observed: `CanvasVersions.title` names the canvas `<name> — version-N` (`versions_spec.py`).

### (S) Agent --> Record Each Version's Published Link

Observed: `record_link` keeps each version's canvas link in `versions.json`, in the order published (`versions_spec.py`).

### (S) Agent --> Keep A Published Version As A Release

Observed: `release` renames the version's folder and its link to the release's name (`versions_spec.py`).

### (S) Agent --> Remove Older Versions When Keeping A Release

Intended (`claude_design.md` release-a-version): when a version is kept as a release the older versions are removed; `release` in `versions.py` only renames.

### (S) Agent --> Start Numbering Again From A Release

Observed: once no numbered version is left, `start_next` starts `version-1` as a copy of the latest release (`versions_spec.py`).

### (S) Agent --> Find A Release's Canvas Folder

Observed: `CanvasVersions.from_release` opens `.sessions/<release>/design-canvas`, for the release being worked on or a named one (`versions_spec.py`).

---

## Scope boundary

**In scope:** the canvas files (`canvas.json`, pages, artboards), the story map artboard with its look, zoom and thumbnails, the story explorer and the read-only story panel as the canvas shows them, the fixture bar every prototype screen shares, and numbered canvas versions and releases in the release's session folder.

**Out of scope:** reading the story map drawio and the UX map into the graph, building the pattern's fixtures bundle (`CanvasFixtures`), porting product screens to artboards, laying out the Screens page boards (`ux/model/claude_design`), and publishing a version to Claude Design.
