# BDD sketch â€” workspace (slices A + B)

Design: `workspace-eval-oo-sketch.md` Â§2. Grill: `grill-answers.md`.

## Slice A â€” path overrides (ticks 1â€“3)

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

## Slice B â€” openWorkSession (grill tick 4)

Fidelity: behavior

a workspace
  that opens a work session
    -> workspace.openWorkSession(name, goal, fidelities, contexts, path, default_path, tool, fidelity)
    it should load path overrides from context-index before opening
    with a new session name
      it should add the opened work session to its work sessions
      it should set the current work session to the opened work session
    with an existing session name
      it should load the existing work session from its sessions folder
      it should set the current work session to that work session
    with an explicit path that differs from the default path for the opening tool
      it should record a path override for that tool and fidelity
    with an explicit path that equals the default path for the opening tool
      it should drop any path override for that tool and fidelity

## Slice C â€” WorkSession.open (grill tick 5)

Fidelity: behavior

a work session
  that is opened on its workspace
    -> workSession.open(name, goal, fidelities, contexts, path)
    with HEAD already on its session branch
      it should continue without switching branch
    with a clean working tree not on its session branch
      with an existing session branch
        it should check out that session branch
      with no session branch yet
        it should create its session branch
    with a dirty working tree not on its session branch
      it should refuse to switch branch

## Slice D â€” host edit-path resolution (grill tick 6)

Fidelity: behavior

a context tool host
  that opens on a workspace with a context index key and default workspace folder
    with an explicit path argument
      it should use that path as its durable edit root
    with no explicit path argument
      with a stored override for its tool and fidelity
        it should use the override path as its durable edit root
      with no stored override
        it should use the path under its workspace default folder

**Deferred:** Turn/git/repairs via currentWorkSession; SessionLog; GitRepo commit/push on Turn.finish.

