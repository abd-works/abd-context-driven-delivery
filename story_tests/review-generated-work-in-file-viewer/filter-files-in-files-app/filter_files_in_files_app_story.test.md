---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Filter Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-filter-files-in-files-app). Acceptance tests: `space/session/practices/practice_session_output_spec.py` and `space/kanban/kanban_tools_spec.py` for what the session answers; `harness/files_app/app/files/file-bar.spec.ts` for what only the page shows. The other scenarios of this epic are in [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md).

### Domain terms

- design canvas: a Claude Design canvas the UX mockup writes as files, one numbered version after another, under the UX root's `design-canvas/` folder (`design-canvas/version-N/project/canvas.json`); `design-canvas/versions.json` keeps the link each version was published at (`harness/design_canvas/versions.py` *CanvasVersions*).
- format group: the formats a filter chip stands for (`harness/markdown/format.py` `Format.GROUPS`): canvas is `claude_design`, drawn ▦.

> The example ++another project++ is the Files app opened on a project other than the CDD checkout, its server started for the CDD checkout, as [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md#example-another-project) names it.

## Story: Filter Files By Format In Files App

Requested 2026-11-16, the person: "Make sure design canvas is a filter option for UX, and that if selected a design canvas entry appears in the folder tree at the location where design canvas files / pointers live locally."

#### Scenario: Offer the canvas format while UX is on

*Given* the session of ticket checkout-flow has UX on and its Specification stage selected
*When* the Files app shows its format chips
*Then* the canvas chip ▦ is among them, standing for claude_design, because the UX mockup writes a design canvas

#### Scenario: Show a design canvas in its design-canvas folder

*Given* the UX root of checkout-flow holds `design-canvas/version-2/project/canvas.json`, published at its link in `design-canvas/versions.json`
*And* the canvas chip ▦ is selected
*When* the file bar shows its files in their folders
*Then* the design canvas is listed by the title it is published under, such as ux-mockup.version-2, in the `design-canvas` folder, beside `versions.json`, not three folders down in `version-2/project`
*And* pressing it opens the design canvas at its link in a tab of its own, not the text of `canvas.json`

##### Example: another project

*Given* the Files app is opened on ++another project++, whose design-review session holds `design/ux/design-canvas/version-1/project/canvas.json`, published at its link in `design/ux/design-canvas/versions.json`
*When* the file bar lists design-review's UX mockup and story map files
*Then* the design canvas is listed by the title it is published under, ux-mockup.version-1, marked as a design canvas
*And* pressing it opens the design canvas at the link that project keeps, not the text of `canvas.json`

#### Scenario: List the canvas a session folder or the root holds

*Given* the session's root holds a published design canvas the UX mockup does not name, such as one under a finished session's folder
*When* the Files app lists every file under the session's root
*Then* the canvas's `canvas.json` is listed with the link it is published at, so it opens as the design canvas there too

## Story: List Every File In Session Folders

Requested (the person, 2026-11-26): an "All files" scope button, placed before the file bar's ▤ and Δ scope buttons, that shows every file and folder in the session's folders, "everything that is there, not only the files the fidelities name or the changed ones".

#### Scenario: List every file in the session's folders

*Given* the session works in *board*, and Stories writes under *board/.context* and *story_tests/checkout*
*And* *board/notes.txt* is a file no fidelity declares
*When* the Person lists all files, pressing *All files*, the first of the scope buttons
*Then* the file bar lists every file under *board* and under *story_tests/checkout*, *notes.txt* among them (`session.all_files`)
*And* the stages, practices and formats selected leave none of them out

#### Scenario: List each file once when roots overlap

*Given* *board/.context* is a root inside *board*, the folder the session works in
*When* the Person lists all files
*Then* each file under *board/.context* is listed once

#### Scenario: Leave out what git ignores

*Given* *board/node_modules* is ignored by git
*When* the Person lists all files
*Then* no file under *board/node_modules* is listed

#### Scenario: List no file through a link

*Given* *board/link-in* is a link to *board/drafts*, and *board/link-out* a link to *outside*, outside every root
*When* the Person lists all files
*Then* each file in *board/drafts* is listed once, under *board/drafts*
*And* no file in *outside* is listed

#### Scenario: Leave out what a change to session.json leaves beside it

*Given* a *session.json* under the session's roots has its lock file beside it
*When* the Person lists all files
*Then* the lock file is not listed

#### Scenario: Keep listing when git's own folder is a root

*Given* an older session.json keeps *.git* as a root of a practice
*When* the Person lists all files
*Then* the files of the session's other roots are listed, and nothing from *.git*

#### Scenario: Go back to the selected files

*Given* the Person listed all files
*When* the Person presses ▤ All session files
*Then* the file bar lists again only the files the stages, practices and formats selected
