# Handoff format

A handoff is drafted from the conversation, tailored to the next focus when one is given.

Use this exact structure:

# Handoff — {one-line description} ({today ISO date})

## Outcome
One paragraph: what this session actually achieved and where the next session starts.

## Progress
Keep this section terse. Do not write long essays.

### Files
Short bullet list of created or modified files — relative paths plus a few words each.

### Outstanding
Short bullet list of remaining work, failures, and partial items.

## Key Learnings
Do not cross-check AGENTS.md or dump every learning. List only the most important rules / corrections from the corrections document: rule name + star count, optionally the session delta. One line per rule. If every learning is already in that file, the list of top rules is still required — do not write "All captured. No new items." as a substitute.

Find the corrections document in this order:
1. Assume it is in the current session folder (e.g. `.sessions/{name}/corrections.md` or a path the session already uses).
2. If not found, search the sessions root (`.sessions/corrections.md`, `.sessions/**/corrections.md`).
3. If still not found, look under `.sessions/main/`.
4. Also try the durable project location `.context/corrections.md` if the session copies are missing.

Read the current session block first (the latest `# Session: YYYY-MM-DD` heading). Prefer rules that appear in that block, ordered by star count.

## Approach for Next Agent
Analyse the chat and/or the user's instructions for a deliberate numbered loop whose steps are context tools plus their parameters. Extract the actual slash-command / tool+parameter sequence used or instructed in this session. Do not invent a generic software process.

Examples of the style (replace with the sequence from this session):
- `/stories-scenarios` `/generate` `/markdown`
- `/clean-engineering-model` `/generate` `/markdown`
- `/stories-acceptance-tests` `/clean-engineering-code` `/generate` `/code`

Include:
- Read this handoff and the corrections document (session block first) to orient.
- The numbered context-tool loop extracted from this session.
- If a skill conflicts with corrections.md, follow corrections.md.
- A start-at pointer for the next agent.
- Corrections CLI commands if a `corrections-cli` exists in the project.

## Guidance To Read First
List the practice guidance the next agent reads, and applies, before generating anything: a scenario, a test, code, a model, or a document. Name each file by its path. Take them from the session: every practice and fidelity it has on (its `session.json` practices and the board's active fidelities), the supplements that apply to them, and any pattern overlay the session uses.

- Each practice's guidance at the fidelities the work touches: `cdd_guidance/practices/{practice}/{practice}.md` (its shared rules and that fidelity's section), such as `stories/stories.md` for scenarios and acceptance tests, and `clean_engineering/clean_engineering.md` for code.
- The TDD supplement, `cdd_guidance/practices/tdd/tdd.md`, whenever the work writes tests or code: say which flow each change is in (Flow A, a boundary crossed for the first time: run it for real end to end and have the person verify it before the stubbed unit tests; Flow B, a known area: a failing unit test first, then the code, then heavy and e2e tests handed to a background agent), and the tiers and budgets the tests go in.
- The pattern overlays the session applies (`.context/patterns.md` where the work writes) and the module's own `.context/module-context.md`.
- The person's corrections from this session that change how the guidance is applied.

Write it as an instruction, not a reading list for later: the next agent reads these and says which flow and which rules apply before it writes the first scenario, test, or line of code, because work generated before reading them has to be redone.

## Where The Work Goes Live
Say how the next agent puts finished work in front of the person. Pick the steps from the session's branch, not from habit:
- **A ticket's branch, in its own worktree** (any branch but main): commit and push each finished step to that branch, then repin the dev lane to the branch tip with `python scripts/install.py --ide Claude --pin-runtime` from the worktree, and run `app.open` for each app the step changed (Files, Kanban, Story UI), so its server rebuilds and restarts on the dev lane. Message only the sessions that use the dev lane before the repin; skip the message when none runs.
- **main, in the main checkout**: commit and push to main, then repin the stable lane with the same command from the main checkout, after messaging the sessions that use the stable lane.

Never list a merge to main as a next step, a question to ask, or an outstanding item for a ticket's branch: the dev lane is where a ticket's work runs. Merge a ticket's branch to main only when the person asked for that merge in their own words, and say so with their words when the handoff carries it.

## Correction trend
Include this section only if the corrections document was found. Compare this session's correction count (from the session block / conversation) to the previous session's count. State the trend in 1–2 sentences (e.g. "Session 2026-09-14 needed 5 corrections across 2 epics — roughly 2–3 per story. The previous session needed ~12. Trend is sharply down."). Optionally append the Corrections CLI cheat sheet (`list`, `add-correction`, `new-session`). If corrections cannot be found after the search order above, omit this section.
