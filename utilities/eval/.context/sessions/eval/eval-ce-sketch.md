# eval — Clean Engineering sketch

**Session:** `utilities/eval/.context/sessions/eval/`  
**Pairs with:** `eval-bdd-sketch.md` (BDD)  
**Active module:** `utilities/eval`  
**Fidelity:** informal modules  
**Status:** theme ready to code (ring 1)

## Module map

```
utilities/
  workspace/                    ← KEEP — now at context_tools/actions/workspace
  eval/                         ← OWN — Session YAML, Turn, ToolCall, Mistake, Correction, Repair
  repair/                       → absorb into eval/ (now at context_tools/actions/repair)
  record_decisions/             ← KEEP — CDRs ≠ turns
  scanners/                     ← KEEP — Scan; eval depends for regression only

context_tools/
  base/                         ← self.workspace + self.eval (+ scan, decisions)
```

## Placement (locked)

| Concern | Today | Target |
|---|---|---|
| path / folder / open / ContextIndex | workspace | **workspace** |
| SessionLog / @log → events.log | workspace | **eval** (ToolCall on open turn) |
| Mistake / correction | repair | **eval** |
| repair / improve / regression / archive | repair | **eval** |
| git branch/commit helpers | — | **WorkspaceRepo** + **CDDRepo** (in eval) |
| RecordDecisions | record_decisions | **record_decisions** |

**Edges:** `eval → workspace` only.  
**Names:** `workspace.Session` = locations; `eval.Session` = domain.  
**Base:** `self.workspace` + `self.eval` (`eval.Session`).

## Theme: eval/ (detail)

Persist as **`{workspace.folder}/session.yaml`**.

**While a chat reply is in progress:** keep one **open Turn** on the Session. Tool runs and mistakes attach to that open Turn. When the reply finishes: if the working area changed → commit, close the Turn onto `turns`, save YAML; if nothing changed → drop the open Turn (no append, no commit).

**Mistake → fix:**

```
Session
  Turn (spotted)
    Mistake
      correction
        improved
        status                      // open | fixed
        fixedIn → Turn (fix)
  Turn (fix)
    toolCalls / prompt / result
    changeCommit
```

```
eval/
  Session
    workspace                       // workspace.Session (path, folder, name)
    branch                          // from WorkspaceRepo.ensureSessionBranch(workspace.name)
    turns                           // closed Turn[]
    openTurn                        // Turn in progress; null when idle
    workspaceRepo                   // WorkspaceRepo
    cddRepo                         // CDDRepo
    // on start / construct:
    //   branch = workspaceRepo.ensureSessionBranch(workspace.name)
    beginTurn
      // create openTurn if idle
    recordToolCall toolCall
      -> beginTurn
      -> openTurn.toolCalls.add
    recordMistake mistake
      -> beginTurn
      -> openTurn.mistakes.add
    recordCorrection mistakeId improved
      -> find Mistake by entryId
      -> mistake.correction.improved / status=fixed
      -> mistake.correction.fixedIn = openTurn or latest closed turn
    finishTurn prompt result context
      // if working area dirty:
      -> workspaceRepo.commitOnSessionBranch
      -> cddRepo.currentBranchAndSha
      -> turns.append(openTurn)
      -> save
      // if clean: discard openTurn
      openTurn = null
    save                            // session.yaml
    load

  ----
  Turn
    id
    toolCalls
    context
    prompt
    result
    mistakes
    changeCommit
    toolBranch
    toolSha

  ----
  ToolCall
    toolset
    name
    summary

  ----
  Mistake
    entryId
    artifact
    rule
    wrong
    original
    tool
    fidelity
    correction                      // owned Correction

  ----
  Correction
    improved
    status                          // open | fixed
    fixedIn                         // → Turn that fixed it

  ----
  WorkspaceRepo
    ensureSessionBranch sessionName
    commitOnSessionBranch paths message
    currentCommit
    currentBranch

  ----
  CDDRepo
    currentBranchAndSha

  ----
  ArchivePromoter                   < scaffold for first coding slice
    promote session commitRange archiveRepo
    leavePointerAndPrune session

  ----
  Repair                            // lives in eval; Base keeps log_mistake face
    session                         // eval.Session
    scanner
    log_mistake …
      -> session.recordMistake
    log_correction …
      -> session.recordCorrection
    repair asset violation
    improve
    verify_regression examplesRoot
    archive …
      -> ArchivePromoter.promote     // after ArchivePromoter exists
```

## workspace/ (association)

```
workspace/
  Session
    path
    folder
    open
```

## First coding slice (v1)

1. `utilities/eval`: `Session`, `Turn`, `ToolCall`, `Mistake`, `Correction` + YAML save/load  
2. `beginTurn` / `recordToolCall` / `recordMistake` / `recordCorrection` / `finishTurn`  
3. Point `BaseContextTool.log_mistake` / `log_correction` at `self.eval` (move or wrap Repair)  
4. Point `@log` append at `self.eval.recordToolCall` (keep old events.log readable if easy; do not block on deleting it)  
5. Thin `WorkspaceRepo` / `CDDRepo` — enough for session branch + commit on `finishTurn` when dirty  
6. Defer: ArchivePromoter, full Repair file move polish, rings 2–5  

## Invariants

- One `session.yaml`; closed Turns under Session; Mistakes under Turn; ToolCalls under Turn.  
- Mistake owns Correction; Correction.fixedIn → fixing Turn.  
- Dirty finish → git commit + append Turn; clean finish → no Turn, no commit.  
- `eval → workspace` only.

## Grill log

- Theme closed for coding — open-turn + finishTurn rules locked  
- Base attribute: `self.eval`  
- YAML path: `{folder}/session.yaml`
