# BDD sketch — workspace module (usage story)

Design: `workspace-eval-oo-sketch.md` §2 (Workspace), §4 (turn envelope).

Fidelity: behavior

**LOCKED — mistake/correction association (Git-primary):**
- Mistake = git note payload on the **introducing commit SHA** (not the discovery turn's commit).
- Correction = **new commit** on the session branch; trailers + note payload name the mistake `entry_id`s (resolve to those introducing SHAs).
- `session.yaml` / session trail are **not** the association store.
- Merge/fix-branch topology: deferred (not required for this slice).

**LOCKED — mistake note payload** (on introducing SHA): `entry_id`, `artifact`, `rule`, `wrong`, `original`, `tool`, `fidelity` (+ introducing SHA identity).
**LOCKED — correction commit payload** (on fix SHA): `improved`, `how`, `status`, `entry_ids[]` (+ fix SHA; each id → introducing SHA).

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
        that records a mistake on its open turn
          it should note the mistake's entry id on the introducing commit on the session branch
          it should note the artifact path on that commit
          it should note the rule name on that commit
          it should note what was wrong on that commit
          it should note the original excerpt on that commit
          it should note the tool name on that commit
          it should note the fidelity on that commit
          it should not note the mistake on its open turn's commit
        that records a correction on its open turn
          it should record the improved content on its correction commit on the session branch
          it should record how the fix was made on its correction commit
          it should record the correction status on its correction commit
          it should record the entry ids of the mistakes it fixes on its correction commit
          it should link those entry ids to those mistakes' introducing commits on the session branch
      that the agent is finished working with it
        it should finish its turn for the action
      that has finished its turn
        it should record the action run on the session trail
        it should attach the action run record to its turn
        it should set its turn name to its context tool, action, and fidelity
        it should save that turn name as its commit message
        it should commit its scoped changes on the session branch
        it should push its session branch to origin
        with one supported format only
          it should include that format in its turn name
