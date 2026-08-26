# Harness generate slices

Deliberate cuts for engineering generate. Each slice is one turn: open → spec + code for that job → close.

Not a slice: one `describe`, one `with`, one `it`.
Not a slice: the whole sketch.

Bdd and CleanEngineering stay paired on the same slice.

| # | Slice | In | Out | Status |
|---|--------|----|-----|--------|
| 1 | **Deploy shell** | `Harness(type)` required. Generate AskQuestions (IDE, name filter). Walk `context_tools/` + `utilities/`, write each plus Harness skill + prompt, no separate deploy, no confirm list, overwrite, drop stale slugs, save IDE. One source writes that one. Cursor `.cursor/` (incl. multi-folder copies). VS Code `.github/`. Claude / Codex / ChatGPT named, not implemented. | Write vehicles and bodies | **done** |
| 2 | **Write vehicles and bodies** | Default file kind from source (context tool / utility → Skill + ContextToolBody; action / companion / scaffold → Prompt, Cursor writes a command, ActionBody; formats and CDD / tool fidelities → Prompt + FormatBody or ActionBody). `@skill` `@prompt` `@instruction` on the operation (VS Code names; optional `name`; several → each). Cursor: prompt → Command, instruction → Rule. Paths for Skill / Prompt / Command / Instruction / Rule. Resolve in every body. | Host lifecycle, kit merges, delete AgentSkills | **done** |
| 3 | **Replace the old host** | Lifecycle off BaseContextTool onto Generate / Validate / CreateRule / Document / Satisfy / Render. Kit merges (sketch / iterate / grill / partition / backlog). Delete `utilities/agent_skills`. `generateAgain`. `clean` `@prompt`, this IDE only. | — | |

**Not this issue:** Hook, Agent, AgentGuidance.

**Already too small (fold into 1, do not keep cutting):** `it should refuse`; `it should AskQuestion for the IDE`.
