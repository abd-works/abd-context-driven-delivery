# Harness generate slices

Deliberate cuts for engineering generate. Each slice is one turn: open → spec + code for that job → close.

Not a slice: one `describe`, one `with`, one `it`.
Not a slice: the whole sketch.

Bdd and CleanEngineering stay paired on the same slice.

| # | Slice | In | Out | Status |
|---|--------|----|-----|--------|
| 1 | **Construct and ask** | `Harness(type)` required. Generate with no IDE / no name filter AskQuestions, then construct. | Walk, write files | **done** |
| 2 | **Generate is the deploy** | No source: walk `context_tools/` + `utilities/`, generate each, also write Harness skill + prompt, no separate deploy, no confirm list, overwrite, drop stale slugs, save IDE. With a source: write that one. Cursor `.cursor/` (incl. multi-folder copies). VS Code `.github/`. Claude / Codex / ChatGPT named, not implemented. | Source-kind defaults | **done** |
| 3 | **Default file kind from source** | Context tool / utility → one Skill, ContextToolBody. Action → Prompt (Cursor writes a command). Companions (echo, handoff, backlog, start, finish), scaffold (not a fidelity), format prompts, CDD stage + tool fidelity prompts. | Decorators | |
| 4 | **Annotations and write vehicles** | `@skill` `@prompt` `@instruction` on the operation (VS Code names only). Several → write each. Optional `name`. Cursor: prompt → Command, instruction → Rule. Skill / Prompt / Command / Instruction / Rule paths. | Bodies | |
| 5 | **Bodies and Resolve** | ContextToolBody, ActionBody (locked recipe), FormatBody. Resolve: no required pairing; confirm when taken from context; guess+confirm wrong fidelity; AskQuestion constrained to this source; then CLI. | Host move | |
| 2 | **Lifecycle off the host** | BaseContextTool keeps `guidance` (contexts, examples, templates). Drop generate / validate / document / satisfy / createRule / render / scan / turn tools from the host. New actions: Generate, Validate, CreateRule, Document, Satisfy, Render — each runs on each provided context tool. Refactor existing specs onto those classes. | Kit merges | |
| 3 | **Kit merges** | Sketch includes `sketch_session`. Iterate includes `iterate_session`. Grill includes `grill_with_context`. Partition includes `partition_corpus`. Workflow backlog includes `handoff_tool`. start/finish stay `@agent_tool`. | Replacement | |
| 3 | **Replace AgentSkills** | Delete `utilities/agent_skills` as deploy owner. `generateAgain` (saved IDE, no questions; refuse if none). `clean` is `@prompt`; this Harness type’s deploy area only. | — | |

**Not this issue:** Hook, Agent, AgentGuidance.

**Already too small (fold into 1, do not keep cutting):** `it should refuse`; `it should AskQuestion for the IDE`.
