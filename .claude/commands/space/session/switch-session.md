Switch to an existing CDD session and set it current on disk.

Ask the user for the session name when it is not already clear from the chat.
Call MCP ``session.switch`` with that name (paths optional — loaded from the session folder).
Do not call ``session.open_named``.
