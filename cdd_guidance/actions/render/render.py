"""Render — convert already-generated content on each listed guidance."""

from __future__ import annotations

from cdd_guidance.actions.render.rendered_code import RenderedCode, RenderHasNoDeclaredPlace
from cdd_guidance.actions.render.rendered_file import SAVED_GROUPS, WHITEBOARD, RenderedFile
from cdd_guidance.actions.render.render_order import WorkerRender
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


# The file a saved graph is kept in, which a render reads as data.
_SAVED_GRAPH_SUFFIX = ".json"


class BoardNotKept(LookupError):
    """A comment came from a board no whiteboard file of the session's project was published to, so no practice says
    how to answer it."""

    def __init__(self, board: str, searched: Path) -> None:
        super().__init__(f"No whiteboard file under {searched} keeps the board {board} in its whiteboards.json")
        self.board = board
        self.searched = searched


@agent_toolset
class Render(GuidanceAction):
    """Render already-generated output for the listed guidance."""

    @on_stage(5, TAKES_FORMATS)
    @mcp
    @skill
    @agent_tool
    def render(
        self, guidance: GuidanceArg, format: str, paths: list[str] | str, content: str = "", source: str | None = None,
    ) -> list:
        """Convert already-generated content into format. Returns one result per guidance. Every render of paths ends in saved files, which its result names. A drawio, whiteboard, or markdown render is saved beside the first path, under the name the fidelity writes that format to when the path is one of the fidelity's own files or a sketch, else under the path's own name, keeping the layout people gave a drawing already there and everything else only the file held: lines of a markdown document the render does not write stay below it under a heading saying so, and a cell or element only the drawing held stays in it; its result names the saved file as path, and what was kept that way as migrate. A render to python, typescript, or javascript is saved as one file for each piece of the code, at the paths the fidelity declares for that format, such as one file for each aggregate; its result names the files that now hold the render as paths. A code file already there is never replaced: it takes the new shape, a member the source gained arriving empty, and keeps every line it held; a member the model no longer holds stays in the file, marked, and the result lists it as migrate, with its file and the added members that may have replaced it; a member both hold keeps the file's own opening line, and when the model writes that line otherwise the result lists it as migrate too, with the model's line. A render that would lose a line a file holds fails by name and leaves the file as it was. Code from one sketch or file that is not the fidelity's own is saved beside it, named for it. A document rendered from a saved graph is saved at the path the fidelity declares, its {name} filled from what the graph was read from: the one spec's name, else the folder holding every file. A document or drawing of a file that is not one of the fidelity's own is saved beside that file under the file's own name in format, and a render into the format the file is already in keeps the file and names it. Only code that no declared path can place is refused by name, and saves nothing. Only a render into a data format a program reads, such as json, answers its content. After the conversion returns, follow place_rendered; for format whiteboard, then follow publish_board.
        format: the target channel, such as python, markdown, or drawio.
        paths: a file, a list of files, or a folder, named from the project's root or absolute. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP. A path that is not there, or not under the session's root, is refused, and so is an empty file.
        content: in-process text when paths is empty. Leave this empty on an MCP call.
        source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, javascript, json, or drawio. md is markdown. Omit source when content is already the current format, or for a file whose extension says its format, such as .drawio, .whiteboard, or .py."""
        self._work_on(guidance)

        def on(worked: WorkedGuidance) -> object:
            if isinstance(worked, str):
                return worked
            return self._render_files(worked, format, paths, source) if paths else worked.render(format, content, source)

        converted = self.work.each(on)
        self.files.wrote([path for result in converted if isinstance(result, dict) for path in self._saved_by(result)])
        tools(self.act_quickly)
        tools(self.place_rendered)
        if Format(format).name == WHITEBOARD:
            tools(self.publish_board)
            tools(self.record_board)
        if self._session is not None:
            tools(self.graph.refresh)
        return converted

    def _render_files(self, worked: WorkedGuidance, format: str, paths: list[str] | str, source: str | None) -> dict:
        """The render of the files at paths, saved: a diagram or a document beside them, code at the paths the fidelity
        declares, and a document from a saved graph at the declared path its scope names. Only a render into a data
        format, such as json, which a program reads and no one saves as a file, answers its content. Only code that no
        declared path places is refused."""
        sources = self.files.paths_to_read(paths)
        source = source or self._format_named_by(sources)
        declared = worked.declared if isinstance(worked, FidelityGuidance) else None
        written = worked.session_output.written if isinstance(worked, FidelityGuidance) else None
        saved = RenderedFile.from_sources(sources, Format(source), Format(format), declared, written)
        if saved is None and (Format(format).is_code or Format(format).group in SAVED_GROUPS):
            return self._saved_by_declared_paths(worked, Format(format), sources, paths, source)
        if saved is None:
            return worked.render_files(format, paths, source)
        if not isinstance(worked, FidelityGuidance):
            return saved.save(worked.render_files(format, paths, source, saved.previous))
        return saved.save(self._drawn(worked, worked.files_to_render(format, paths, source, saved.previous)))

    def _saved_by_declared_paths(self, worked: WorkedGuidance, format: Format, sources: list[Path], paths: list[str] | str, source: str | None) -> dict:
        """A render no source's declared name places, saved all the same. Code goes to the paths the fidelity declares
        for format, one file for each piece, and is refused when they cannot place it. A document or a drawing is never
        refused for its name: from a saved graph it goes to the declared path its scope names; answered as a file for
        each name, to the declared paths; else beside its source under the source's own name in format, and a render
        into the format the file is already in keeps the file and names it."""
        first = sources[0]
        if format.is_code:
            return self._saved_code(worked, format, sources, Format(source)).save(worked.render_files(format.name, paths, source))
        if first.suffix == _SAVED_GRAPH_SUFFIX and isinstance(worked, FidelityGuidance):
            saved = RenderedFile.from_graph(first, worked, format)
            return saved.save(worked.render_files(format.name, paths, source, saved.previous))
        own = RenderedFile.beside_itself(first, Format(source), format)
        is_itself = own.path in sources
        rendered = worked.render_files(format.name, paths, source, "" if is_itself else own.previous)
        if isinstance(rendered.get("content"), dict):
            return self._saved_code(worked, format, sources, Format(source)).save(rendered)
        return {"format": rendered["format"], "path": str(own.path)} if is_itself else own.save(rendered)

    def _saved_by(self, result: dict) -> list[str]:
        """The files a render's result says it saved: the one a drawing or a document names, or each a code render names."""
        return [result["path"]] if "path" in result else list(result.get("paths", []))

    def _saved_code(self, worked: WorkedGuidance, format: Format, sources: list[Path], written_in: Format) -> RenderedCode:
        """Where a render of sources into a code format is saved: under the first root of the fidelity worked at, by
        the paths it declares for format. Guidance that is no fidelity, or one working in no session, declares no path
        under any root, so its code has no place and is refused."""
        if not isinstance(worked, FidelityGuidance) or not worked.session_output.roots:
            raise RenderHasNoDeclaredPlace("code", format, [], "name a fidelity in a session, which declares where its code is written")
        outputs = {label: [names] if isinstance(names, str) else list(names) for label, names in worked.declared.outputs.items()}
        source = sources[0] if len(sources) == 1 and sources[0].is_file() else None
        every = [name for names in outputs.values() for name in names]
        own_name = written_in.stem_of(source) if source is not None else ""
        formats = worked.practice_guidance.formats
        reshape = getattr(formats.adapter(format), "reshape", None) if format in formats else None
        return RenderedCode(worked.session_output.root, outputs.get(format.name, []), format, source, every, own_name, reshape)

    def _format_named_by(self, sources: list[Path]) -> str | None:
        """The format the first source's name says it is in, for a call that names no source: a drawing, a whiteboard,
        code, or markdown, by its extension, whatever format the fidelity it is rendered at works in. None for a
        folder, and for a file named as a sketch, such as ``orders-sketch.md``, which the call says is one."""
        first = sources[0] if sources else None
        if first is None or not first.is_file() or Format("sketch").names(first):
            return None
        named = Format.from_extension(first.suffix)
        return named.name if named.is_offered else None

    def _drawn(self, fidelity: FidelityGuidance, request: RenderRequest) -> dict:
        """What request renders to at fidelity: drawn by a worker process for a call that answers a chat when it is a
        diagram, whose class layout can hold the interpreter every chat shares for minutes; else in this process."""
        worker = WorkerRender(fidelity)
        if self.call is not None and self.call.request.answers_a_chat and worker.takes(request):
            return worker.render(request)
        return fidelity.render_request(request)

    @agent_instructions
    def place_rendered(self) -> str:
        """Render saved every file its results name, as path or paths: leave each where it is, and do not write it again. A render onto a code file already there kept everything the file held and gave it the new shape, so a member the model gained is there, empty, and a member the model no longer holds is still in its class, under a line that says it is no longer in the model. When a result lists migrate, migrate as your next step, before anything else: for each entry, open file, find the member kept, and move its body into the member that replaced it, which is usually one of may_have_replaced_it (a rename or a move looks like one member kept and one added); when none replaced it, ask the person whether the model should hold it again. Move comments and helpers that belong with the body too. Delete the kept member and its marking line only once everything in it is placed, because nothing else holds that code. An entry that names signature_differs is a member the file and the model both hold, whose opening line the model now writes as model_has: the file kept its own line, so bring that line and the body under it up to date with the model, or, when the file is right, change the model. Then fill each added member that is still empty from what the model says it does. An entry whose file is a document or a drawing names what that file held and the render did not write: lines of a markdown document, kept below it under a heading saying they are no longer in the model, or a cell of a drawing or an element of a whiteboard, kept where it was. Move each line to the section it belongs to and delete it from under that heading; leave a note a person added to a drawing where it is; delete a card from a drawing only when the thing it stands for is gone from the model on purpose. Tell the person what you moved, from which member to which, and what you left marked and why. Do not re-render to tidy up, and do not invent types. Render refreshed the session's graph with the files it saved; after you edit a file, call refresh with exactly the files you changed, so the session's graph holds them as they are now; nothing watches the files."""
        return "Leave each file render saved where it is; migrate each member a result lists, then delete it."

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
