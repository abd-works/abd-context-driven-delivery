# A whiteboard's board link may be any text, and Open sends it to the chat as the person's own message

- **Title:** `render.record_board` keeps any `url` (a non-claude.ai site, `javascript:alert(1)`, text with a line break, empty) in the `.whiteboard` file, writes it outside the project too, and the Files app's Open on that board sends the link verbatim to the chat as the person's own message.
- **Charter:** C1 (board sends). **Tester:** Pip.
- **Story:** connect-chat-bar-board-and-story-ui; draw-practice-models-on-claude-whiteboard (publish then record the board). No scenario covers a link that is not a Claude board; `record_board`'s own doc says url is "the address of the Claude Whiteboard board the .whiteboard file at path was published to".
- **Module and class:** `cdd_guidance/actions/render/render.py` `Render.record_board` (no check of url, `files.path_named(path)` takes `../` and absolute paths); `harness/whiteboard/whiteboard.py` `Whiteboard.published_to` / `board_of`; `space/session/practices/practice_session_output.py` `publication_of` (link given as the file holds it); `harness/files_app/app/files/files-page.ts` `openPublished` (``Open the ${kind} ${name} (${path}) in the artifact panel: ${link}`` sent as `submit`, which the chat bar submits `asUser: true`).
- **Severity:** wrong result (and a way for a file's content to speak as the person in the chat).

## Steps

Sandbox project as in pip-1; `.context/story-map.whiteboard` a real whiteboard file (copied, `elements` present). Driver `scripts/r2.py`, `r3.py`:

1. `render.record_board(path=".context/story-map.whiteboard", url=U)` for U in `https://evil.example/x`, `javascript:alert(1)`, `"not a url at all\nsecond line"`, `""`.
2. `ticket.root_files(ticket="chips-ticket")` -> the entry's `link`.
3. `render.record_board(path="../outside.whiteboard", url="https://claude.ai/artifact/OUT")` with a whiteboard file one folder above the project.
4. (Reading, not run: no Files app started in this charter) Press Open on the board in the Files app with a chat linked.

## Expected

Only a Claude board address (`https://claude.ai/artifact/...` or `claude.ai/code/artifact/...`) on one line is kept; anything else is refused by name. The path is refused outside the project or the session's roots, as validate and the file tools refuse one. Open never puts text taken from a file into the person's own message unchecked.

## Actual

Every url is kept and answered back; `root_files` then gives `link: 'javascript:alert(1)'`, `link: 'not a url at all\nsecond line'`, `link: 'https://evil.example/x'`. Step 3 rewrote `sandbox/outside.whiteboard` (outside the project) with `"board": "https://claude.ai/artifact/OUT"`; an absolute path outside works the same. Since `openPublished` builds the chat message from `link`, a `.whiteboard` file whose `board` field holds a line break and further text (from `record_board`, a hand edit, or a pulled branch) is submitted to the chat as if the person typed it, every press another time once the turn ends.

## Tier that should catch it

Unit: `cdd_guidance/actions/render` spec for record_board refusals (url shape, path outside the project); `files-page.spec.ts` for an Open whose link is not a Claude address. Specs only record a good claude.ai link.
