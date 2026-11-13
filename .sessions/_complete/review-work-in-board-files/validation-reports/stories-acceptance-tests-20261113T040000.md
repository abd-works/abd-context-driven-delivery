# Validate — stories-acceptance-tests (third pass)

Guidance: stories-acceptance-tests, with overlays cdd_web_domain_access and lern_domain_driven.
Session: review-work-in-board-files. validate.validate refused the paths: it names files from the session's root in the
main checkout (`C:\dev\abd-context-driven-delivery\harness\.context`), and these are in the ticket's worktree. So this
judgment is written here, as the second pass's was.
It follows `stories-acceptance-tests-20261113T030000.md` after the TypeScript viewer was built.

Paths judged:
- space/kanban/review-files-in-viewer.story.ui.spec.ts (new)
- space/kanban/review-fidelity-outputs.story.ui.spec.ts (rewritten)
- space/kanban/review-fidelity-outputs.story.shared.py (Open the workpath folder from the details)
- space/kanban/app/src/kanban/board/side-panel-client.spec.ts (files panel, filters, comments, save)
- harness/.context/stories/.../review_files_in_viewer_story.test.md (Show AI Changes As Diff)

Runs:
- review-files-in-viewer.story.ui: 23 pass.
- review-fidelity-outputs.story.ui: pass.
- The whole Playwright suite: the first run had 14 failures. 12 came from older specs pressing the removed folder button or the workpath link, or expecting a violation's markdown file as lines. After fixing those, the rerun passed: 140 of the touched files plus 29 of the e2e tier. The steer-ticket-sessions and e2e failures did not repeat.
- side-panel-client, help-text and package-direction (vitest): 54 pass.
- Python domain and server tiers, kanban_tools_spec and session_spec: 312 pass.

Fixed since the second pass:
- `playwright-tests-browser-interaction`:
  - The changed-files filter and its clear now have browser tests.
  - So do the practice filters (short forms, colored tabs, preset, turning one on, selecting a tab).
  - So do the session button, the workpath link, markdown rendered as a page, folding and violation marks.
  - So do adding, opening, deleting and keeping a comment across a reload.
  - So do send, send all, not connected, the changed file shown once processed, and clearing processed comments.
- `do-not-invent-requirements`: Show AI Changes As Diff now has scenarios (four), linked from the story map, with realizations.

## Judgment — `harness/.context/stories/story-map.md`

### `do-not-invent-requirements` — Fail
- story-map.md:591 `Show AI Changes As Diff` has scenarios but no acceptance test. Its scenarios are intended, not built.
- story-map.md:553 `List Ticket Context Files` is the ticket's name for a different story than `List Ticket Files`. The person said to leave it (2026-11-12).

## Judgment — `space/kanban/review-fidelity-outputs.story.ui.spec.ts`

### `shared-example-fixtures` — Fail
- review-fidelity-outputs.story.ui.spec.ts:44 The changed-files filter runs on checkout-flow, whose files are not changed, so the browser test sees the filter empty all tabs. The scenario's example is pet-visits with src/mine_spec.py changed; the fixture project has no branch for it. The filter's choice of the changed file is proven in side-panel-client.spec.ts, not on the page.
- review-fidelity-outputs.story.ui.spec.ts:70 The practice-filter tests use the fixture's story map files, not the scenario's stories/story-map.md, checkout_story.test.md and src/order_spec.py.

## Judgment — `space/kanban/review-files-in-viewer.story.ui.spec.ts`

### `shared-example-fixtures` — Fail
- review-files-in-viewer.story.ui.spec.ts:21 order.py is kept in the session folder (`.sessions/checkout-flow/order.py`), not the scenario's src/checkout. The fixture's checkout-flow works on the whole project, and its session folder is what the details open.
- review-files-in-viewer.story.ui.spec.ts:300 The not-connected toast names the chat named after the ticket (checkout-flow), not checkout-chat. The board knows no assigned chat that has not checked in (`working_chat` is null), so it sends to the ticket's own chat name.

## Passes

stories-acceptance-tests:
- playwright-tests-browser-interaction
- examples-declare-seed-vs-interaction
- seed-state-at-its-real-owner (comments, graph and file are seeded where the session keeps them)
- separate-test-controls-from-production-contracts
- system-stubs-domain-real (FakeChat checks in through the board's server)
- assert-domain-behavior-not-seeded-state
- infrastructure-in-lifecycle-hooks
- inline-simple-gwt-bodies
- domain-operations-inline-in-steps
- given-only-what-the-system-checks

cdd_web_domain_access:
- domain-lives-in-python (`session.workpath_files`; the page only filters on `is_changed` and practice)
- one-line-to-the-domain
- tool-stays-thin
- annotate-what-typescript-reads
- read-files-through-the-file-manager

lern_domain_driven:
- standard-mutation-response
- shared-behavior-stays-tier-free
- server-tier-calls-the-real-thing

Not checked here: the chat bar's session button (harness/chat-ui) has no test harness in the repository, and it was not loaded in a live chat.
