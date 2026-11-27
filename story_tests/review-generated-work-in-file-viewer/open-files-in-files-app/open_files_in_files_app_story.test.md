---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Open Files In Files App

Map: [story-map.md](../../../.context/story-map.md#e-open-files-in-files-app). Acceptance tests: `harness/whiteboard/whiteboard_spec.py` and `space/session/practices/practice_session_output_spec.py` for what the session answers; `harness/files_app/app/files/file-bar.spec.ts`, `files-page.spec.ts` (Open Whiteboard In Files App) and `whiteboard-canvas.spec.ts` for what only the page shows. The other scenarios of this epic are in [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md).

### Domain terms

- whiteboard file: a `.whiteboard` file a practice renders its diagram to, such as `.context/story-map.whiteboard` (`harness/whiteboard/whiteboard.py` *Whiteboard*), which the page reads as Python reads it (`harness/whiteboard/whiteboard_file.py` *WhiteboardFile*, `whiteboard-file.show`).
- board: the Claude Whiteboard artifact the whiteboard file was published to. Its address is kept in the whiteboard file itself, as the file's `board` field (`Whiteboard.board_of`), which the render's publish step writes once it creates the board.

> The example ++another project++ is the Files app opened on a project other than the CDD checkout, its server started for the CDD checkout, as [review_files_in_files_app_story.test.md](../review-files-in-files-app/review_files_in_files_app_story.test.md#example-another-project) names it.

## Story: Open Whiteboard In Files App

Requested 2026-11-16, the person: "Same with whiteboard — if the diagram filter is on, we need a link to Claude whiteboard where we see a whiteboard file; whiteboard file entries don't open those files, they open the actual whiteboard."

Requested 2026-11-18 (Nov 18 demo fixes): "Whiteboard entry opens as an external link, not a canvas."

#### Scenario: Open a whiteboard's board in Claude

*Given* the session of ticket checkout-flow holds `.context/story-map.whiteboard`, and the file keeps its board's address
*And* the diagram chip ◇ is selected
*When* the file bar lists the Stories story map's files
*Then* the whiteboard is listed as story-map, marked as a whiteboard
*And* pressing it opens its board at its board's address, in Claude's artifact panel when a chat opened the page and in a browser tab when none did, never a drawing or the text of the file
*And* the board in Claude is a press away, at its board's address, opening in Claude's artifact panel

##### Example: another project

*Given* the Files app is opened on ++another project++, whose design-review session holds `design/.context/story-map.whiteboard`, and the file keeps its board's address
*And* the diagram chip ◇ is selected
*When* the file bar lists the Stories story map's files
*Then* the whiteboard is listed as story-map, marked as a whiteboard
*And* its board is at the address that project keeps, not one the CDD checkout keeps

#### Scenario: A whiteboard not on a board yet

*Given* `.context/story-map.whiteboard` was never published, so no address is kept for it
*When* the file bar lists it
*Then* it is listed as a whiteboard not on a board in Claude yet

#### Scenario: A board address that is no Claude address is never sent to the chat

*Given* `.context/story-map.whiteboard` keeps, as its board's address, text that is no address in Claude, such as another site, a script link, or an address followed by more lines, as a hand edit or a pulled branch can leave it
*When* the Person presses the whiteboard in the Files app opened from a chat
*Then* the chat is sent nothing, since the ask to open a board reaches it as the Person's own message
*And* the whiteboard is listed as not on a board in Claude yet

#### Scenario: Open the board from every session file

*Given* the board's address is kept for `.context/story-map.whiteboard`
*When* the Files app lists every file under the session's root
*Then* the whiteboard file is listed with its board's address, so it opens the board there too
