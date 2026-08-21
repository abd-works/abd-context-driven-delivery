 eval — Clean Engineering sketch

**Session:** `context_tools/actions/eval/.context/sessions/eval/`  
**Pairs with:** `eval-bdd-sketch.md` (BDD)  
**Active module:** `context_tools/actions/eval`  
**Fidelity:** informal modules  
**Status:** ring 1 coded; absorb Repair into eval — ready to code

**Sources / context:** `grill-answers.md`, `eval-bdd-sketch.md`, `context_tools/actions/eval/.context/module-context.md`

## Module map

```
utilities/
  workspace/                    ← KEEP — locations only (now at context_tools/actions/workspace)
  eval/                         ← OWN — EvalSession domain + Repair
  record_decisions/             ← KEEP — CDRs ≠ turns
  scanners/                     ← KEEP — Scan; Repair uses it to confirm mechanical violations

context_tools/
  bdd/                          ← KEEP — expect_scan_fails / expect_scan_passes (mistake fail/pass files)
  agent_bdd/                    ← KEEP — generate_and_judge (same pass file)
  base/                         ← self.workspace + self.eval + self.repairer (eval.Repair)
  actions/repair/               ← DELETE — no shim, no re-export; update all imports
```

**Build order:** workspace → eval (EvalSession) → eval.Repair → Base wiring. Domain specs stay in `context_tools/actions/eval/` (`session_spec.py`, `agent_bdd_spec.py`). Mistake fail/pass scan and generate+judge live on Bdd / AgentBdd spec helpers — not a new eval harness.

## Placement (locked)

| Concern | Target |
|---|---|
| path / folder / open / ContextIndex | **workspace** |
| session.yaml / collections / turn lifecycle | **EvalSession** (orchestrates) |
| @log → ToolCall on open Turn | **Turn.add** (via SessionLog → session.recordToolCall) |
| record / track a Mistake | **Mistake** |
| apply a Correction | **Correction** |
| log_mistake / log_correction / repair | **Repair** (atomic — does not call eval) |
| createRule (new rule + matching scanner) | **BaseContextTool.createRule** |
| eval | **Repair.eval** — separate tool; agent runs it after repair |
| contribute to evals (opt-in) | before/after session-branch commit links, then **run the latest eval** |
| git branch/commit | **WorkspaceRepo** + **CDDRepo** (extends WorkspaceRepo) |
| mistakes.log / old repair package | **deleted** |
| RecordDecisions | **record_decisions** |
| Archive | **scaffold** (rings 2–4 / promote later) — `promote` + archived EvalSessions |

**Edges:** `eval → workspace` only.  
**Names:** `workspace.Session` = locations (`WorkspaceSession` on the diagram); `EvalSession` = eval domain.  
**Base:** `self.workspace` + `self.eval` (`EvalSession`) + `self.repairer` (`eval.Repair`). Host exposes `repair` and `eval` as separate tools — not `improve`.

## Theme: eval/

Persist as **`{workspace.folder}/session.yaml`**.

**While a chat reply is in progress:** one **open Turn**. Tool runs and mistakes attach there. On finish: dirty working area → commit, append Turn, save YAML; clean → drop the open Turn.

