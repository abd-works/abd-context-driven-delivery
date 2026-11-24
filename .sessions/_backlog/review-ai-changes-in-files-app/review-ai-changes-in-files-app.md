# Review AI Changes In Files App

Review what the AI changed in a file, turn by turn, the way other IDEs let a person accept or reject an agent's edits, without committing to git.

Filters in the Files app, each its own toggle (decided 2026-11-16 by the person):
- Session: the files this session's practices list.
- Changes: the files the session's branch changed since it left main (exists: SessionFiles.changed).
- Not reviewed: files whose text differs from the session's reviewed baseline.
- Reviewed: files the AI changed this session that the person has approved.

Increment 1, review: a reviewed baseline per session kept in git outside the branch's history (a tree written through a temporary index, `git add -A` + `git write-tree`, held by a ref such as refs/cdd/review/<session>), so untracked files and edits made through shell commands are caught too. Snapshot taken when a chat turn starts (the prompt-submit hook). The source view marks the lines changed since the baseline, reusing SessionFile.changes and the change marks. Approve moves a file's baseline to its current text; Approve all moves the whole snapshot.

Increment 2, reject: write the baseline text back (delete a file the AI created), with a confirm, a warning when the file changed again after the turn, and a message to the chat that its change was reverted. Whole files first; approving or rejecting single hunks is a later increment, only if needed (about double the work).
