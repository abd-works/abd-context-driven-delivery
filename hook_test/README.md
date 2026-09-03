# `hook_test/` — Cloud-Agent hook tester

A small Python-based tester that wires up every Cursor hook that runs in
Cloud Agents (see `cursor.com/docs/hooks#cloud-agent-support`), records every
firing to disk, and demonstrates each of the visible "notification" channels
a hook can produce inside a Cloud Agent run.

Cloud Agents have **no desktop notification system, no toast, no popup, and no
IDE Hooks output channel that you can click on.** So when we say
"notifications", we mean *any observable signal, produced by the hook, that
proves it fired*. The tester exercises all of them.

## Summary: what notifications can a hook produce in a Cloud Agent?

| Channel | What it looks like | Which hooks emit it |
|---|---|---|
| **File log** (`hook_test/logs/events.jsonl` + `pretty.log`) | Structured JSON line + human summary. Read with `python3 hook_test/view_events.py`. | Every hook. Always on. |
| **Hook stderr** (`sys.stderr` from the hook process) | Text prefixed `[hook_test]`. Visible in the Cursor Hooks output channel in the IDE; in Cloud Agents it's captured with the hook's process output. | Every hook. |
| **`permission: "deny"` + `user_message`** | Visible message shown to the user (rendered as a "hook blocked X" note in the chat/transcript). The action is blocked. | `beforeShellExecution`, `beforeReadFile`, `preToolUse`, `subagentStart`. |
| **`agent_message` on deny** | Text fed back into the model's context as feedback about the blocked action. The agent will visibly react to it in its next turn. | `beforeShellExecution`, `preToolUse`. |
| **`additional_context`** | Extra string injected into the conversation after a tool result. Appears in the transcript as context attached to the tool output. | `postToolUse`. |
| **`updated_input`** | Rewrites the tool's arguments. The tool runs with the rewritten args and the agent sees the rewritten call + its output. | `preToolUse`. |
| **`followup_message`** | Auto-submits as the next user message. Shows up in the transcript exactly as if a user had typed it. Bounded by `loop_limit`. | `stop`, `subagentStop`. |
| **`continue: false` + `user_message`** | Blocks the user prompt from ever reaching the model; the user sees the message. | `beforeSubmitPrompt`. |
| **`user_message` on compaction** | Shown to the user when the context window is compacted. | `preCompact`. |
| **`updated_mcp_tool_output`** *(MCP only)* | Would replace the model-visible MCP tool result. **Not reachable in Cloud Agents** because MCP hooks don't run there. | `postToolUse` (MCP tools only). |

Notes and gotchas:

* Cloud Agents may start in a **read-only** exploratory phase; hooks do not
  run during that phase. Once the environment is writable the hooks engage.
* `permission: "ask"` is not enforced for `preToolUse` and is treated as
  `deny` for `subagentStart`. This tester does not use `ask`.
* MCP hooks (`beforeMCPExecution` / `afterMCPExecution`), `sessionStart`,
  `sessionEnd`, `workspaceOpen`, and the Tab hooks are documented as
  **not supported in Cloud Agents** and are therefore not wired here.

## Injection-method walkthrough

Each subsection covers one method of pushing text into the running conversation
from inside a hook: what the response JSON looks like, where the injected text
lands, and how to trigger it with this tester.

### 1. `user_message` — visible chat notification

Present on: `beforeShellExecution`, `beforeReadFile`, `preToolUse` (deny),
`subagentStart` (deny), `beforeSubmitPrompt` (block), `preCompact`.

Response shape (deny variant):

```json
{ "permission": "deny", "user_message": "hook_test: blocked because ..." }
```

Where it lands: rendered as a user-facing "hook blocked X" note in the chat
transcript. The action is blocked.

Trigger with this tester: run a shell command containing `HOOK_TEST_MARKER_DENY`
inside the agent's Shell tool, e.g. `echo HOOK_TEST_MARKER_DENY`.

### 2. `agent_message` — feedback into the model's context on deny

Present on: `beforeShellExecution`, `preToolUse` (deny).

Response shape:

```json
{
  "permission": "deny",
  "user_message": "...visible to user...",
  "agent_message": "...visible to the model in its next turn..."
}
```

Where it lands: injected into the model context as feedback about the blocked
action. The agent's *next* turn will visibly react to it — a good way to steer
the agent without stopping the run.

Trigger with this tester: same as `user_message`. `hook_logger.py` sets both
fields whenever a deny fires.

### 3. `additional_context` — extra text appended after a tool result

Present on: `postToolUse`.

Response shape:

```json
{ "additional_context": "hook_test: extra context to attach after the tool result" }
```

Where it lands: appended to the tool output the model sees, right after the
Shell/Read/etc. result. Useful for "here is a lint report / coverage summary
that came from running that tool" style injection.

Trigger with this tester: run a shell command containing `HOOK_TEST_MARKER_CTX`,
e.g. `echo HOOK_TEST_MARKER_CTX`. `postToolUse` sees the marker in `tool_input`
and returns `additional_context`.

### 4. `updated_input` — rewrite a tool call before it runs

