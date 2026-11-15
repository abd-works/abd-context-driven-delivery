# Replace cdd polling with events

The chat bar and the apps learn about changes in cdd by polling it on timers. That makes them slow to sync and keeps the shared cdd server busy for nothing.

Today:
- The chat bar checks in every second while active and every 5 seconds while idle.
- The chat bar reads the chat's selection (`chat.show`) every second.
- The Files app reads the session's practices and the selection every second.
- Comments being sent are read again every 2 seconds.

Replace these timers with events that cdd pushes when state changes, such as a stream per chat or session (server-sent events or a websocket from the cdd server). The chat bar and every page would redraw at once, and the server would only work when something actually changed.

Covers:
- The chat's one selection (`Chat.select`).
- Its commands (`Chat.send`).
- The session's practices turned on or off.
- File comment states.
- Board refreshes.

Requested by the person on 2026-11-15, after the Files app and chat bar selection sync felt slow.
