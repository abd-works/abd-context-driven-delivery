# BDD sketch — workspace module (usage story)

Design: `workspace-eval-oo-sketch.md` §2. Grill: `grill-answers.md` (slices A–D).

Fidelity: behavior

a context tool
  with its workspace
    -> workspace = Workspace(path=...)
    that has been loaded
      with no path overrides persisted
        it should expose an empty path override list
        it should have no override path for its tool and fidelity
      with a path override stored for its tool and fidelity
        it should expose that path override
        it should return the stored workspace-relative path for its tool and fidelity
      with path overrides stored for other tools only
        it should have no override path for its tool and fidelity
      that records a tool path with a known default path
        with a path that differs from the default path
          -> workspace.upsertPath(tool, fidelity, path, default_path)
          it should keep a path override row for that tool and fidelity
        with a path that equals the default path
          -> workspace.upsertPath(tool, fidelity, path, default_path)
          it should drop the path override row for that tool and fidelity
      that is saved after path overrides change
        -> workspace.save()
        it should persist its path override rows under its path
  that is invoked to run an action
    with an explicit path argument
      it should resolve its path to that argument
    with no explicit path argument
      with no override path stored for its tool and fidelity
        it should resolve its path under its default workspace folder
      with an override path stored for its tool and fidelity
        it should resolve its path to the override path
    -> workspace.openWorkSession(name, goal, fidelities, contexts, path)
    it should load its path overrides
    with a new work session name
      it should add the opened work session to its work sessions
      it should set the current work session to the opened work session
    with an existing work session name
      it should load the existing work session from its sessions folder
      it should set the current work session to that work session
    with a resolved path that differs from the default path
      it should record a path override for that tool and fidelity
    with a resolved path that equals the default path
      it should drop any path override for that tool and fidelity
    with its work session opening
      with HEAD already on its session branch
        it should continue without switching branch
      with a clean working tree not on its session branch
        with an existing session branch
          it should check out that session branch
        with no session branch yet
          it should create its session branch
      with a dirty working tree not on its session branch
        it should refuse to switch branch
    -> turn.open(host)
    it should open a turn for the action run

**Deferred:** Turn/git/repairs via currentWorkSession; SessionLog; GitRepo commit/push on Turn.finish.
