# BDD sketch ΓÇö workspace path overrides (slice A)

**Grill record:** `grill-answers.md` ticks 1ΓÇô3 (turns 9266b3db ΓÇª 92bd1931). **Slice unlocked:** yes.

**Sources:** `workspace-eval-oo-sketch.md` ┬º2 (Workspace, PathOverride, lines 47ΓÇô50, 55ΓÇô58, 111ΓÇô123, 131).

Fidelity: behavior

a workspace
  -> workspace = Workspace(path=...)
  that has been loaded
    with no context-index file present
      it should expose an empty path override list
    with a context-index file listing tool, fidelity, and path rows
      it should expose those rows as path overrides
  that is asked for a tool path
    with no override stored for that tool and fidelity
      it should return no override path
    with an override stored for that tool and fidelity
      it should return the stored workspace-relative path
  that records a tool path with a known default path
    with a path that differs from the default path
      -> workspace.upsertPath(tool, fidelity, path, default_path)
      it should keep a path override row for that tool and fidelity
    with a path that equals the default path
      -> workspace.upsertPath(tool, fidelity, path, default_path)
      it should drop the path override row for that tool and fidelity
  that is saved after path overrides change
    it should write current override rows to context-index under its path without a change log section

**Deferred (next slices):** `workSessions`, `currentWorkSession`, `openWorkSession`, `WorkSession.open`, BaseContextTool three-step resolution on open.
