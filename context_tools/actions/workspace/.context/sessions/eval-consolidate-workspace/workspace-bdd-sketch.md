# BDD sketch — workspace module (usage story)

Design: `workspace-eval-oo-sketch.md` §2. Grill: `grill-answers.md` (slices A–D).

Fidelity: behavior

a context tool
  that is invoked to run an action
    -> workspace.openWorkSession(name, goal, fidelities, contexts, path, default_path, tool, fidelity)
    -> turn.open(host)
    it should open its work session before domain steps
    it should load path overrides from context-index before opening
    with an explicit path argument on open
      it should resolve its path to that argument
    with no explicit path argument on open
      with a stored override for its tool and fidelity
        it should resolve its path to the override path
      with no stored override
        it should resolve its path to its default workspace folder under the workspace
    with a new work session name
      it should add the opened work session to its work sessions
      it should set the current work session to the opened work session
    with an existing work session name
      it should load the existing work session from its sessions folder
      it should set the current work session to that work session
    with an explicit path that differs from the default path for the opening tool
      it should record a path override for that tool and fidelity
    with an explicit path that equals the default path for the opening tool
      it should drop any path override for that tool and fidelity
    with its work session opening on the workspace
      with HEAD already on its session branch
        it should continue without switching branch
      with a clean working tree not on its session branch
        with an existing session branch
          it should check out that session branch
        with no session branch yet
          it should create its session branch
      with a dirty working tree not on its session branch
        it should refuse to switch branch

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

**Deferred:** Turn/git/repairs via currentWorkSession; SessionLog; GitRepo commit/push on Turn.finish.
