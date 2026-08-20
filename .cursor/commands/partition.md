# partition

Do not run this as its own toolset.

If the chat names **one or more** context tools (for example `/stories /ddd /iterate`), run **each** named toolset **in that order** with the same action and fidelity. Do not pick only the first. If AskQuestion is needed, the user may select more than one — still run them in the order listed.

**Step 1 — Identify the context tool(s).**
Check whether one or more context tools are already in scope — passed in (path / session / toolset) or named in this chat. If one or more are found, use them. If none is found, use the `AskQuestion` tool to let the user choose:

```
Question: "Which context tool should run `partition`?"
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
For **each** selected context tool, in the order named, invoke with `action: partition` and the chosen fidelity:

```yaml
toolset: <this context tool>
context:
  fidelity: <selected fidelity>
action: partition
```

Follow that context-tool skill's instructions: run its manifest, obey `response.instructions`, then invoke via `_req.yaml` + `python -m tools run`. Then the next named tool. Do not skip remaining tools after the first. Read `examples/` before guessing field shape.

