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

## Triage

- **Status:** confirmed. `Render().record_board` kept `https://evil.example/x`, `javascript:alert(1)`, a two-line text and `""` in the file's `board` field; through a session's cdd server it wrote `../<name>.whiteboard` outside the project; `publishedOf` in the Files app took any link and `openPublished` sent it to the chat as a `submit`.
- **Severity:** wrong result (and a way for a file's text to speak as the person in the chat).
- **Triaged by:** Relay.
- **What a board link may be (from the render action's guidance):** `publish_board` has the agent create the board with Claude's Artifact tool and record "the board's address"; `answer_board_comment` calls it "the claude.ai artifact link"; the Artifact tool's addresses are `claude.ai/artifact/{id}` and `claude.ai/code/artifact/{uuid}`. So `record_board` keeps exactly `https://claude.ai/artifact/<id>` or `https://claude.ai/code/artifact/<id>`, alone. The Files app also opens design canvases, whose links come from `versions.json`, so the page keeps any `https://claude.ai/...` address on one line and nothing else.

## Fix

- **Scenarios:** "Only a board's address in Claude is recorded" and "A whiteboard file outside the project is not recorded" in `story_tests/draw-practice-models-on-claude-whiteboard/publish-board-to-claude/publish_board_to_claude_story.test.md`; "A board address that is no Claude address is never sent to the chat" in `story_tests/review-generated-work-in-file-viewer/open-files-in-files-app/open_files_in_files_app_story.test.md`.
- **Tests:** `cdd_guidance/actions/render/render_spec.py` (unit): a `claude.ai/code/artifact/` address is kept; another site, a script link, an address followed by more lines and an empty address are refused (*BoardAddressRefused*, naming the text) and no address is kept. `cdd_guidance/actions/render/render_record_board_heavy_spec.py` (heavy, real cdd server and session): a whiteboard file outside the project is refused and keeps no address. `harness/files_app/app/files/files-page.spec.ts` (unit): a board link that is another site, a script link, or an address followed by more lines is sent to no chat. Each seen failing first.
- **Fix:** `cdd_guidance/actions/render/render.py`: `record_board` reads its path through the action's files (`files.paths_to_read`, which refuses one outside the session's roots, as render's own paths are) and keeps the url only through `BoardAddressRefused.check`. `harness/files_app/app/files/file-bar.ts`: `publishedOf` keeps a published file's link only when it is a `https://claude.ai/` address on one line, so `openPublished`, the press, and the view's `href` and browser fallback never use anything else; such a file reads as not published yet.
- **Commit:** f241d5596.
