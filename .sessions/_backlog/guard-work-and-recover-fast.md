# Guard Work And Recover Fast

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** a person sees at once when cdd is down, fixes it from where they are, and the agent is stopped before it breaks a rule.

**Slicing notes:** mod-ideas build order 1, server health band and rule guards: small, and they fix problems that already happened.

## Notes from the backlog

From `mod-ideas.md`, its opening:

> Claude Code mods that would make CDD better. Each one was checked against the repo and the mod API types of Claude Code 2.1.309. Nothing here is built or proven on a real pane unless it says so.
>
> A mod owns no domain logic. It changes what a person sees beside the chat and what the agent is told. Under the `cdd-claude-mod` pattern, stage rules and word lists live in Python, and the mod displays and calls them, so the rules stay available to Cursor, where mods do not run.

From `mod-ideas.md`, build order 1, "Server health band and rule guards. They are small and fix problems that already happened":

> **Server health band.** A session lost its `cdd` server and the board simply failed. Show that `cdd` is disconnected and how to fix it as soon as a call fails. This also enforces the MCP fail-loud rule.
>
> **Rule guards.** Use `tool.call` to refuse what the rules already forbid, and give the reason: editing `.claude/` or `.mcp.json`, writing `AGENTS.md`, or running a bare `git stash`. A hard refusal is more reliable than hoping the agent remembers the rule.
>
> **Stage guard.** Warn when work runs ahead of the active ticket's fidelity, such as production code while the ticket is in Discovery.
>
> **Banned word check.** Catch the writing-guidelines banned words in `.md` writes before they reach the file.
>
> **Branch guard.** Warn before a commit when the branch does not match the active ticket's session.

Built today: the chat bar's server health mark and panel, reconnect and reinstall (Check CDD Server Health In Chat Bar).

From `chat-enhancements.md`, "button in chat ui":

> - checkout latest and build
> - restart buttons on panel
> - click on app in helath bar

Requested on 2026-11-10: clicking an app in the chat bar starts it when it is down and opens it when it is up (Open App From Health Panel).

From `board-enhancements.md`: "restart refresh ->onre button relopadsplugins mcp everything!@".

## Epic: Move Work Forward From Chat Bar

### Feature: Guard Work Against Rules

#### Story: Refuse Forbidden Edits

*Claude Code*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Rule guards"): `tool.call` refuses edits to `.claude/` or `.mcp.json`, writes to `AGENTS.md`, and a bare `git stash`, and says which rule forbids it.

#### Story: Warn When Work Outruns Fidelity

*Claude Code*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Stage guard"): a warning shows when work runs ahead of the active ticket's fidelity, such as production code while the ticket is in Discovery.

#### Story: Catch Banned Words In Markdown

*Claude Code*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Banned word check"): a markdown write that uses a writing-guidelines banned word is caught before it reaches the file.

#### Story: Warn On Branch Mismatch

*Claude Code*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Branch guard"): a warning shows before a commit when the branch does not match the active ticket's session.

## Epic: Move Work Forward On Session Board

### Feature: Check CDD Server Health On Board

#### Story: Open Board Server Health Panel

*Person*. Requested (2026-11-06, as the Chat Bar does): a panel listing MCP host, Tools, Kanban app, Graph app and Hook server, or what is wrong.

#### Story: Reconnect CDD Server From Board

*Person*. Requested (2026-11-06, as the Chat Bar does): the board retries `cdd` and reads the board again. Built today (checked 2026-11-10): the board reads itself again every 2 s while cdd is down (`board-page-view.tsx:22`) and the board server opens a new session on the next call after a restart (`cdd-connection.ts:125`). Missing: a Reconnect button.

#### Story: Reinstall CDD Tools From Board

*Person*. Requested (2026-11-06, as the Chat Bar does): the board runs the installer and says installing, installed or failed.

#### Story: Reload Everything With One Button

*Person*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "restart refresh -> one button reloads plugins mcp everything"): Update also reloads the Claude Code plugins and the cdd server, so one press brings every part to the new code. Built today (checked 2026-11-10): Update pulls the code, pins and restarts the cdd server, reinstalls the cdd-board plugin, rebuilds the page and restarts the board server (`board-update.ts:59-62`). Missing: reloading the plugins in open chats, and reinstalling skills, rules and commands.

## Epic: Move Work Forward From Chat Bar

### Feature: Check CDD Server Health In Chat Bar

#### Story: Update CDD From Chat Bar

*Person*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "checkout latest and build"), and Requested on 2026-11-06 as the CDD Kanban does: get the latest commit, rebuild the board, pin the cdd server to that commit, and restart the board.

#### Story: Restart Parts From Chat Bar

*Person*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "restart buttons not on panel"): the restart controls sit on the chat bar itself, not only inside the server health panel.

#### Story: Open App From Health Panel

*Person*. Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "click on app in health bar"): pressing the Kanban app or Graph app in the server health panel opens that app. Requested (2026-11-10, "clicking on app in chat ui starts it if down, opens it if up"): pressing an app that is not running starts it and then opens it; pressing one that is running opens it. Built on branch `open-app-from-health-panel` (ticket `open-app-from-health-panel`).
