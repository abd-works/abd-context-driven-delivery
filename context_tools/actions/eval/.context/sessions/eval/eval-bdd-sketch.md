 eval — BDD sketch

**Session:** `context_tools/actions/eval/.context/sessions/eval/`  
**Perspectives active:** BDD + Clean Engineering (Modules)  
**Status:** theme ready to code — CE in `eval-ce-sketch.md`

## Stance

One subject: **`an eval session`**. One YAML. Packages: **workspace** (paths) + **eval** (domain). Repair absorbs into eval.

## Capability rings

```
1 capture + placement               ← done (coded)
1b absorb Repair into eval          ← this theme — grilling
2 review / observe / report       < scaffold
3 tactical root cause             < scaffold
4 deeper root cause               < scaffold
5 formalized agent eval           < scaffold
5a contribute to evals            ← locked: opt-in after repair (not inside repair)
```

## Theme: an eval session

```
an eval session
  that was started through a context tool
    with a working-area path
      it should expose that path for durable work
      it should create a WorkspaceRepo branch named for this session
      it should link cddAt from cddRepo.headSha once
    that the host records through eval
      it should expose eval beside workspace
      that a first-order logged tool is invoked on the host
        it should attach a ToolCall to the open Turn
        it should not close the Turn yet
      that a mistake is logged on the host
        it should have that Mistake record itself onto the session
        it should have that Mistake add itself to the open Turn
      that a correction is logged on the host
        it should have that Correction apply onto the Mistake collection
        it should set Correction.status=fixed
        it should set Correction.fixedIn to the open Turn

  that chooses git clones for the working area
    that lives in a project clone separate from the tools
      it should root WorkspaceRepo at the project clone
      it should root CDDRepo at the tools clone
    that lives inside the tools clone
      it should share that clone's git root for both repos
    that has no git clone
      it should report that it cannot connect

  that a first-order tool or action runs before the chat turn is finished
    it should attach a ToolCall to the open Turn
    it should not close the Turn yet

  that an asset is repaired with no Mistake on the session
    it should take the Mistake from context
    it should have that Mistake record itself onto the session
    that the fix lands with no Correction
      it should take the Correction from context
      it should have that Correction apply onto the Mistake collection

  that a mistake is pointed out before the chat turn is finished
    it should have that Mistake record itself onto the session
        it should have that Mistake add itself to the open Turn
        it should write that Mistake under the session mistakes folder named after the mistake
        it should not write an improvement folder when no improvement was made
        it should leave Correction open on that Mistake
    it should leave that Mistake with no Repair
    that the same Mistake's asset is repaired
      it should begin a Repair
      it should set that Mistake.repair to the Repair
      it should open a WorkspaceSession on the CDD clone
      it should bring the project mistakes onto that CDD session as copies
      it should write those mistakes under the CDD session folder
      it should keep the project mistake files on the project session
      it should write a landing correction under the CDD session as well
      it should implement the tool fix as turns on that CDD session
      with further Mistakes collected into the same Repair
        it should attach those Mistakes to the same Repair
        it should keep each Mistake on exactly one Repair
      with neither a scan violation nor a judge finding yet
        it should determine whether the fix is mechanical or judgment-based
        with a mechanical fix
          it should call createRule with what failed and what is wanted
          it should write a new rule and a matching scanner to the tool
          it should run that rule
          it should have ScanReport.matches true for that Mistake
      with a scan violation for that Mistake
        it should not call createRule
        it should have ScanReport.matches true for that Mistake before root-causing
      with a judge finding for that Mistake
        it should confirm that finding from validate before root-causing
      with a mechanical fix
        it should use contexts, examples, and template to find why the context tool produced the mistake
        with the fault in the context tool's own guidance
          it should fix that fault in the context tool
        with the fault in a shared utility the tool depends on
          it should fix that fault in that utility
        with the fault in a shared primitive the tool depends on
          it should fix that fault in that primitive
        it should wait for approval before applying that change
        it should regenerate the asset from the fixed tool
        it should pass validate
        it should have that Correction apply onto the Mistake collection
        it should set Correction.status=fixed
        it should set Correction.fixedIn to the Turn that did the fix
      with a judgment-based fix
        it should use contexts, examples, and template to find why the context tool produced the mistake
        with the fault in the context tool's own guidance
          it should fix that fault in the context tool
        with the fault in a shared utility the tool depends on
          it should fix that fault in that utility
        with the fault in a shared primitive the tool depends on
          it should fix that fault in that primitive
        it should wait for approval before applying that change
        it should regenerate the asset from the fixed tool
        it should pass validate
        it should have that Correction apply onto the Mistake collection
        it should set Correction.status=fixed
        it should set Correction.fixedIn to the Turn that did the fix
        it should fix the guidance in prose
      that the same Mistake is fixed in a later Turn
        it should have that Correction apply onto the Mistake
        it should set Correction.fixedIn to the Turn that did the fix
        it should keep the same Mistake.entryId
        it should store the Correction as repairedAsset beside that Mistake
        it should write an improvement folder named after the problem theme under repairs
        it should write which tool was improved, how, and what the error was
        it should drop that Mistake folder into that improvement folder
        it should not leave that Mistake under the session mistakes folder
        that a second Mistake of the same problem is also fixed
          it should drop both Mistake folders into the same improvement folder

  that an agent chat turn has finished
    with changes to the working area
      it should close the open Turn onto the EvalSession
      it should record prompt, result, and context on that Turn
      it should commit the working-area delta on the WorkspaceRepo session branch
      it should write a TurnCommit as that commit
      it should set Turn.changeCommit to that TurnCommit
      it should save session.yaml
    with no changes to the working area
      it should discard the open Turn
      it should not create a WorkspaceRepo commit
```

