---
description: "A comment from a Claude Whiteboard board CDD published goes through render.answer_board_comment, which hands over the guidance of the practice that draws the board"
alwaysApply: true
---

# Board comments

When a comment arrives from a Claude Whiteboard board, such as a turn headed `[Artifact comment sent to Claude]` on a board a render published, call the MCP tool `render.answer_board_comment` with the board's address before changing anything, and follow what it returns.

The board is drawn from a file of a practice, such as the story map's `.context/story-map.md`, and the next render draws the board again from that file. The tool names that file and hands over the rules of the fidelity that draws the board, so the change is made in the file under the same guidance that wrote it, then rendered and published back onto the board. A change made on the board alone, or made without those rules, is undone by the next render or breaks the rules the practice checks.

When the tool says no whiteboard file keeps the board, the board is not one CDD published: answer the comment as an ordinary request. When the tool fails or is missing, follow `mcp-fail-loud.md`.
