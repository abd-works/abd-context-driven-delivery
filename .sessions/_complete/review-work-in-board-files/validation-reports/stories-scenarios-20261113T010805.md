# Validation: stories-scenarios (second pass)

Files:
- `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md` and `.py`
- `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md` and `.py`
- `harness/.context/stories/review-work-in-board-files-scenario-realization.md`

Graph rule validation: validate saved no report or graph section for stories-scenarios, so this is the AI judgment alone.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md`

These are the person's corrections of 2026-11-12, all applied:
- The example was the file manager's own code. It is now checkout-flow's `order.py`, in a session that works in `src/checkout`.
- "Works on the whole repository" and the outside-the-roots scenarios are gone. A session reaches only its own files, so those scenarios could not happen.
- Comments are not sent, sent, then processed.
- New stories: Mark File Comment Processed, Show Changed File In Viewer, and Clear Processed File Comments.
- Send File Comments To Chat has a new scenario: Send every open comment at once.

I also removed a scenario I had added myself, keeping an unsaved edit when the file changes on disk. No source asks for it (`do-not-invent-requirements`).

Passes: every scenarios rule, and every pattern rule that applies at this fidelity. In particular:
- `scenario-names-continuation`: Add Comment → Send, Send → Mark Processed, Mark Processed → Show Changed File.
- `given-only-what-the-system-checks`.
- `domain-lives-in-python`: the comment's state is read from its chat message's state in Python.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md`

The person's corrections of 2026-11-12, all applied:
- Listing only the branch's changes is now a changed-files-only filter, which the Person turns on and clears. It is marked intended.
- "Say in a toast when the list cannot be read" and "Refuse a file outside the repository" are removed. The board offers no ticket or file that would lead to them.

Passes.
