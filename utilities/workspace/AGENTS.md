# Worktree Commit Guidance

- Treat the complete worktree as the ownership boundary for a WorkSession.
- `finish_work_session` commits every modified, staged, deleted, and untracked file under the repository root; never limit its commit to `scope_paths` or session artifacts.
- Keep the WorkSession guidance, prompt docstring, deployed skill, behavior, and tests aligned whenever finish semantics change.
