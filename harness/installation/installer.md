# Installer

## Install

Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks. `replace` wipes files from the previous install first.

Use slash **`/install`** (command — not a skill, not MCP). Deployed **commands** and **skills**:

- ``@agent_instructions`` with ``@mcp``: short docstring in the slash/skill file; MCP invoke tail (full instructions stay on the MCP prompt).
- ``@agent_tool`` **without** ``@mcp``: Shell invoke tail — ``scripts/{deploy_name}.py`` when present, else ``python -c`` via ``AgentToolSet.instantiate`` (e.g. ``/install`` → ``scripts/install.py``).
- ``@agent_tool`` **with** ``@mcp``: MCP invoke tail on the same skill/command file (no Shell tail).

Every full install also re-deploys the Installer toolset last so the slash commands stay current.

A toolset annotated ``@language_adapter(language="typescript")`` also gets typed code under ``{install_path}/language-adapters/typescript/``, in the folders its source sits in: its data, a class that reads it, and a class that calls its MCP tools. `clean` removes these with the rest of the install, and `patterns-cdd-web-domain-access` says how applications use them.

Every chat in every project talks to **one cdd server**, installed once under `~/.cdd/`. Install writes the IDE's user-level `cdd` entry as that server's URL, starts the server when none answers, and pins it to this checkout's current commit only on the very first install. A later install from any worktree leaves the serving code alone, so it never repoints every open chat at that worktree. To change what serves every chat, say so: `python scripts/install.py --pin-runtime` serves this checkout's current commit, and `python scripts/install.py --serve-from-checkout` serves this checkout as it is on disk, for working on CDD itself; after editing Python there, `cdd.restart` reloads it for every chat.

When install runs **inside** the cdd server itself, the installer skips standing up a second MCP host and starting the server, so it does not reload every toolset during an unrelated tool request.

**After install finishes, read the diagnostic report back to the user.** `install` always runs `diagnose_after_install` (install-channel counts and runtime status only) and appends to `{install_path}/diagnostics.json` (for this repo, `.cursor/diagnostics.json`). It does not run guidance instruction or action probes — use `/guidance-diagnostics` for those. The CLI only prints reports that start with `!` (red); green and yellow stay in the log. Open the latest `installs[]` entry: give the overall `color`, paste the full `diagnose_install` `report` (channel deltas, any new/deleted items, **cdd server**, **hook server**, **hooks registered (events)**, **hook handlers (operations)**), and call out red or yellow. If you ran install in the shell, read that file or run `Installer(...).diagnose_install()` against the same install path — do not leave the user without the summary.

### When install fails

Treat every failed install as evidence, whoever ran it: `/install`, `python scripts/install.py` in a shell, the chat bar's **Run install**, or a reinstall another fix asked for. The same few causes come back across chats and weeks (a stale pinned runtime, a locked file, a missing header, a server that will not start), and they only show up as themes when every failure is written down in the same place.

1. **Log it in the session folder.** Append one entry to `install-failures.md` in the open session's folder, `.sessions/{session}/` at the repository root (`.sessions/main/` when no ticket session is open). Create the file when it is missing. Each entry holds:
   - the date and time, and who ran it (which command, from which chat or button);
   - the checkout it ran from, its branch and commit, and the commit in `~/.cdd/runtime.json`;
   - the error: the exception name and message, and the last lines of output that explain it, quoted as they appeared;
   - what you tried, and whether it cleared the failure; fill this in once you know.
   Log the failure before you start fixing it, so a fix that takes the chat somewhere else does not lose it.
2. **Hand the error to diagnostics.** Run `/harness-diagnostics-agent-tools-diagnostics` (MCP `agent-tools-diagnostics.agent_tools_diagnostics`) with the error in hand, and read its results under `agent_tools` in `diagnostics.json` in the install folder (`.claude/` or `.cursor/`). When the cdd server is itself what the install broke, the MCP call fails too: say so, as `mcp-fail-loud` asks, and carry on with step 3 from the logs alone.
3. **Look for themes across time.** Read every `install-failures.md` under `.sessions/` and `.sessions/_complete/`, the `installs[]` and `agent_tools` history in `diagnostics.json`, and the diagnostics you just ran. Group the failures by cause, not by wording: two stack traces from the same stale runtime are one theme. For each theme, record how often it happened, when it was first and last seen, which commits it spans, whether a fix held, and the fix that worked. Keep the result in `.sessions/_backlog/install-failure-themes.md`, updating the themes already there rather than starting a new list, so the history stays in one file.
4. **Tell the person.** Report this failure, the theme it belongs to (or that it is new), and the fix that has worked before. When a theme keeps coming back after its fix, say so and propose fixing the installer or server code itself, because another manual workaround will only add another entry.

## Clean

Remove files written by the previous install for this IDE path. Slash **`/clean`** — same automatic Shell tail (``@agent_tool`` without MCP).

## Diagnose Install

Compare this install with the last entry in `diagnostics.json` on the install path. Report green, yellow, or red, each channel as previous -> current (delta), every new or deleted item, whether the cdd server and hook server are running, and which hook events and handler operations are registered on the install path.

`diagnose_after_install` is the last install step. It runs `diagnose_install` and appends one install section to `diagnostics.json`.

- Green: surface change is at most 10%.
- Yellow: surface change is at most 50%.
- Red: majority of the surface changed. The result starts with `!`, shows each channel delta, and these instructions.

When the result is red, do not treat the last install as wrong until you look:

1. Read the last install in `diagnostics.json` for the channel whose delta is largest.
2. Compare its `items` with the install tree: `skills/**/SKILL.md`, `commands/` or `prompts/`, `rules/**/*.mdc`, `hook-handlers.json`, and the MCP operations recorded for this install.
3. Check whether this install replaced a prior publish or kept it.
4. Check whether a toolset that should deploy was skipped, or an examples toolset was collected.
5. The next install appends another section — do not rewrite the trail.

Guidance instruction and action probes live on `/guidance-diagnostics`, not on install.

## Agent tools diagnostics

Probe **space**, **harness**, and **tools**: ping on the live MCP host; light + heavy invoke in a child process ([`cdd-diagnostic`](https://github.com/abd-works/cdd-diagnostic) fixtures). Results in `diagnostics.json` → `agent_tools`. Slash **`/agent-tools-diagnostics`** → MCP `agent-tools-diagnostics.agent_tools_diagnostics`.

## Ensure Runtimes

Start the hook daemon and MCP host; fail if either stays down.
