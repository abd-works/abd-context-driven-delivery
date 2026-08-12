# eval — BDD sketch

**Session:** `utilities/eval/.context/sessions/eval/`  
**Perspectives active:** BDD + Clean Engineering (Modules)  
**Status:** theme ready to code — CE in `eval-ce-sketch.md`

## Stance

One subject: **`a session`**. One YAML. Packages: **workspace** (paths) + **eval** (domain). Repair absorbs into eval.

## Capability rings

```
1 capture + placement               ← this theme — ready to code
2 review / observe / report       < scaffold
3 tactical root cause             < scaffold
4 deeper root cause               < scaffold
5 formalized agent eval           < scaffold
```

## Theme: a session

```
a session
  that was started through a context tool
    with a working-area path
      it should expose that path for durable work
    it should create a WorkspaceRepo branch named for this session
    that the host records through eval
      it should expose eval beside workspace
      that a first-order logged tool is invoked on the host
        it should attach a ToolCall to the open Turn
        it should not close the Turn yet
      that a mistake is logged on the host
        it should record a Mistake on the open Turn through eval
      that a correction is logged on the host
        it should set Correction.improved and status=fixed on that Mistake

  that a first-order tool or action runs before the chat turn is finished
    it should attach a ToolCall to the open Turn
    it should not close the Turn yet

  that a mistake is pointed out before the chat turn is finished
    it should record a Mistake on the open Turn
    it should leave Correction open on that Mistake
    that the same Mistake is fixed in a later Turn
      it should set Correction.improved and status=fixed on that Mistake
      it should set Correction.fixedIn to the Turn that did the fix
      it should keep the same Mistake.entryId

  that an agent chat turn has finished
    with changes to the working area
      it should close the open Turn onto the Session
      it should record prompt, result, and context on that Turn
      it should commit the working-area delta on the WorkspaceRepo session branch
      it should record WorkspaceRepo commit and CDDRepo branch/SHA on that Turn
      it should save session.yaml
    with no changes to the working area
      it should discard the open Turn
      it should not create a WorkspaceRepo commit
```

## Grill log

- Theme ready to code; ArchivePromoter scaffolded for later
- Open Turn while work is in progress; finishTurn closes or discards
- Mistake.correction.fixedIn → fixing Turn
