# mod-ideas

Claude Code mods that would make CDD better. Each one was checked against the repo and the mod API types of Claude Code 2.1.309. Nothing here is built or proven on a real pane unless it says so.

A mod owns no domain logic. It changes what a person sees beside the chat and what the agent is told. Under the `cdd-claude-mod` pattern, stage rules and word lists live in Python, and the mod displays and calls them, so the rules stay available to Cursor, where mods do not run.

## Build order

1. Server health band and rule guards. They are small and fix problems that already happened.
2. Command entry and autocomplete.
3. Mini panel above the chat bar, with next-step suggestions.
4. Finish the Kanban alongside all of these.

## Original four

### Kanban and session tracking

`cdd-board` in `harness/kanban/pane` already has the Board pane, toasts, the status line, the violations band, and `/board` and `/ticket`. It still has layout gaps against the Claude Design canvas. Content tracking can build on `ticket.files` and `ticket.report`.

### Command entry and autocomplete

The `prompt.autocomplete` event adds suggestions to the typeahead as you type, so it can offer an action, then a practice-fidelity, then content or a file. `argumentHint` shows the expected parameters after a command's name. Take the options from the CDD catalog so they cannot drift from what is installed.

### Hooks and notifications

Toasts exist only for ticket moves and finished fidelities. `tools/prompt_notify` writes a toast file for Cursor only. Port "which action or practice just ran" to `$.ui.toast`, and use `tool.call` to react to every CDD call. `$.audio.play` is available for sounds.

### Mini panel above the chat bar

The `AbovePrompt` band exists but shows only violations. Make it always on, with the session, a breadcrumb of stage, practice, and fidelity, the violation count, and buttons for next, validate, and handoff.

## Reliability and guardrails

### Server health band

A session lost its `cdd` server and the board simply failed. Show that `cdd` is disconnected and how to fix it as soon as a call fails. This also enforces the MCP fail-loud rule.

### Rule guards

Use `tool.call` to refuse what the rules already forbid, and give the reason: editing `.claude/` or `.mcp.json`, writing `AGENTS.md`, or running a bare `git stash`. A hard refusal is more reliable than hoping the agent remembers the rule.

### Stage guard

Warn when work runs ahead of the active ticket's fidelity, such as production code while the ticket is in Discovery.

### Banned word check

Catch the writing-guidelines banned words in `.md` writes before they reach the file.

### Branch guard

Warn before a commit when the branch does not match the active ticket's session.

## Flow

### Next-step suggestion

After each turn, use `$.prompt.suggest` to pre-fill the next command from `ticket.generate_commands`.

### Validate on save

When an artifact in a session changes, run the graph rules and update the band.

### Automatic handoff

Write the handoff when a session ends, so the next session never starts cold.

## Capturing knowledge

### Correction capture

Use `$.model.classify` to spot when the user is correcting generated work, then offer to add it to `corrections.log`. Do the same for decisions and offer a CDR.

## Views

### Trace pane

Pick a story and see its scenarios, tests, and code from `harness/graph`, plus the domain, class, and bounded-context diagrams wanted on the canvas.
