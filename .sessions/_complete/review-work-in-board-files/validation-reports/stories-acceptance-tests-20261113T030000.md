# Validate — stories-acceptance-tests (second pass)

Guidance: stories-acceptance-tests, with overlays cdd_web_domain_access and lern_domain_driven.
Session: review-work-in-board-files. The validate call saved no report of its own, so this judgment is written here.
It follows `stories-acceptance-tests-20261113T020000.md` after the fixes for its Python findings.

Paths judged:
- space/kanban/review-files-in-viewer.story.shared.py
- space/kanban/session_board_examples.py
- space/session/file_comments.py
- space/session/session_file.py

Runs: review-files-in-viewer domain 23 / server 8 pass, kanban_tools_spec 116 pass, session_spec pass (297 together).

Fixed since the first pass:
- `domain-operations-inline-in-steps`: `comments_of` and `add_comment` are gone; each When and Then calls `world.Ticket.load(...).session.file_comments.<operation>` in the step. `seed_checkout_flow`, `seed_connected_chat`, `seed_file_comments` and `seed_comment_shown_in_chat` moved to `session_board_examples.py`.
- `given-only-what-the-system-checks`: "Keep the comment unsent when the chat is not connected" names the comment in its own step, "And checkout-flow's file comments hold order.py:L12-L14, not sent", in the markdown and the shared story.
- `standard-mutation-response`: `add`, `remove`, `send`, `send_open` and `clear_processed` all return `FileComments`.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md`

### `playwright-tests-browser-interaction` — Fail
- review_fidelity_outputs_on_board_story.test.md:26 The changed-files filter and its clear are screen interactions with no Playwright test; the TypeScript viewer is not built.
- review_fidelity_outputs_on_board_story.test.md:52 Browse Ticket Files By Practice (filters, colored tabs, preset, select tab) has no test in any tier.
- review_fidelity_outputs_on_board_story.test.md:97 Opening the session folder from the session button has no screen test.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md`

### `playwright-tests-browser-interaction` — Fail
- review_files_in_viewer_story.test.md:51 Rendering markdown as a page, and folding (line 57), are screen outcomes; the Python tiers prove only the data the viewer draws from.
- review_files_in_viewer_story.test.md:173 Show Changed File In Viewer: the viewer refreshing when a comment turns processed has no screen test.

## Judgment — `harness/.context/stories/story-map.md`

### `do-not-invent-requirements` — Fail
- story-map.md:591 `Show AI Changes As Diff` is in this session's increment but has no scenarios and no acceptance test.
- story-map.md:553 `List Ticket Context Files` is the ticket's name for the story whose scenarios and tests say `List Ticket Files`.

## Passes

stories-acceptance-tests: examples-declare-seed-vs-interaction, shared-example-fixtures (`ORDER_GRAPH`, `FileCommentExample`), seed-state-at-its-real-owner (the saved graph seeded where the session keeps it), separate-test-controls-from-production-contracts, system-stubs-domain-real, assert-domain-behavior-not-seeded-state (folds and violations are ranged by `SessionFile`, not read back), infrastructure-in-lifecycle-hooks, inline-simple-gwt-bodies, domain-operations-inline-in-steps, extract-assertion-helper (`states_on_order`, `queued_fills`), given-only-what-the-system-checks.
cdd_web_domain_access: domain-lives-in-python (folds and violations ranged in `SessionFile`), state-lives-behind-the-tool, one-line-to-the-domain (`session.file`), tool-stays-thin, annotate-what-typescript-reads, read-files-through-the-file-manager (`SessionFile` reads through `SessionFiles`), fail-loud-on-mcp.
lern_domain_driven: standard-mutation-response, reduce-story-overlap, shared-behavior-stays-tier-free, server-tier-calls-the-real-thing, no-expect-in-given.
Noise (covered by cdd_web_domain_access): LERN's TypeScript domain, node tier, routes and lowdb store are not expected; the domain is Python behind MCP.