```
eval/
  session.py
    EvalSession
      workspace                       // WorkspaceSession (path, folder, name)
      branch
      turns                           // composition — EvalSession owns Turns
      openTurn
      mistakes                        // composition — EvalSession collection; pointed-out this session
      repairs                         // composition — Repair instances this EvalSession created
      workspaceRepo                   // association — working-area clone; EvalSession does not own it
      cddRepo                         // association — CDDRepo extends WorkspaceRepo; EvalSession does not own it
      cddAt                           // CDD checkout linked once at start — not stamped every Turn
      beginTurn(): Turn
      recordToolCall(toolCall): None
        -> beginTurn(): Turn
        -> openTurn.add(toolCall): None
      finishTurn(prompt, result, context): None
        if workspaceRepo.isDirty(path):
          -> workspaceRepo.commitOnSessionBranch(paths, turnCommit): TurnCommit
          -> openTurn.changeCommit = that TurnCommit
          -> turns.add
          -> save(): None
        else:
          -> discard openTurn
      save(): None
      load(): EvalSession
      ----
      Turn
        id
        toolCalls                     // composition — tools called during this Turn
        context
        prompt
        result
        mistakes
        changeCommit                  // workspace TurnCommit this turn
        add(toolCall): None
        add(mistake): None
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
        correction
        repair                        // setter — 0..1 association
          -> repair.mistakes.add(self)
        record(session): None
          -> session.beginTurn(): Turn
          -> session.mistakes.add(self)
          -> session.openTurn.add(self): None
        correct(correction): None
          -> self.correction = correction
      ----
      Correction
        improved
        how                           // what changed in the context tool
        status                        // open | fixed
        fixedIn                       // → Turn that closed it
        apply(mistakes, turn): None
          -> each mistake.correct(self): None
          -> status = fixed
          -> fixedIn = turn
      ----
      WorkspaceRepo                   // session-tracked git clone — working-area change seam
        ensureSessionBranch sessionName
        commitOnSessionBranch paths turnCommit
          -> formats turnCommit into the git message
          -> returns that TurnCommit as HEAD
        currentCommit                 // last TurnCommit on the session branch
        currentBranch
        isDirty path
      ----
      CDDRepo                         // extends WorkspaceRepo — tool clone
        headSha                       // live checkout of the tools
        link session
          -> session.cddAt = headSha  // once — this asset session used these tools
        openSession name
          -> WorkspaceSession path = this clone
          -> EvalSession on that workspace (this CDDRepo is its workspaceRepo)
          // repair and eval are ordinary turns on that session
      ----
      TurnCommit                      // the session-branch commit for a finished Turn
        turnId
        sessionName
        toolNames                     // tools called this turn
        mistakeIds                    // mistakes on this turn, if any
        sha                           // git identity — wrapped here, not returned as a bare string
        // WorkspaceRepo formats these fields into the git message

    Repair
      session                         // association — the asset EvalSession; EvalSession owns the collection
      cddSession                      // association — EvalSession whose working area is the CDD clone
      mistakes                        // association — many; Mistake has 0..1 Repair
      scanner                         // association — does not own Scan
      host                            // association — BaseContextTool that launched this Repair
      log_mistake(artifact, rule, wrong, original): str
        -> Mistake(...).record(session): None
      log_correction(mistakes, correction): None
        -> session.beginTurn(): Turn
        -> correction.apply(mistakes, session.openTurn): None
      _begin(mistakes): Repair
        -> session.repairs.add(self)
        -> each mistake.repair = self
        -> cddSession = session.cddRepo.openSession(name): EvalSession
      _kind(asset, violation): Kind    // mechanical | judgment
      repair(asset, violation): None
        if not session.mistakes:
          -> host.contexts: Instruction
          -> log_mistake(artifact, rule, wrong, original): str
        -> _begin(mistakes): Repair
        -> scanReport = scanner.scan(paths): ScanReport
        if not scanReport.matches(mistake):
          -> validateReport = host.validate(): str
          if validateReport.ok:
            -> kind = _kind(asset, violation): Kind
            if kind == mechanical:
              -> host.createRule(failed, wanted): None
              -> scanReport = scanner.scan(paths, root, rule): ScanReport
              -> detected = scanReport.matches(mistake): bool

        -> host.contexts: Instruction
        -> host.examples: Instruction
        -> host.templates: Instruction
        -> AskQuestion(prompt): str
        -> cddSession.beginTurn(): Turn
        -> cddSession.recordToolCall(toolCall): None
        -> cddSession.finishTurn(prompt, result, context): None
        -> host.generate(): str
        -> landed = host.validate(): str
        if landed.ok:
          if not correction:
            -> host.contexts: Instruction
            -> log_correction(mistakes, correction): None
          else:
            -> correction.apply(mistakes, session.openTurn): None
      eval(): None
        if not cddSession:
          -> cddSession = session.cddRepo.openSession(name): EvalSession
        -> cddSession.beginTurn(): Turn
        -> cddSession.recordToolCall(toolCall): None
        -> cddSession.finishTurn(prompt, result, context): None
        -> cddSession.beginTurn(): Turn
        -> cddSession.recordToolCall(toolCall): None
        -> cddSession.finishTurn(prompt, result, context): None
        -> scanner.scan(beforePaths, root, rule): ScanReport
        -> scanner.scan(afterPaths, root, rule): ScanReport
        -> AgentBdd.validate(): str
        -> generateResult = AgentBdd.generate(): str
        if generateResult.ask:
          -> AskQuestion(prompt): str
      contribute(beforeCommit, afterCommit): None
        -> eval(): None

  BaseContextTool
    createRule(failed, wanted): None
      -> contexts: Instruction
      -> examples: Instruction
      -> templates: Instruction

  session_spec.py                     // eval domain (session/git/repair)
  agent_bdd_spec.py                   // eval domain (real-git agent path)
    // mistake regression is NOT here — Bdd expect_scan_fails/passes +
    // AgentBdd generate_and_judge

  Archive                             < scaffold
    sessions                          // composition — EvalSessions this Archive has promoted
    promote session commitRange
      -> sessions.add
      // working area keeps a thin pointer; bulky session-area audit is pruned
```

