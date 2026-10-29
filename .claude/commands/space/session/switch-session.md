Switch to session ``name``, creating its folder when missing. Returns keep_log.

``name`` defaults to ``session`` in ``.sessions/session.json``, then to the saved ``branch``.
Saves ``name`` as ``session`` there. Does not touch branches or worktrees.

Use MCP tool: `session.switch(name: 'str' = '', workpath: 'Path | None' = None, repo_path: 'Path | None' = None, session_path: 'Path | None' = None)`
