---
description: "Link a file in a reply by its whole path, so the link opens the file rather than a web page that asks the person to sign in"
alwaysApply: true
---

# File Links

When a reply links to a file in the project, such as a sketch, a story map, or a file just written, write the link's target as the file's whole path from the drive: `[client-testimonial-video-creator-sketch.md](C:\dev\client-testimonial-video-creator\.context\client-testimonial-video-creator-sketch.md)`, with `#L48` after it to open at a line. The chat reads a relative target, such as `.context/story-map.md`, as an address on its own web site, so the person gets a page asking them to sign in instead of the file.

Show the path from the project's root as the link's text, and keep the whole path as its target, so the reply stays short to read and the link still opens. A `.drawio` file is the exception: link it to the draw.io viewer, as the draw.io Viewer rule says, because the file view shows its XML rather than the diagram.
