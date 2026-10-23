Commit local changes. Optional hint: {{hint}}.

Inspect git status and diff (staged and unstaged) with the Shell tool.
On Windows PowerShell, chain git commands with ``;`` (``&&`` is not supported).

Draft a commit message that:
- Summarizes what changed and why in a short imperative subject.
- Names practice, fidelity, and artifact format when this session used CDD
  tools (slash commands, MCP tools, or skills), for example bdd-behavior,
  clean-engineering-code, or sketch.
- Calls out key paths when that clarifies scope.

If the working tree is clean, say so and do not call ``repo.push_commit``.
Otherwise call MCP ``repo.push_commit`` with the full message (subject plus body when useful).
