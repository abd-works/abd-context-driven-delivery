# BDD sketch — workspace module (usage story)

Design: `workspace-eval-oo-sketch.md` §2. Grill: `grill-answers.md` (slices A–E).

Fidelity: behavior

a context tool
  with a workspace
    that has an action run against it
      with a new work session name
        it should add the opened work session to its work sessions
        it should set the current work session to the opened work session
      with an existing work session name
        it should load the existing work session from its sessions folder
        it should set the current work session to that work session
      with HEAD already on its session branch
        it should continue without switching branch
      with a clean working tree not on its session branch
        with an existing session branch
          it should check out that session branch
        with no session branch yet
          it should create its session branch
      with a dirty working tree not on its session branch
        it should refuse to switch branch
      it should open a turn for the action run
      that has a turn open
        that is reading or writing module artifacts
          with an explicit path given on the run
            it should use that path for its module artifacts
          with no explicit path given on the run
            with no path override for its tool and fidelity
              it should use its default workspace folder for its module artifacts
            with a path override for its tool and fidelity
              it should use the override path for its module artifacts
        with a path for the turn that differs from the default path
          it should keep a path override for that tool and fidelity
        with a path for the turn that equals the default path
          it should drop the path override for that tool and fidelity
        that is asked for its instructions
          it should record the expansion on the session trail
          it should attach the expansion record to its open turn
      that has finished its turn
        it should record the action run on the session trail
        it should attach the action run record to its turn
        with a dirty working tree on its session branch
          it should commit its scoped changes on the session branch
        it should push its session branch to origin

**Deferred:** domain Repair / mistake / correction chain (eval module Bdd sketch).
