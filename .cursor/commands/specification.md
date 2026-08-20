# specification

Do not run this as its own toolset. This command sets the CDD stage to `specification`.

The context tool maps this stage name to its own concrete fidelity (Stories: discovery→story_map, specification→scenarios, engineering→acceptance_tests; CleanEngineering: discovery→modules, specification→model, engineering→code; and so on).

If the chat names **one or more** context tools (for example `/stories /ddd /iterate`), run **each** named toolset **in that order** with the same action and fidelity. Do not pick only the first. If AskQuestion is needed, the user may select more than one — still run them in the order listed.

**Step 1 — Identify the context tool(s).**
Check whether one or more context tools are already in scope — passed in (path / session / toolset) or named in this chat. If one or more are found, use them. If none is found, use the `AskQuestion` tool to let the user choose:

```
Question: "Which context tool should work at the `specification` stage?"
Options:
  - /cdd — orchestrate all child tools at one stage
  - /stories — who does what, in what sequence
  - /clean-engineering — module boundaries and OO design
  - /ux — navigation, screens, front end
  - /bdd — observable behavior and tests
  - /ddd — bounded contexts and domain building blocks
```

**Step 2 — Identify the action.**
Check whether an action was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose:

```
Question: "What action should run at `specification`?"
Options:
  - partition — index source material and extract chunks
  - grill — context-grounded Q&A
  - sketch — grill plus a persisted rough draft
  - generate — produce the formal artifact
  - document — describe existing code/tests/docs
  - iterate — generate one small slice at a time
  - validate — scan and report pass/fail
  - satisfy — validate, fix, validate again until clean
  - repair — root-cause and fix why the tool produced a violation
  - improve — log mistake, repair, capture regression
```

**Step 3 — Run the action at this stage.**
For **each** selected context tool, in the order named, invoke with the chosen action and `specification` as fidelity:

```yaml
toolset: <this context tool>
context:
  fidelity: specification
action: <selected action>
```

Follow that context-tool skill's instructions: run its manifest, obey `response.instructions`, then invoke via `_req.yaml` + `python -m tools run`. Then the next named tool. Do not skip remaining tools after the first. Read `examples/` before guessing field shape.

