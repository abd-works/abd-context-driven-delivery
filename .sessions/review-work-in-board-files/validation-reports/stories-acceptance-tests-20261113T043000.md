# Validate — stories-acceptance-tests (Show AI Changes As Diff)

Guidance: stories-acceptance-tests, with overlays cdd_web_domain_access and lern_domain_driven.
Session: review-work-in-board-files. validate.validate refused the paths again: the pinned cdd server names files from
the session's root in the main checkout (`C:\dev\abd-context-driven-delivery\harness\.context`), and these are in the
ticket's worktree. So this judgment is written here, as the earlier passes' were. It follows
`stories-acceptance-tests-20261113T040000.md`, and judges only what Show AI Changes As Diff added.

Paths judged:
- space/kanban/review-files-in-viewer.story.shared.py (four Show AI Changes As Diff scenarios)
- space/kanban/review-files-in-viewer.story.ui.spec.ts (seedOrderAs; four Show AI Changes As Diff scenarios, 7 tests)

Runs:
- review-files-in-viewer domain and server tiers: 42 pass.
- space/session plus the review-fidelity-outputs and review-files-in-viewer Python tiers: 306 pass.
- review-files-in-viewer.story.ui (Playwright): 30 pass.
- vitest (whole board app): 312 pass, 2 fail. Set Stage WIP Limit passed when rerun alone (flaky).
  Choose Session Root "should open its ticket with that folder as its workpath" fails each run: it expects the
  workpath `src/visits` and gets an absolute path. Neither touches the viewer, comments or session files.

Fixed since the third pass:
- `do-not-invent-requirements`: story-map.md:591 Show AI Changes As Diff now has acceptance tests on every tier and is
  built (`SessionFile.changes`, `FileComment.sent_text`, the viewer's changed, added and removed lines).

## Judgment — `space/kanban/review-files-in-viewer.story.ui.spec.ts`

### `shared-example-fixtures` — Fail
- The diff tests share the earlier caveat: order.py is kept in the session folder (`.sessions/checkout-flow/order.py`),
  not the scenario's src/checkout, because the fixture's checkout-flow works on the whole project.

## Passes

stories-acceptance-tests:
- playwright-tests-browser-interaction (changed line, the removed line above it, added lines, nothing marked, cleared)
- seed-state-at-its-real-owner (the processed comment and its sent text are seeded in file-comments.json, where FileComments keeps them)
- assert-domain-behavior-not-seeded-state (the changes are computed by SessionFile from the seeded comment and file)
- given-only-what-the-system-checks
- inline-simple-gwt-bodies
- domain-operations-inline-in-steps

cdd_web_domain_access:
- domain-lives-in-python (the diff is difflib in SessionFile.changes; the page only draws FileChangeData)
- annotate-what-typescript-reads (FileChange's fields are data fields; the adapter types were regenerated)

lern_domain_driven:
- shared-behavior-stays-tier-free
