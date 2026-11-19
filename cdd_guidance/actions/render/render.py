"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from cdd_guidance.actions.render.rendered_file import WHITEBOARD, RenderedFile
from cdd_guidance.actions.render.worker_render import WorkerRender
from harness.guidance_actions import GuidanceArg, GuidanceAction, WorkedGuidance
from harness.guidance.guidance import FidelityGuidance
from harness.guidance.practice_formats import RenderRequest
from harness.guidance.stages import TAKES_FORMATS, on_stage
from pathlib import Path

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, instructions, noSessionLog, tools
from harness.installation.files import skill
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import mcp
from harness.whiteboard import BoardLinks, Whiteboard


class BoardNotKept(LookupError):
    """A comment came from a board no whiteboard file of the session's project was published to, so no practice says
    how to answer it."""

    def __init__(self, board: str, searched: Path) -> None:
        super().__init__(f"No whiteboard file under {searched} keeps the board {board} in its whiteboards.json")
        self.board = board
        self.searched = searched


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
        """Convert already-generated content into format. Returns one result per guidance. A drawio, whiteboard, or markdown render of paths is saved beside the first path, under the name the fidelity writes that format to when the path is one of the fidelity's own files or a sketch, else under the path's own name, keeping the layout people gave a drawing already there; its result names the saved file. Any other render returns its content. After the conversion returns, follow place_rendered; for format whiteboard, then follow publish_board.
        format: the target channel, such as python, markdown, or drawio.
        paths: a file, a list of files, or a folder, named from the project's root or absolute. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP. A path that is not there, or not under the session's root, is refused, and so is an empty file.
        content: in-process text when paths is empty. Leave this empty on an MCP call.
        source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, java, javascript, json, or drawio. md is markdown. Omit source when content is already the current format, or for a file whose extension says its format, such as .drawio, .whiteboard, or .py."""
        self._work_on(guidance)

        def on(worked: WorkedGuidance) -> object:
            if isinstance(worked, str):
                return worked
            return self._render_files(worked, format, paths, source) if paths else worked.render(format, content, source)

        converted = self.work.each(on)
        self.files.wrote([result["path"] for result in converted if isinstance(result, dict) and "path" in result])
        tools(self.act_quickly)
        tools(self.place_rendered)
        if Format(format).name == WHITEBOARD:
            tools(self.publish_board)
            tools(self.record_board)
        if self._session is not None:
            tools(self.graph.refresh)
        return converted

    def _render_files(self, worked: WorkedGuidance, format: str, paths: list[str] | str, source: str | None) -> dict:
        """The render of the files at paths, saved beside them when it is a diagram or a document."""
        sources = self.files.paths_to_read(paths)
        source = source or self._format_named_by(sources)
        declared = worked.declared if isinstance(worked, FidelityGuidance) else None
        saved = RenderedFile.from_sources(sources, Format(source), Format(format), declared)
        if saved is None:
            return worked.render_files(format, paths, source)
        if not isinstance(worked, FidelityGuidance):
            return saved.save(worked.render_files(format, paths, source, saved.previous))
        return saved.save(self._drawn(worked, worked.files_to_render(format, paths, source, saved.previous)))

    def _format_named_by(self, sources: list[Path]) -> str | None:
        """The format the first source's name says it is in, for a call that names no source: a drawing, a whiteboard,
        or code, by its extension. None for a folder, and for a markdown file, which is a document or a sketch as the
        fidelity it is rendered at says."""
        first = sources[0] if sources else None
        if first is None or not first.is_file():
            return None
        named = Format.from_extension(first.suffix)
        return named.name if named.is_offered and named.group != "markdown" else None

    def _drawn(self, fidelity: FidelityGuidance, request: RenderRequest) -> dict:
        """What request renders to at fidelity: drawn by a worker process for a call that answers a chat when it is a
        diagram, whose class layout can hold the interpreter every chat shares for minutes; else in this process."""
        worker = WorkerRender(fidelity)
        if self.call is not None and self.call.request.answers_a_chat and worker.takes(request):
            return worker.render(request)
        return fidelity.render_request(request)

    @agent_instructions
    def place_rendered(self) -> str:
        """A result that names a path was saved there by render: leave it where it is, and do not write it again. A result that carries content is code: fold it into the module the sketch names when that module already has code. Keep the behavior that module already implements. Add the rendered operations and properties onto those types. Join behavior specs into the spec that module already has. When the sketch names no existing module, put each class in the practice model folder for that channel — `{practice}/model/{format}/`. Shared graph types stay on the harness knowledge graph. Do not replace an existing file with the rendered text. Do not re-render. Do not invent types. Then call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."""
        return "Leave each file render saved where it is; fold rendered code into the module the sketch names, or the practice model folder when that module is new."

    @agent_instructions
    def publish_board(self) -> str:
        """After a render to whiteboard, put each .whiteboard file on its board in Claude. A file render saved answers with board, the address kept for it in whiteboards.json beside it, and batches, the writes that put the file on that board: write each batch to the board's store with ArtifactData batch, in order. With no board, create a Whiteboard artifact titled after the file first, write the batches to its store, then call record_board with the file and the board's address, so the next render updates the same board and the Files app opens it. A render's batches change only what the render changed, so what people moved or added on the board stays. For a .whiteboard file you wrote yourself, read the address kept for it in whiteboards.json beside it; with one, read that board's store into the board as it is in Claude and write only the batches Whiteboard.batches(previous) answers against it, never rebuilding the board; with none, create the artifact, write Whiteboard.batches(), and call record_board. A comment a person later leaves on the board goes through answer_board_comment, which names the file to change and hands over the rules of the practice that draws it."""
        return "Publish each whiteboard file to its board in Claude, and record the address of a board you created."

    @mcp
    @skill
    @agent_instructions
    def answer_board_comment(self, board: str) -> str:
        """Answer a comment a person left on a board in Claude that CDD published. board: the board's address, the claude.ai artifact link the comment came from. Make the change the comment asks for in the file the board is drawn from, following the rules below, never on the board alone, which the next render would undo. Then render that file to whiteboard with paths set to it, follow publish_board, and reply on the comment's thread saying what changed."""
        drawn_from = self._drawn_from(board)
        instructions(drawn_from)
        rules = self.work.rules_to_follow
        instructions(rules)
        tools(self.render)
        tools(self.publish_board)
        return ""

    def _drawn_from(self, board: str) -> str:
        """Which whiteboard file the board was published from and the file it is drawn from, working from now on at the
        fidelity that draws it, so the rules handed over are that fidelity's."""
        board_file = self._file_published_to(board)
        relative = self._from_root(board_file)
        fidelity = self._fidelity_drawing(relative)
        if fidelity is None:
            return f"The board was published from {relative}, which no fidelity of this session draws: change the file it is drawn from."
        self._work_on(fidelity.slug)
        folder = relative.rsplit("/", 1)[0] + "/" if "/" in relative else ""
        source = fidelity.declared.file_name_beside(relative, "markdown")
        return f"The board was published from {relative}, which {fidelity.slug} draws. Change {folder}{source or 'the file it is drawn from'}."

    def _file_published_to(self, board: str) -> Path:
        """The whiteboard file of the session's project whose board is at board; refused when none was published to it."""
        root = self.session.work_root
        for record in self.session.session_files.find(f"{root.as_posix()}/**/{BoardLinks.RECORD}"):
            found = BoardLinks(record.parent).file_published_to(board)
            if found is not None:
                return found
        raise BoardNotKept(board, root)

    def _fidelity_drawing(self, relative: str):
        """The fidelity of the session's practices that writes the file at relative as its whiteboard; none when none
        declares it."""
        fidelities = (fidelity for practice in self.work.practice_set() for fidelity in practice.fidelities)
        return next((fidelity for fidelity in fidelities if fidelity.declared.includes(relative, WHITEBOARD)), None)

    def _from_root(self, file: Path) -> str:
        """file named from the folder the session works in."""
        return file.resolve().relative_to(self.session.work_root.resolve()).as_posix()

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
