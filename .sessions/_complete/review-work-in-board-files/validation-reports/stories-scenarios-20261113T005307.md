# Validation: stories-scenarios

Files:
- `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md` and `.py`
- `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md` and `.py` (Open Session Files From Details only)
- `harness/.context/stories/review-work-in-board-files-scenario-realization.md`

Graph rule validation: validate saved neither a report nor a graph section for stories-scenarios on either call (2026-11-12). This report is the AI judgment alone.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-files-in-viewer/review_files_in_viewer_story.test.md`

The first pass found three failures, and all three were fixed before this judgment:
- `scenario-names-continuation`: Mark a comment beside the selection's first line did not name Send File Comments To Chat.
- `when-holds-the-operation`: Save the edited text had two Whens, edit and save. The edit is now a Given.
- `examples-trace-domain-model`: line 173 of the chat fill was abbreviated. It is now the real line.

Passes: every scenarios rule and every pattern rule that applies at this fidelity.
- `do-not-invent-requirements`: each story cites its request, the research, or the grill answer.
- `flagged-writes-intended-gwt`: the Evidence section says nothing here is built.
- `read-files-through-the-file-manager`: reading and saving go through `FileManager`.
- `domain-lives-in-python`: the sent mark and the prompt are made in `FileComments.send`.

The LERN rules for tiers, stores and shared stories apply at acceptance tests, not here. cdd_web_domain_access puts the domain in Python, so they are not expected.

## Judgment — `harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md`

Passes: Open Session Files From Details.
- The handoff link and No handoff yet are observed in `details-view.tsx:37-55`.
- That the workpath link opens its folder is intended, flagged in the story's evidence line.

## Judgment — `harness/.context/stories/review-work-in-board-files-scenario-realization.md`

Passes: each When realizes one page call reaching one domain operation. The new operations are named as new: `FileManager.write`, `FileComments.add/on/remove/send`, `FileComment.prompt/mark_sent`, `FileText.language`.
