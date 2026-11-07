# Keeping the session log

The session owns logging once `sessions.switch` has run.

**Chat pointers.** Every log line ends with a pointer to the chat that caused it: the chat id, the agent transcript JSONL path, and the transcript line range (`{id} {transcript} {lines}`), or `no-chat` when no chat can be named. Pass `conversation_id`, `transcript_path`, and `transcript_lines` on any MCP tool call; the server takes them off the call, and every line that call writes points at that chat. A Claude Code chat may pass `conversation_id` alone, and its transcript is found by that id. On a long thread, give an accurate slice for this turn or a cumulative range (for example 1-1152, then 1-1450), so `read_loop` can put the whole dialogue of the loop under its lines. When an earlier line is missing its chat, use `session.append_log` (`/append-log`); never edit `session.log` by hand.

**Loops.** Call `session.mark_loop` (`/mark-loop`) with the chat fields on that call, so the `--- N` marker carries the chat's pointer and ties the loop to the transcript. Keep logging the loop's actions with the same chat id and growing line ranges, so `read_loop(number)` puts the matching transcript under every line of the loop. `sessions.switch` starts a new session's log with `--- 1`.

**Where lines come from.** Every tool call the MCP host serves writes a `tool` line. A guidance action writes its own line, and Validate writes one line per practice it checked. Each failed action or MCP call writes an `error` line that points at its full trace in `session.err`. Hooks do not write `session.log`. Add a line yourself only when a line lacks detail. When the user corrects the agent's behaviour or output, call `session.append_log` with the note, the loop when it is not the latest, the paths it concerns, and the chat fields.

**Session artifacts.** Write every large or temporary output (graph JSON, MCP dumps, probe results) under the session's folder, not only under the IDE's agent-tools folder, and list those paths on `append_log`, so the next agent finds them beside the log.

**Permanent artifacts.** Fidelity outputs belong to the folder the session was opened on, its workpath, and sit at the repository root only when the session names no folder. Markdown and drawio go in that folder's `.context/`; code goes straight in that folder.