## Theme: eval (open)

```
an eval session
  that a Mistake's asset was repaired
    that eval is run
      it should fail scan on the before version
      it should pass scan on the after version
      it should pass the AI judge
      it should generate a similar successful result
      it should hold that last generate for human review
      with a need to confirm with the user
        it should ask via AskQuestion
```

Mistake specs do **not** live in this package. Mechanical: Bdd
`expect_scan_fails` / `expect_scan_passes`. Judgment: AgentBdd
`generate_and_judge` on the pass file.

## Theme: contribute to evals (open)

```
an eval session
  that a Mistake's asset was repaired
    that contribute-to-evals is run
      it should link the session-branch commit from before the fix
      it should link the session-branch commit after the fix
      that the latest eval has been created
        it should run that latest eval
```

## Grill log

- Ring 1 coded; next theme locked: absorb Repair into eval (2026-08-17)
- Slice locked: Session-YAML repair loop; mistakes.log deleted
- Repair: EvalSession collection of Repair; Mistake 0..1 Repair; Repair many Mistakes. Repair is atomic. **eval is a separate tool** after repair. **No improve** — repair wires mistake/correction from context if missing
- Old `context_tools/actions/repair` **deleted** on delivery — no shim
- Contribute to evals: opt-in before/after commit links; **only eval connection** = run the latest eval after it is created
- Open Turn / finishTurn / Archive deferred as before
- Correction.apply(mistakes, turn): each Mistake.correct; status=fixed; fixedIn=Turn
- EvalSession orchestrates; Mistake / Correction / Repair / Turn own their behavior
- CDDRepo extends WorkspaceRepo; link once (cddAt); repair is a WorkspaceSession on the CDD clone — no stampTurn
- ScanReport.matches(mistake): scan already matching the Mistake skips createRule; after createRule the new rule must match
- eval is a separate tool after repair; repair does not call it
- Mistake regression: Bdd `expect_scan_fails` / `expect_scan_passes`; AgentBdd `generate_and_judge` — no eval-package harness
