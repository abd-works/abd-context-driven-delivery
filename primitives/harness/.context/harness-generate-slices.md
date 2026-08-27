# Harness generate slices

Deliberate cuts for engineering generate. Each slice is one turn: open → spec + code for that job → close.

Not a slice: one `describe`, one `with`, one `it`.
Not a slice: the whole sketch.

Bdd and CleanEngineering stay paired on the same slice.

| # | Slice | In | Out | Status |
|---|--------|----|-----|--------|
| 1 | **Deploy shell** | `Harness(type)` required. Generate AskQuestions (IDE, name filter). Walk `context_tools/` + `utilities/`, write each plus Harness prompts (`/deploy-harness`, `/clean-harness`), no Harness skill, no separate deploy, no confirm list, overwrite, drop stale slugs, save IDE. One source writes that one. Cursor `.cursor/` (incl. multi-folder copies). VS Code `.github/`. Claude / Codex / ChatGPT named, not implemented. | Write vehicles and bodies | **done** |
| 2 | **Write vehicles and bodies** | Default file kind from source (context tool → Skill + ContextToolBody; utility → Skill/Prompt + UtilityBody; action → Prompt + ActionBody; formats → FormatBody; tool fidelities → slim ActionBody). `@skill` `@prompt` `@instruction` on the operation. Resolve AskQuestions only on context-tool skills and action bodies. | Host lifecycle, kit merges, delete AgentSkills | **done** |
| 3 | **Replace the old host** | Lifecycle off BaseContextTool onto Generate / Validate / CreateRule / Document / Satisfy / Render. Kit merges (sketch / iterate / grill / partition / backlog). Delete `utilities/agent_skills`. `generateAgain`. `clean` `@prompt`, this IDE only. | — | |

**Not this issue:** Hook, Agent, AgentGuidance.

**Already too small (fold into 1, do not keep cutting):** `it should refuse`; `it should AskQuestion for the IDE`.
