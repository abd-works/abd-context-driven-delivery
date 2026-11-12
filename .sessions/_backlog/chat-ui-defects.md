# Chat UI defects

Each defect a person reported in the chat UI, and where it stands.

## A diagram not drawn yet opens empty in draw.io

Reported 2026-11-12. The chat bar's files view listed `.context/modules.drawio` for Clean Engineering modules and offered
Open in draw.io, which opened an empty diagram: the fidelity declares the file, but no one had drawn it.

Fixed on branch `class-diagram-improvements`: each tab carries whether its file exists, and a diagram not drawn yet says
"… is not drawn yet." with no Open in draw.io button (`harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx`).

## Opening a ticket from the chat bar: "you are on Remote Control", no chat started

Reported 2026-11-12, several times. Opening a ticket from the main chat's chat bar types a request into the main chat
asking its agent to start the ticket's chat with `start_session`. The desktop app refused it each time, saying the person
is working over Remote Control, though they were at the desktop.

Cause: Remote Control is switched on for the main chat (`remoteControlActive: true`). With it on, the app cannot tell
whether a message it did not see the person type came from the desktop or a phone, so it refuses to start a session from
a message the chat bar typed. A message the person types themselves starts it.

Open: turn Remote Control off on the main chat while working at the desktop, or have the chat bar start the chat some way
that does not depend on the agent's turn.
