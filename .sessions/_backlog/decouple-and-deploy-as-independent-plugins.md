# Decouple And Deploy As Independent Plugins

**Outcome:** parts of CDD can be installed and used on their own, without the whole toolset, so more people try them and we gather more evidence of what works.

**Why:** offering smaller pieces by themselves will probably increase adoption and improve the evidence we get back.

## Candidate plugins

### Simple command bar
A command bar on its own that creates a chat, creates a worktree, hands off a session, and opens a files viewer.

### Command bar with stages and actions
A generic version of the stages and fidelities: a person defines their own stages and actions, and each action points to one of:
- an MCP call
- a slash command (`/whatever`)
- a markdown file
- a code function

Also includes the summary below the chat card.

### Diagnostics panel
A person names the services they want running and the scripts that start them; the panel shows whether each is up and starts the ones that are not.

### Configurable bar
A bar defined in JSON: list boxes, toggles, and click buttons. Open questions:
- how a person configures custom logic behind a control — the same way as the workflow above (MCP call, slash command, markdown file, code function), or AI-assisted
- data sources that feed the controls (e.g. a list box filled from an MCP call)

## Notes
- Each plugin needs its seams pulled out of `harness/`, `space/`, and the chat-ui plugin so it installs without the rest.
- Raw request (2026-11-11): "decouple and deploy as independant plugins … simple command bar … command bar stages and actions … diagnostics panel … configurable bar".