## workspace/ (association)

```
workspace/
  Session
    path
    folder
    open
```

## First coding slice (v1) — DONE

1. Session / Turn / ToolCall / Mistake / Correction + YAML  
2. beginTurn / recordToolCall / recordMistake / recordCorrection / finishTurn  
3. Base `log_mistake` / `log_correction` on eval (temporary direct-to-eval; this slice moves them onto Repair)  
4. @log → recordToolCall  
5. Thin WorkspaceRepo / CDDRepo  

## Next coding slice — absorb Repair (locked)

1. Behavior on the objects: Mistake.record / repair setter / correct; Correction.apply; Turn.add; Repair._begin + loop. EvalSession only orchestrates turn lifecycle + save/load.  
2. Base: `self.repairer = Repair(session=self.eval, scanner=…)`; host log_* forward to repairer  
3. Delete `mistakes.log` as a store; Session YAML is the store  
4. **Delete** `context_tools/actions/repair` — no shim; update imports  
5. **Eval is a separate tool** — agent calls `eval` after repair; repair does not call it  
6. Contribute opt-in: link before/after session-branch commits; **run `eval`**  
7. Asset session: `cddRepo.link` once (`cddAt`). Repair._begin: `cddRepo.openSession`. No `stampTurn`. **No `improve`** — repair wires mistake/correction from context if missing. **createRule** on Base when scan does not already match the Mistake.
8. Defer: rings 2–4, Archive (`promote` + archived EvalSessions), fuller ring 5  

## Invariants

- One `session.yaml`; EvalSession owns Turns, Mistakes, and Repairs it created and orchestrates turn lifecycle + persist. ToolCalls under Turn.  
- Mistake owns recording/tracking itself (`record`, repair setter, `correct`). Correction owns applying a fix (`apply` → status=fixed, fixedIn → Turn).  
- Repair owns `repair` (atomic) and `eval` (separate tool). If repair has no Mistake or Correction, it takes them from context and wires them. No `improve`. Session does not record mistakes, apply corrections, or begin repairs.  
- Mistake has 0..1 Repair; a Repair may collect many Mistakes. Repair does not own Mistakes (they exist with zero repairs).  
- Archive owns the EvalSessions it has promoted (`sessions` collection). `promote` adds an EvalSession to that collection.  
- Composition only when the owner owns the part's lifetime. WorkspaceRepo, CDDRepo, Scan, and WorkspaceSession fail that test — associations.  
- Repair.repair does not call eval. Agent (or contribute) runs eval after a repair.  
- createRule only when scan does not already match the Mistake; then run that rule and detect a failure that matches the Mistake.  
- CDDRepo **extends** WorkspaceRepo. Asset session **links once** (`cddAt` = headSha). Repair **opens a WorkspaceSession on the CDD clone**. `repos_for_workspace` roots CDDRepo at the running tools clone, not `find_git_root(workspace)` — share one root only when the working area sits inside that clone. Cannot connect → `EvalGitConnectError`; no live Null fallback. No stampTurn on every generate.  
- Dirty finish → git commit + append Turn on **this** session's WorkspaceRepo; clean finish → no Turn, no commit.  
- Turn.changeCommit is this session's TurnCommit. Asset session does not store a per-turn CDD commit.  
- `eval → workspace` only.  
- Eval tests are **specs in this package** for the eval domain. Mistake fail/pass scan and generate+judge are Bdd / AgentBdd helpers, not an eval harness.

## Grill log

- Ring 1 coded — open-turn + finishTurn; `self.eval`; `{folder}/session.yaml`  
- Absorb Repair: eval.Repair; old repair package deleted  
- EvalSession collections: mistakes + repairs; Mistake 0..1 Repair; Repair many Mistakes  
- log_* : Base → repairer → Mistake.record / Correction.apply
- EvalSession orchestrates; Mistake / Correction / Repair / Turn own their behavior  
- Repair.repair is atomic; eval is a separate tool; no improve — repair wires mistake/correction from context if missing  
- Contribute: before/after commits; run latest eval
- Archive (not ArchivePromoter): promote + collection of archived EvalSessions
- Domain type: EvalSession (not Session) — workspace stays WorkspaceSession
- Correction.apply(mistakes, turn): each Mistake.correct; status=fixed; fixedIn=Turn
- createRule: Base action; skip if scan already matches the Mistake; then run the rule and detect a failure that matches the Mistake
