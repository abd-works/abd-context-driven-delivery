---
description: "A comment from a Claude Whiteboard board or a design canvas CDD published goes through render.answer_board_comment, which names the file to change and hands over the guidance of the practice that writes it"
alwaysApply: true
---

# Board comments

When a comment arrives from a Claude Whiteboard board or a Claude Design canvas, such as a turn headed `[Artifact comment sent to Claude]` on a board a render published or on a version of the UX practice's design canvas, call the MCP tool `render.answer_board_comment` with the board's address before changing anything, and follow what it returns. For a design canvas, also pass `anchor`: the label of the story explorer row the comment sits on, as the comment shows it (a step's keyword and words, a scenario or story name, an outline row's example), with its location.

A whiteboard is drawn from a file of a practice, such as the story map's `.context/story-map.md`, and the next render draws the board again from that file. A design canvas is drawn from the story map, the scenarios and the UX map, and the knowledge graph links each story, scenario and step to the screens and interactions that show it, so the tool finds what the anchor names, the scenarios file and line that hold it, and the screens that show it. Either way the tool names the file and hands over the rules of the fidelity that writes it, so the change is made in the file under the same guidance that wrote it, then rendered and published back. A change made on the board alone, or made without those rules, is undone by the next render or breaks the rules the practice checks.

When the tool says no whiteboard file or design canvas version keeps the board, the board is not one CDD published: answer the comment as an ordinary request. When it says the anchor names nothing on the graph, refresh the graph with the story files, or answer the comment as an ordinary request. When the tool fails or is missing, follow `mcp-fail-loud.md`.
