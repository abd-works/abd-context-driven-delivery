# Validate — stories-acceptance-tests, clean-engineering-code

Guidance: stories-acceptance-tests, clean-engineering-code, with overlays cdd_web_domain_access and lern_domain_driven.
Session: review-work-in-board-files. The validate call saved no report of its own, so this judgment is written here.

Paths judged:
- space/kanban/review-files-in-viewer.story.shared.py, .story.domain.spec.py, .story.server.spec.py
- space/kanban/review-fidelity-outputs.story.shared.py
- space/kanban/session_board_examples.py, space/kanban/session_board_tiers.py
- space/session/file_comments.py, file_manager.py, session_files.py, practice_session_output.py, session.py
- harness/chat/chat.py

Runs: review-files-in-viewer domain 21 / server 8 pass; review-fidelity-outputs domain 7 / server 4 pass; kanban_tools_spec 116 pass; space/session and harness/chat quick specs 284 pass.

Fixed during this run (a regression, not a judgment): `Session.file_comments` was declared `-> FileComments` with FileComments imported at run time, so the harness re-hosted FileComments' tools under Session (`session.add`, `session.send`, `session.on`, …), which collides with `session.send` if it is ever added. The import now sits under `TYPE_CHECKING`, imported lazily in the property, and kanban_tools_spec expects `session.write_file`, `is_changed` and `language`.

## Judgment — `space/kanban/review-files-in-viewer.story.shared.py`

### `domain-operations-inline-in-steps` — Fail
- review-files-in-viewer.story.shared.py:49 `comments_of` wraps `Ticket.load(...).session.file_comments`, so a step reads `comments_of(world).send(...)` instead of showing the domain path it runs.
- review-files-in-viewer.story.shared.py:53 `add_comment` wraps `FileComments.add`, the operation several Givens rely on; the rule wants the call inline in the step.
- review-files-in-viewer.story.shared.py:43 `seed_checkout_flow`, `seed_connected_chat` and `seed_comment_shown_in_chat` (lines 61, 73) are seed fixtures kept in the story file; the rule puts `seed…` fixtures in the examples file (`session_board_examples.py`).

### `given-only-what-the-system-checks` — Fail
- review-files-in-viewer.story.shared.py:283 "Keep the comment unsent when the chat is not connected": the Given "ticket checkout-flow is assigned the chat checkout-chat" also adds the empty-cart comment, a state its text does not name.

## Judgment — `space/session/file_comments.py`

### `standard-mutation-response` — Fail
- file_comments.py:162 `add` returns `FileComment` while `remove` (171), `send_open` (186) and `clear_processed` (196) return `FileComments`; `send` (179) returns `FileComment`. Mutations on one aggregate should answer in one shape (lern_domain_driven).

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md`

### `playwright-tests-browser-interaction` — Fail
- review_fidelity_outputs_on_board_story.test.md:26 The changed-files filter (and its clear, line 36) is a screen interaction with no Playwright test; the Python tiers only prove `is_changed`.
- review_fidelity_outputs_on_board_story.test.md:52 Browse Ticket Files By Practice (filters, colored tabs, preset, select tab) has no test in any tier.
- review_fidelity_outputs_on_board_story.test.md:83 View Fidelity Files' tab colors have no test.
- review_fidelity_outputs_on_board_story.test.md:97 Opening the session folder from the session button has no screen test; the server tier only proves `Session.folder_files`.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md`

### `playwright-tests-browser-interaction` — Fail
- review_files_in_viewer_story.test.md:51 Rendering markdown as a page is a screen outcome; the Python tier proves only `language: markdown`.
- review_files_in_viewer_story.test.md:156 Show Changed File In Viewer: the viewer refreshing when a comment turns processed has no screen test.

## Judgment — `harness/.context/stories/story-map.md`

### `do-not-invent-requirements` — Fail
- story-map.md:591 `Show AI Changes As Diff` is in this session's increment but has no scenarios and no acceptance test, so nothing in this fidelity covers it.
- story-map.md:553 `List Ticket Context Files` is the ticket's name for the story whose scenarios and tests say `List Ticket Files`; one of the two names is wrong.

## Passes

stories-acceptance-tests: examples-declare-seed-vs-interaction, shared-example-fixtures, seed-state-at-its-real-owner, separate-test-controls-from-production-contracts, system-stubs-domain-real (real Chat queue in a throwaway `CDD_CHATS_FOLDER`), assert-domain-behavior-not-seeded-state, infrastructure-in-lifecycle-hooks, extract-assertion-helper.
cdd_web_domain_access: domain-lives-in-python, state-lives-behind-the-tool (comment state is read from the chat message, never stored), one-line-to-the-domain, tool-matches-the-object (`file-comments.*`, `chat.*`), tool-stays-thin, annotate-what-typescript-reads, read-files-through-the-file-manager (`FileManager.write`), fail-loud-on-mcp (ChatNotConnectedError, FileCommentNotFoundError), act-on-a-throwaway-project.
lern_domain_driven: reduce-story-overlap, shared-behavior-stays-tier-free, tier-runs-shared-behavior, server-tier-calls-the-real-thing, no-expect-in-given.
Noise (covered by cdd_web_domain_access): LERN's TypeScript domain, node tier, routes and lowdb store are not expected; the domain is Python behind MCP.
