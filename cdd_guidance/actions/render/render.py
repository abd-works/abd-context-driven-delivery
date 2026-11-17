"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction, WorkedGuidance
from harness.guidance.stages import TAKES_FORMATS, on_stage
from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, noSessionLog, tools
from harness.installation.files import skill
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import mcp
from harness.whiteboard import BoardLinks, Whiteboard

@agent_toolset
class Render(GuidanceAction):
    """Render already-generated output for provided context tools."""

    @on_stage(5, TAKES_FORMATS)
    @mcp
    @skill
    @agent_tool
    def render(
        self, guidance: GuidanceArg, format: str, paths: list[str] | str, content: str = "", source: str | None = None,
    ) -> list:
        """Convert already-generated content into format. Returns one result per guidance. After the conversion returns, follow place_rendered; for format whiteboard, then follow publish_board.
        format: the target channel, such as python, markdown, or drawio.
        paths: a file, a list of files, or a folder. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP.
        content: in-process text when paths is empty. Leave this empty on an MCP call.
        source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, java, javascript, json, or drawio. md is markdown. Omit source when content is already the current format."""
        self._work_on(guidance)

        def on(worked: WorkedGuidance) -> object:
            if isinstance(worked, str):
                return worked
            return worked.render_files(format, paths, source) if paths else worked.render(format, content, source)

        converted = self.work.each(on)
        tools(self.act_quickly)
        tools(self.place_rendered)
        if Format(format).name == "whiteboard":
            tools(self.publish_board)
            tools(self.record_board)
        if self._session is not None:
            tools(self.graph.refresh)
        return converted

    @agent_instructions
    def place_rendered(self) -> str:
        """After render, fold the result into the module the sketch names when that module already has code. Keep the behavior that module already implements. Add the rendered operations and properties onto those types. Join behavior specs into the spec that module already has. When the sketch names no existing module, put each class in the practice model folder for that channel — `{practice}/model/{format}/`. Shared graph types stay on the harness knowledge graph. Do not replace an existing file with the rendered text. Do not re-render. Do not invent types. Then call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."""
        return "Fold rendered classes into the module the sketch names, or the practice model folder when that module is new."

    @agent_instructions
    def publish_board(self) -> str:
        """After a render to whiteboard, put each .whiteboard file you wrote on its board in Claude. Read the address kept for the file in whiteboards.json beside it. With none, create a Whiteboard artifact titled after the file, write the board's Whiteboard.batches() to its store, then call record_board with the file and the board's address, so the next render updates the same board and the Files app opens it. With one, read that board's store into the board as it is in Claude and write only the batches Whiteboard.batches(previous) answers against it, never rebuilding the board, so what people moved or added stays."""
        return "Publish each whiteboard file to its board in Claude, and record the address of a board you created."

    @mcp
    @agent_tool
    @noSessionLog
    def record_board(self, path: str, url: str) -> str:
        """Keep url, the address of the Claude Whiteboard board the .whiteboard file at path was published to, beside the file in its folder's whiteboards.json, so the next render updates that board and the Files app opens it. path: the whiteboard file, named from the project's root or absolute. Returns the address kept."""
        file = self.files.path_named(path)
        if file.suffix != Whiteboard.SUFFIX:
            raise ValueError(f"{path} is not a {Whiteboard.SUFFIX} file: only a {Whiteboard.SUFFIX} file is published to a board.")
        BoardLinks.beside(file).record(file, url)
        return url
