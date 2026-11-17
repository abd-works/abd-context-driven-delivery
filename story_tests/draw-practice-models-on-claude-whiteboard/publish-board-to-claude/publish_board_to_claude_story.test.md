---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Publish Board To Claude

Map: [story-map.md](../../../.context/story-map.md#e-publish-board-to-claude). Acceptance tests: `cdd_guidance/actions/render/render_spec.py` for what the Render action records and tells the agent, `harness/whiteboard/whiteboard_spec.py` for where the address is kept. The Files app opening the board is in [open_files_in_files_app_story.test.md](../../review-generated-work-in-file-viewer/open-files-in-files-app/open_files_in_files_app_story.test.md).

### Domain terms

- whiteboard file: a `.whiteboard` file a practice renders its diagram to, such as `.context/story-map.whiteboard` (`harness/whiteboard/whiteboard.py` *Whiteboard*).
- board: the Claude Whiteboard artifact the agent publishes the whiteboard file to, through Claude's own Artifact tool, which CDD never sees. Its address is kept beside the file, in the folder's `whiteboards.json`, by the file's name (*BoardLinks*).
- record board: the Render action's tool the agent calls with the whiteboard file and the board's address once the board is published (`render.record_board`).

## Story: Create Whiteboard Artifact For Fidelity File

Requested 2026-11-16, "Whiteboard entries open the board": a published board's address is recorded, so the Files app's whiteboard entries open the board instead of saying it is not published yet.

#### Scenario: Record the board a whiteboard file was published to

*Given* the session holds `.context/story-map.whiteboard`, and no board address is kept for it
*And* the agent rendered it and created a Whiteboard artifact in Claude titled after it
*When* the agent calls record board with the file and the board's address
*Then* `.context/whiteboards.json` keeps that address under story-map.whiteboard
*And* the next Files app listing opens the board from the whiteboard entry

#### Scenario: A board published again keeps one address

*Given* `.context/story-map.whiteboard` already has a board address kept for it
*When* the agent records a new address for the same file
*Then* the file keeps only the new address, and the other files' addresses in the folder stay as they were

#### Scenario: Only a whiteboard file is published to a board

*Given* `.context/story-map.drawio`, which is not a whiteboard file
*When* the agent calls record board with it
*Then* the call is refused, saying only a `.whiteboard` file is published to a board, and nothing is kept

#### Scenario: Rendering to a whiteboard says how to publish it

*When* the agent renders a fidelity's file to the whiteboard format
*Then* the render tells it to publish the board: create a Whiteboard artifact titled after the file when no address is kept, else write only the changed elements to the board kept for it
*And* to call record board with the file and the board's address after creating the board
