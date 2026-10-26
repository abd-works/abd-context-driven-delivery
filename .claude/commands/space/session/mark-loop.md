Mark the next loop in the open session log (slash ``/mark-loop``).

Pass ``conversation_id``, ``transcript_path``, and ``transcript_lines`` (cumulative JSONL
range for this chat). Dispatch logs ``session.mark_loop``; the ``--- N`` marker carries the
same pointer when chat is bound.

Use MCP tool: `session.mark_loop(conversation_id: 'str' = '', transcript_path: 'str' = '', transcript_lines: 'str' = '')`
