---
name: stories
description: "Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# Stories

This skill **is** this context tool. Do not ask which context tool to run.

**Step 1 — Identify the action.**
Check whether an action was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose:

```
Question: "What action should Stories run?"
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

**Step 2 — Identify the fidelity.**
Check whether a fidelity was provided alongside this command (in the user message or chat context). If one is found, use it. If not, use the `AskQuestion` tool to let the user choose from this tool's available fidelities or from the CDD stage names (`discovery`, `specification`, `engineering`).

**Step 3 — Run the manifest and invoke.**
Load this tool's manifest:

```
python -m tools manifest context_tools.stories.stories:Stories
```

Follow `response.instructions` before doing anything else. Write the request to
a YAML file (e.g. `_req.yaml`) and run:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format:

```yaml
toolset: context_tools.stories.stories:Stories
context:
  fidelity: <selected fidelity>
action: <selected action>
```

Read `examples/` before guessing any field shape.
