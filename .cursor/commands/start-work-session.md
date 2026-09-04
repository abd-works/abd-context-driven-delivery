start_work_session — agent starts or resumes a named work session.

Non-default session branches isolate in a sibling worktree named
``{abbrev}-{ticket}`` (or a short slug) next to the primary clone.
Stay in the primary clone when the session branch is the default branch.
Pass ``isolate: false`` to keep session folders / turns / logs on the
current checkout (no sibling worktree) — e.g. track work on main.

Do not call this from a /cli-agent parent. CliAgent opens the session,
switches to that path, and binds doer/judge. Resume does not rewrite Start.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: workspace.workspace:WorkSession
tool: start_work_session
```
.\tools.ps1 run -
