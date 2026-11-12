# Chat UI defects

Each defect a person reported in the chat UI, and where it stands.

## A diagram not drawn yet opens empty in draw.io

Reported 2026-11-12. The chat bar's files view listed `.context/modules.drawio` for Clean Engineering modules and offered
Open in draw.io, which opened an empty diagram: the fidelity declares the file, but no one had drawn it.

Fixed on branch `class-diagram-improvements`: each tab carries whether its file exists, and a diagram not drawn yet says
"… is not drawn yet." with no Open in draw.io button (`harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx`).
