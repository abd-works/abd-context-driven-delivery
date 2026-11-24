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
- board: the Claude Whiteboard artifact the agent creates for the whiteboard file, through Claude's own Artifact tool, which CDD never sees. Its address is kept in the whiteboard file itself, as the file's `board` field (`Whiteboard.board_of`), never in the board's store.
- record board: the Render action's tool the agent calls with the whiteboard file and the board's address once the board is created (`render.record_board`).

## Story: Create Whiteboard Artifact For Fidelity File

Requested 2026-11-16, "Whiteboard entries open the board": a published board's address is recorded, so the Files app's whiteboard entries open the board instead of saying it is not published yet. Requested again 2026-11-24, "the goal is the claude artifact you must create the artifact when creating the whiteboard and add link it to the file": a whiteboard render is not finished until its board exists in Claude and the file holds the board's address.

#### Scenario: Rendering a whiteboard file never published finishes by creating its board

*Given* the session holds `.context/story-map.md`, and no `.context/story-map.whiteboard` yet
*When* the agent renders the story map to the whiteboard format
*Then* the render answers with no board and with `publish`, telling the agent the render is not finished until it creates a Whiteboard artifact titled after the file, writes the batches to its store, and calls record board with the file and the board's address
*And* a robot or sub-agent that cannot reach the Artifact tool reports the board as unpublished, naming the file

#### Scenario: Record the board a whiteboard file was published to

*Given* the session holds `.context/story-map.whiteboard`, and the file keeps no board address
*And* the agent rendered it and created a Whiteboard artifact in Claude titled after it
*When* the agent calls record board with the file and the board's address
*Then* `.context/story-map.whiteboard` keeps that address in its `board` field, and every element it held stays as it was
*And* the next Files app listing opens the board from the whiteboard entry

#### Scenario: A board published again keeps one address

*Given* `.context/story-map.whiteboard` already keeps a board address
*When* the agent records a new address for the same file
*Then* the file keeps only the new address, and the other whiteboard files in the folder keep theirs

#### Scenario: Rendering a published whiteboard file again keeps its board

*Given* `.context/story-map.whiteboard` keeps the address of its board in Claude
*When* the agent renders the story map to the whiteboard format again
*Then* the saved file still keeps that address, and the render answers with it as board and with only the changed elements to write to it

#### Scenario: A whiteboard file that cannot be read is left for a person to repair

*Given* `.context/story-map.whiteboard` holds text that is not a whiteboard file, such as a file cut off half way
*When* the agent records the board it was published to
*Then* the call is refused as an unreadable board
*And* the file keeps what it held

#### Scenario: Only a whiteboard file is published to a board

*Given* `.context/story-map.drawio`, which is not a whiteboard file
*When* the agent calls record board with it
*Then* the call is refused, saying only a `.whiteboard` file is published to a board, and nothing is kept

#### Scenario: Rendering to a whiteboard says how to publish it

*When* the agent renders a fidelity's file to the whiteboard format
*Then* the render tells it to publish the board as part of the render: create a Whiteboard artifact titled after the file when the file keeps no address, else write only the changed elements to the board it keeps
*And* to call record board with the file and the board's address after creating the board
