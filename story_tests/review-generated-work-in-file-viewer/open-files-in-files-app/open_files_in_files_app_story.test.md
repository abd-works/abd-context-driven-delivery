---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Open Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-open-files-in-files-app). Acceptance tests: `harness/whiteboard/whiteboard_spec.py` and `space/session/practices/practice_session_output_spec.py` for what the session answers; `harness/files_app/app/files/file-bar.spec.ts` for what only the page shows. The other scenarios of this epic are in [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md).

### Domain terms

- whiteboard file: a `.whiteboard` file a practice renders its diagram to, such as `.context/story-map.whiteboard` (`harness/whiteboard/whiteboard.py` *Whiteboard*).
- board: the Claude Whiteboard artifact the whiteboard file was published to. Its address is kept beside the file, in the folder's `whiteboards.json`, by the file's name, as a design canvas keeps its links in `versions.json` (`harness/whiteboard/whiteboard.py` *BoardLinks*).

> The example ++another project++ is the Files app opened on a project other than the CDD checkout, its server started for the CDD checkout, as [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md#example-another-project) names it.

## Story: Open Whiteboard In Files App

Requested 2026-11-16, the person: "Same with whiteboard — if the diagram filter is on, we need a link to Claude whiteboard where we see a whiteboard file; whiteboard file entries don't open those files, they open the actual whiteboard."

Requested 2026-11-18 (Nov 18 demo fixes): "Whiteboard entry opens as an external link, not a canvas."

#### Scenario: Open a whiteboard file as a canvas

*Given* the session of ticket checkout-flow holds `.context/story-map.whiteboard`, and `.context/whiteboards.json` keeps its board's address
*And* the diagram chip ◇ is selected
*When* the file bar lists the Stories story map's files
*Then* the whiteboard is listed as story-map, marked as a whiteboard
*And* pressing it draws the board on a canvas beside the file list, its blocks, labels and arrows where the board places them, not the text of the file
*And* the board in Claude is a press away, at its board's address, opening in Claude's artifact panel

##### Example: another project

*Given* the Files app is opened on ++another project++, whose design-review session holds `design/.context/story-map.whiteboard`, and `design/.context/whiteboards.json` keeps its board's address
*And* the diagram chip ◇ is selected
*When* the file bar lists the Stories story map's files
*Then* the whiteboard is listed as story-map, marked as a whiteboard
*And* its board is at the address that project keeps, not one the CDD checkout keeps

#### Scenario: A whiteboard not on a board yet

*Given* `.context/story-map.whiteboard` was never published, so no address is kept for it
*When* the file bar lists it
*Then* it is listed as a whiteboard not on a board in Claude yet, and pressing it still draws it on a canvas, rather than showing the file's text

#### Scenario: Open the board from every session file

*Given* the board's address is kept for `.context/story-map.whiteboard`
*When* the Files app lists every file under the session's root
*Then* the whiteboard file is listed with its board's address, so it opens the board there too
