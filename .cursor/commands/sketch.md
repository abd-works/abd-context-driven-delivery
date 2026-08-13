# sketch

Do not run this as its own toolset.

**Step 1 — Identify the context tool.**
Check whether a context tool is already in scope — passed in (path / session / toolset) or named in this chat. If one is found, use it. If not, use the `AskQuestion` tool to let the user choose:

```
Question: "Which context tool should run `sketch`?"
Options:
  - /cdd — orchestrate all child tools at one stage
  - /stories — who does what, in what sequence
  - /clean-engineering — module boundaries and OO design
  - /ux — navigation, screens, front end
  - /bdd — observable behavior and tests
  - /ddd — bounded contexts and domain building blocks
```

**Step 2 — Identify the fidelity.**
Check whether a fidelity was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose from the selected context tool's available fidelities (see the quick-reference table), or from the CDD stage names (`discovery`, `specification`, `engineering`).

**Step 3 — Run the action.**
Invoke the context tool with `action: sketch` and the chosen fidelity:

```yaml
toolset: <selected context tool>
context:
  fidelity: <selected fidelity>
action: sketch
```

Follow that context-tool skill's instructions: run its manifest, obey `response.instructions`, then invoke via `_req.yaml` + `python -m tools run`. Read `examples/` before guessing field shape.

