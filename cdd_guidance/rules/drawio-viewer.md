---
description: "Show draw.io diagrams in the real draw.io editor inside the browser pane"
alwaysApply: true
---

# draw.io Viewer

When the user asks to see, open, or view a `.drawio` file, show it in the draw.io editor in the browser pane rather than reading its XML back to them. The chat cannot draw a diagram, and the app's file view shows only the XML.

1. Check whether the viewer answers at `http://127.0.0.1:8791/`. When it does not, start it in the background from the repository root: `python tools/drawio_viewer/drawio_viewer.py . 8791`.
2. Navigate the browser pane to `http://127.0.0.1:8791/edit?f=<path>`, with the path relative to the repository root (or absolute) and URL-encoded.
3. Show the browser pane, so the user sees the diagram without looking for it.

The editor is the real draw.io, loaded from embed.diagrams.net, and its **Save** writes back to the file on disk. When the user asks which diagrams exist, open `http://127.0.0.1:8791/`, which lists every `.drawio` file in the repository.
