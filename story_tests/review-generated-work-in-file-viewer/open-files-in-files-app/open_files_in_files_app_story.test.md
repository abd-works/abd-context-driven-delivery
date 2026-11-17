---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Open Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-open-files-in-files-app). Acceptance tests: `harness/whiteboard/whiteboard_spec.py` and `space/session/practice_session_output_spec.py` for what the session answers; `harness/files_app/app/files/file-bar.spec.ts` for what only the page shows. The other scenarios of this epic are in [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md).

### Domain terms

- whiteboard file: a `.whiteboard` file a practice renders its diagram to, such as `.context/story-map.whiteboard` (`harness/whiteboard/whiteboard.py` *Whiteboard*).
- board: the Claude Whiteboard artifact the whiteboard file was published to. Its address is kept beside the file, in the folder's `whiteboards.json`, by the file's name, as a design canvas keeps its links in `versions.json` (`harness/whiteboard/whiteboard.py` *BoardLinks*).

## Story: Open Whiteboard In Files App

Requested 2026-11-16, the person: "Same with whiteboard — if the diagram filter is on, we need a link to Claude whiteboard where we see a whiteboard file; whiteboard file entries don't open those files, they open the actual whiteboard."

#### Scenario: Open a whiteboard file's board

*Given* the session of ticket checkout-flow holds `.context/story-map.whiteboard`, and `.context/whiteboards.json` keeps its board's address
*And* the diagram chip ◇ is selected
*When* the file bar lists the Stories story map's files
*Then* the whiteboard is listed as story-map, marked as a whiteboard, at its board's address
*And* pressing it opens the board in Claude in a tab of its own, not the text of the file

#### Scenario: A whiteboard not on a board yet

*Given* `.context/story-map.whiteboard` was never published, so no address is kept for it
*When* the file bar lists it
*Then* it is listed as a whiteboard with no board yet, and pressing it opens nothing, rather than the file's text

#### Scenario: Open the board from every session file

*Given* the board's address is kept for `.context/story-map.whiteboard`
*When* the Files app lists every file under the session's root
*Then* the whiteboard file is listed with its board's address, so it opens the board there too