Present on: `preToolUse`.

Response shape:

```json
{
  "permission": "allow",
  "updated_input": { "command": "the rewritten command" }
}
```

Where it lands: Cursor executes the tool with the rewritten input. The agent
sees its original requested `tool_input` in the transcript and the actual
executed input via `postToolUse.tool_input`. Comparing the two proves the
hook rewrote it.

Trigger with this tester: run a shell command containing
`HOOK_TEST_MARKER_REWRITE`. The hook replaces the marker with
`REWRITTEN_BY_HOOK` and Cursor runs that version.

### 5. `followup_message` — auto-submit a new user turn

Present on: `stop`, `subagentStop`.

Response shape:

```json
{ "followup_message": "hook_test: appears in the transcript as a new user message" }
```

Where it lands: Cursor auto-submits this string as the next user message in
the conversation. It shows up in the transcript exactly as if a human typed
it, and the agent begins another turn to respond to it. The per-script
`loop_limit` (default 5, set to 2 here) bounds how many times this can fire
in one conversation.

Trigger with this tester:

* `stop`: run `python3 hook_test/demo/run_demos.py followup`. This drops
  `hook_test/state/stop_followup_pending`. On the next `stop` hook firing
  the tester consumes the flag and emits the `followup_message`.
* `subagentStop`: spawn a Task subagent whose task string contains
  `HOOK_TEST_MARKER_FOLLOWUP`. When the subagent completes, `subagentStop`
  emits the follow-up message.

### 6. `continue: false` + `user_message` — block a prompt before submission

Present on: `beforeSubmitPrompt`.

Response shape:

```json
{ "continue": false, "user_message": "hook_test: prompt blocked because ..." }
```

Where it lands: the user's prompt is discarded before it ever reaches the
model; the user sees the `user_message`.

Trigger with this tester: a *human* must type a chat prompt containing
`HOOK_TEST_MARKER_DENY`. Not reachable from inside a Cloud Agent shell demo
because the agent itself does not submit prompts.

### 7. `user_message` on compaction

Present on: `preCompact`.

Response shape:

```json
{ "user_message": "hook_test: context is being compacted (...)" }
```

Where it lands: shown to the user at the moment the context window is
compacted. `preCompact` cannot block compaction, only annotate it.

Trigger with this tester: this hook fires automatically when Cursor
compacts the context window. In practice you'll see it only during long
sessions.

### 8. Hook stderr (`[hook_test]` lines)

Any hook can write to `sys.stderr`. This tester emits `[hook_test]` lines
in a few places (marker seen, sentinel edit, tool failure). Whether the
lines are surfaced in the transcript depends on Cursor's hook transport;
they are reliably captured with the hook's process output regardless, and
in the IDE they show up in the Hooks output channel. Treat this as a
diagnostic channel, not a guaranteed in-chat notification.

### 9. `updated_mcp_tool_output` — not reachable in Cloud Agents

The docs list this as a `postToolUse` response field for MCP tools only.
MCP hooks are documented as not running in Cloud Agents, and the field is
gated to MCP tool calls specifically, so it cannot be exercised here.
Kept in this list for completeness.

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

**Deliberately fire every visible injection channel:**

```bash
python3 hook_test/demo/run_demos.py
```

Or one channel at a time (see the walkthrough section above for what each does):

```bash
python3 hook_test/demo/run_demos.py log       # plain logging
python3 hook_test/demo/run_demos.py stderr    # hook writes to stderr
python3 hook_test/demo/run_demos.py deny      # permission=deny + user_message + agent_message
python3 hook_test/demo/run_demos.py ctx       # additional_context from postToolUse
python3 hook_test/demo/run_demos.py rewrite   # updated_input from preToolUse
python3 hook_test/demo/run_demos.py edit      # afterFileEdit on the sentinel file
python3 hook_test/demo/run_demos.py prompt    # instructions for beforeSubmitPrompt block
python3 hook_test/demo/run_demos.py followup  # arm stop's followup_message
python3 hook_test/demo/run_demos.py subagent  # instructions for subagentStart/Stop channels
```

Some demos can only be triggered *by the agent itself* (deny, rewrite,
subagent). The demo script prints the marker string to hand to the agent
in those cases.

## Safety

The tester is **passive by default**: every hook returns `allow` /
`continue: true` / no follow-up unless the payload contains an explicit
marker string:

* `HOOK_TEST_MARKER_DENY` → `permission: "deny"` (with `user_message` +
  `agent_message`)
* `HOOK_TEST_MARKER_CTX`  → `postToolUse` returns `additional_context`
* `HOOK_TEST_MARKER_REWRITE` → `preToolUse` returns `updated_input` that
  rewrites a Shell command
* `HOOK_TEST_MARKER_STDERR` → hook writes an `[hook_test]` line to stderr
* `HOOK_TEST_MARKER_FOLLOWUP` (in a subagent task) → `subagentStop` returns
  a `followup_message`
* Existence of `hook_test/state/stop_followup_pending` → the next `stop`
  hook returns a `followup_message` (and the flag is deleted, so it only
  fires once)
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
