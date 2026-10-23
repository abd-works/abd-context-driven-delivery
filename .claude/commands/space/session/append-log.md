Append a correction or audit note to the open session log (slash ``/append-log``).

**Agent steps:** confirm the open session; resolve ``loop`` (argument or latest loop with
entries — use ``read_loop`` to inspect); capture conversation id, transcript JSONL path,
and line range for this turn; write a short ``note`` (what changed, ``paths``, cross-refs to
earlier ``session.log`` lines); call MCP ``session.append_log`` with those fields.

Omit ``loop`` to target the latest loop with log lines. Pass ``conversation_id``,
``transcript_path``, and ``transcript_lines`` when hook metadata is missing.
Do not edit ``session.log`` by hand.

**Session artifacts:** whenever an open session exists, write large or temporary
outputs (MCP ``graph_return_nodes`` JSON, diagnostics dumps, probe results) under
``session_path`` on that repo (e.g. ``repo/.sessions/{name}/``). Do not leave the
only copy under Cursor ``.cursor/projects/.../agent-tools``. Reference those files
in ``paths`` on this call.

Use MCP tool: `session.append_log(note: 'str', loop: 'int | None' = None, paths: 'list[str] | None' = None, conversation_id: 'str' = '', transcript_path: 'str' = '', transcript_lines: 'str' = '')`
