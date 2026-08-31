# `hook_test/` — Cloud-Agent hook tester

A small Python-based tester that wires up every Cursor hook that runs in
Cloud Agents (see `cursor.com/docs/hooks#cloud-agent-support`), records every
firing to disk, and demonstrates each of the visible "notification" channels
a hook can produce inside a Cloud Agent run.

Cloud Agents have **no desktop notification system, no toast, no popup, and no
IDE Hooks output channel that you can click on.** So when we say
"notifications", we mean *any observable signal, produced by the hook, that
proves it fired*. The tester exercises all of them.

## What notifications can a hook produce in a Cloud Agent?

| Channel | What it looks like | Which hooks can produce it |
|---|---|---|
| **File log** (`hook_test/logs/events.jsonl` + `pretty.log`) | Structured JSON line + human summary. Read with `python3 hook_test/view_events.py`. | Every hook. Always on. |
| **Hook stderr** (`sys.stderr` from the hook process) | Text prefixed `[hook_test]`. Visible in the Cursor Hooks output channel in the IDE; in Cloud Agents it's captured with the hook's process output. | Every hook. |
| **`permission: "deny"` + `user_message`** | Visible message shown to the user (rendered as a "hook blocked X" note in the chat/transcript). The action is blocked. | `beforeShellExecution`, `beforeReadFile`, `preToolUse`, `subagentStart`. |
| **`agent_message` on deny** | Text fed back into the model's context as feedback about the blocked action. The agent will visibly react to it in its next turn. | `beforeShellExecution`, `preToolUse`. |
| **`additional_context`** | Extra string injected into the conversation after a tool result. Appears in the transcript as context attached to the tool output. | `postToolUse`. |
| **`followup_message`** | Auto-submits as the next user message. Shows up in the transcript exactly as if a user had typed it. Bounded by `loop_limit`. | `stop`, `subagentStop`. |
| **`continue: false` + `user_message`** | Blocks the user prompt from ever reaching the model; the user sees the message. | `beforeSubmitPrompt`. |
| **`user_message` on compaction** | Shown to the user when the context window is compacted. | `preCompact`. |
| **`updated_input`** | Replaces the tool call's arguments before execution. Observable by comparing the transcript's requested tool call to the tool's `tool_input` in `postToolUse`. | `preToolUse`. |

Notes and gotchas:

* Cloud Agents may start in a **read-only** exploratory phase; hooks do not
  run during that phase. Once the environment is writable the hooks engage.
* `permission: "ask"` is not enforced for `preToolUse` and is treated as
  `deny` for `subagentStart`. This tester does not use `ask`.
* MCP hooks (`beforeMCPExecution` / `afterMCPExecution`), `sessionStart`,
  `sessionEnd`, `workspaceOpen`, and the Tab hooks are documented as
  **not supported in Cloud Agents** and are therefore not wired here.

## Layout

```
hook_test/
├── README.md              (this file)
├── hook_lib.py            shared helpers: read stdin, record events, emit JSON
├── hook_logger.py         entry point invoked by every hook (argv[1] = hook name)
├── view_events.py         read-only CLI for the event log
├── logs/                  events.jsonl + pretty.log (auto-created)
└── demo/
    └── run_demos.py       triggers each notification channel deliberately
```

The wiring itself lives at `/.cursor/hooks.json` in the repo root, because
Cursor loads project hooks from `<repo>/.cursor/hooks.json` only.

## How to use

The hooks fire automatically once the config is loaded. You do not need to run
anything to arm them.

**Just look at the log after normal agent work:**

```bash
python3 hook_test/view_events.py             # pretty summary
python3 hook_test/view_events.py --counts    # per-hook counts
python3 hook_test/view_events.py --tail 5    # last 5 events as full JSON
python3 hook_test/view_events.py --hook stop # only stop events
python3 hook_test/view_events.py --clear     # wipe the log
```

**Deliberately fire every visible notification channel:**

```bash
python3 hook_test/demo/run_demos.py
```

Or one at a time:

```bash
python3 hook_test/demo/run_demos.py log      # plain logging
python3 hook_test/demo/run_demos.py stderr   # write to stderr from the hook
python3 hook_test/demo/run_demos.py deny     # emit permission=deny + user_message
python3 hook_test/demo/run_demos.py ctx      # inject additional_context
python3 hook_test/demo/run_demos.py edit     # trigger afterFileEdit
```

## Safety

The tester is **passive by default**: every hook returns `allow` /
`continue: true` / no follow-up unless the payload contains an explicit
marker string:

* `HOOK_TEST_MARKER_DENY` → `permission: "deny"` (with `user_message` +
  `agent_message`)
* `HOOK_TEST_MARKER_CTX`  → `postToolUse` returns `additional_context`
* `HOOK_TEST_MARKER_STDERR` → hook writes an `[hook_test]` line to stderr
* `HOOK_TEST_MARKER_FOLLOWUP` (in a subagent task) → `subagentStop` returns
  a `followup_message`
* Read of any path containing `secret_do_not_read` → `beforeReadFile` denies
* Edit of `hook_test_sentinel.txt` → `afterFileEdit` writes a marker line to stderr

Any exception inside a handler is swallowed and a permissive response is
returned, so a bug here can never block real agent work. `loop_limit` on
`stop` and `subagentStop` is set to `2` to bound accidental follow-up loops.

Log files rotate at ~512 KB (one `.1` backup is kept) so a long-running
agent will not fill the disk.

## Removing it

Delete `hook_test/` and `.cursor/hooks.json`, or edit `.cursor/hooks.json`
to remove the hooks you no longer want.
