"""Render — convert already-generated content on each listed guidance."""

from __future__ import annotations

from cdd_guidance.actions.render.rendered_canvas import RenderedCanvas
from cdd_guidance.actions.render.rendered_code import RenderedCode, RenderHasNoDeclaredPlace
from cdd_guidance.actions.render.rendered_file import SAVED_GROUPS, WHITEBOARD, RenderedFile, RenderedSections
from cdd_guidance.actions.render.render_order import WorkerRender
from cdd_guidance.actions.render.render_result import AnsweredContent, RenderResult, SavedCode, SavedFile
from cdd_guidance.actions.render.source_files import SAVED_GRAPH_SUFFIX, SourceFiles
from harness.guidance_actions import GuidanceArg, GuidanceAction, WorkedGuidance
from harness.guidance.declared_outputs import DeclaredOutputs, RenderPlacement
from harness.guidance.guidance import FidelityGuidance
from harness.guidance.practice_formats import Rendered, RenderRequest
from harness.guidance.action_catalogue import CONVERTS, TAKES_FORMATS, on_stage
from pathlib import Path

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, instructions, noSessionLog, tools
from harness.installation.files import skill
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import mcp
from harness.whiteboard import Whiteboard


# The group of formats a canvas is written in, which a render saves into the version of the canvas being prepared.
CANVAS = "canvas"
# The declarations of guidance that is no fidelity: none.
_DECLARES_NOTHING = DeclaredOutputs({})


class BoardNotKept(LookupError):
    """A comment came from a board no whiteboard file of the session's project was published to, so no practice says
    how to answer it."""

    def __init__(self, board: str, searched: Path) -> None:
        super().__init__(f"No whiteboard file under {searched} keeps the board {board} as the board it was published to")
        self.board = board
        self.searched = searched


class FormatNotDeclared(ValueError):
    """A render was asked to save a fidelity's work in a format the fidelity declares no file for: with no name of its
    own, the file would take another fidelity's name and be written over its file."""

    def __init__(self, fidelity: str, format: str, declared: list[str]) -> None:
        super().__init__(f"{fidelity} declares no {format} file, so a render at it saves none; it declares {', '.join(declared) or 'no file'}")
        self.fidelity = fidelity
        self.format = format
        self.declared = declared


@agent_toolset
class Render(GuidanceAction):
    """Render already-generated output for the listed guidance."""

    @on_stage(5, TAKES_FORMATS, CONVERTS)
    @mcp
    @skill
    @agent_tool
    def render(
        self, guidance: GuidanceArg, format: str, paths: list[str] | str, content: str = "", source: str | None = None,
    ) -> list[RenderResult | str]:
        """Convert already-generated content into format. Returns one result per guidance. Every render of paths ends in saved files, which its result names. A drawio, whiteboard, or markdown render is saved beside the first path, under the name the fidelity writes that format to when the path is one of the fidelity's own files or a sketch, else under the path's own name, keeping the layout people gave a drawing already there and everything else only the file held: lines of a markdown document the render does not write stay below it under a heading saying so, and a cell or element only the drawing held stays in it; its result names the saved file as path, and what was kept that way as migrate, each line, cell, or element with what the render added that may have replaced it. A render to python, typescript, or javascript is saved as one file for each piece of the code, at the paths the fidelity declares for that format, such as one file for each aggregate; its result names the files that now hold the render as paths. A code file already there is never replaced: it takes the new shape, a member the source gained arriving empty, and keeps every line it held; a member the model no longer holds stays in the file, marked, and the result lists it as migrate, with its file and the added members that may have replaced it; a member both hold keeps the file's own opening line, and when the model writes that line otherwise the result lists it as migrate too, with the model's line. A render that would lose a line a file holds fails by name and leaves the file as it was. Code from one sketch or file that is not the fidelity's own is saved beside it, named for it. A document rendered from a saved graph is saved at the path the fidelity declares, its {name} filled from what the graph was read from: the one spec's name, else the folder holding every file. A document or drawing of a file that is not one of the fidelity's own is saved beside that file under the file's own name in format, and a render into the format the file is already in keeps the file and names it. A render to claude_design is saved into the version of the Claude Design canvas being prepared, design-canvas/version-N/project/ in the fidelity's root: canvas.json and one prototype page for each screen; its result names them as paths. It refuses a published version, which people edit, and a file there it did not write, such as a ported screen: ask the person, then start the next version. Only code that no declared path can place is refused by name, and saves nothing. Only a render into a data format a program reads, such as json, answers its content. A result that lists migrate also carries decide: the agent goes through each entry and decides, by reading it against what the source now holds, whether it moved, was merged, is no longer needed, or is still wanted with the source behind; who added or removed it plays no part, and an entry stays where it is until decided. After the conversion returns, follow place_rendered; for format whiteboard, then follow publish_board, since a whiteboard render is not finished until its file is on a board in Claude and a new board's address is recorded in the file with record_board.
        format: the target channel, such as python, markdown, or drawio.
        paths: a file, a list of files, or a folder, named from the project's root or absolute. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP. A path that is not there, or not under the session's root, is refused, and so is an empty file.
        content: in-process text when paths is empty. Leave this empty on an MCP call.
        source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, javascript, json, drawio, or claude_design for a canvas's canvas.json. md is markdown. Omit source when content is already the current format, or for a file whose extension says its format, such as .drawio, .whiteboard, or .py."""
        self._work_on(guidance)

        def on(worked: WorkedGuidance) -> RenderResult | str:
            if isinstance(worked, str):
                return worked
            if not paths:
                return AnsweredContent(worked.render(format, content, source))
            return self._with_supplement_records(worked, self._render_files(worked, format, paths, source))

        if paths:
            self.work.each(lambda worked: self._refuse_undeclared(worked, Format(format)))
        converted = self.work.each(on)
        self.files.wrote([str(path) for result in converted if isinstance(result, RenderResult) for path in result.saved])
        tools(self.act_quickly)
        tools(self.place_rendered)
        if Format(format).name == WHITEBOARD:
            tools(self.publish_board)
            tools(self.record_board)
        if self._session is not None:
            tools(self.graph.refresh)
        return converted

    def _refuse_undeclared(self, worked: WorkedGuidance, format: Format) -> None:
        """Refuse, before anything is saved, a render that saves work at a fidelity in a format the fidelity declares
        no file for (*FormatNotDeclared*): each fidelity saves under its own name, and one with none would take
        another's. Guidance that is no fidelity, and a format no render saves, such as a sketch, are let through."""
        if not isinstance(worked, FidelityGuidance) or not (format.is_code or format.group in SAVED_GROUPS):
            return
        if not worked.declared.placement.paths_in(format):
            raise FormatNotDeclared(worked.slug, format.name, sorted(label for label in worked.declared.outputs if Format(label).is_offered))

    def _render_files(self, worked: WorkedGuidance, format: str, paths: list[str] | str, source: str | None) -> RenderResult:
        """The render of the files at paths, saved: a diagram or a document beside them, a canvas into the version of
        the canvas being prepared (*RenderedCanvas*), code at the paths the fidelity declares, and a document from a saved graph at the declared path its scope names. Only a render into a data
        format, such as json, which a program reads and no one saves as a file, answers its content. Only code that no
        declared path places is refused."""
        sources = self.files.paths_to_read(paths)
        source = SourceFiles(sources, worked).format_read_in(source)
        written = worked.session_output.written if isinstance(worked, FidelityGuidance) else None
        if Format(format).group == CANVAS and isinstance(worked, FidelityGuidance) and worked.session_output.roots:
            return RenderedCanvas.of(worked, format).save(self._drawn(RenderRequest.from_files(worked, format, paths, source)))
        saved = RenderedFile.from_sources(sources, Format(source), Format(format), self._placement_of(worked), written)
        if saved is None and (Format(format).is_code or Format(format).group in SAVED_GROUPS):
            return self._saved_by_declared_paths(worked, Format(format), sources, paths, source)
        if saved is None:
            return AnsweredContent(worked.render_files(format, paths, source))
        if not isinstance(worked, FidelityGuidance):
            return saved.save(worked.render_files(format, paths, source, saved.previous))
        return saved.save(self._drawn(RenderRequest.from_files(worked, format, paths, source, saved.previous)))

    def _with_supplement_records(self, worked: WorkedGuidance, result: RenderResult) -> RenderResult:
        """result, a render of files at worked, naming what the supplements of the fidelity keep in the session about
        the code it saved, such as TDD's record of the test tiers the module of a saved test uses, with what each
        leaves the agent to decide (a *SavedTests*). Only saved code is asked about: a document or a drawing is no test."""
        if not isinstance(result, SavedCode) or not isinstance(worked, FidelityGuidance) or self._session is None:
            return result
        kept = worked.supplement_records(result.saved)
        return result.with_test_tiers(kept) if kept else result

    def _saved_by_declared_paths(self, worked: WorkedGuidance, format: Format, sources: list[Path], paths: list[str] | str, source: str | None) -> RenderResult:
        """A render no source's declared name places, saved all the same. Code goes to the paths the fidelity declares
        for format, one file for each piece, and is refused when they cannot place it. A document or a drawing is never
        refused for its name: from a saved graph it goes to the declared path its scope names; answered as a file for
        each name, to the declared paths; else beside its source under the source's own name in format, and a render
        into the format the file is already in keeps the file and names it."""
        first = sources[0]
        if format.is_code:
            return self._saved_code(worked, format, sources, Format(source)).save(worked.render_files(format.name, paths, source))
        if first.suffix == SAVED_GRAPH_SUFFIX and isinstance(worked, FidelityGuidance):
            saved = RenderedFile.from_graph(first, worked, format)
            return saved.save(worked.render_files(format.name, paths, source, saved.previous))
        if isinstance(worked, FidelityGuidance) and worked.session_output.roots and worked.declared.placement.writes_by_section(first, format):
            sections = RenderedSections(worked.session_output.root, worked.declared.placement, format, worked.session_output.written.every_file())
            return sections.save(worked.render_files(format.name, paths, source, sections.previous))
        own = RenderedFile(self._placement_of(worked).beside_itself(first, Format(source), format), format, Format(source))
        is_itself = own.path in sources
        rendered = worked.render_files(format.name, paths, source, "" if is_itself else own.previous)
        if isinstance(rendered.content, dict):
            return self._saved_code(worked, format, sources, Format(source)).save(rendered)
        return SavedFile(rendered, own.path) if is_itself else own.save(rendered)

    def _saved_code(self, worked: WorkedGuidance, format: Format, sources: list[Path], written_in: Format) -> RenderedCode:
        """Where a render of sources into a code format is saved: under the first root of the fidelity worked at, by
        the paths it declares for format. Guidance that is no fidelity, or one working in no session, declares no path
        under any root, so its code has no place and is refused."""
        if not isinstance(worked, FidelityGuidance) or not worked.session_output.roots:
            raise RenderHasNoDeclaredPlace("code", format, [], "name a fidelity in a session, which declares where its code is written")
        source = sources[0] if len(sources) == 1 and sources[0].is_file() else None
        own_name = written_in.stem_of(source) if source is not None else ""
        formats = worked.practice_guidance.formats
        reshape = formats.adapter(format).reshape if format in formats else None
        return RenderedCode(worked.session_output.root, worked.declared.placement, format, source, own_name, reshape)

    def _placement_of(self, worked: WorkedGuidance) -> RenderPlacement:
        """Where a render at worked is saved, as its declared paths place it; guidance that is no fidelity declares
        none, so a render of it is saved beside its source under the source's own name."""
        return worked.declared.placement if isinstance(worked, FidelityGuidance) else _DECLARES_NOTHING.placement

    def _drawn(self, request: RenderRequest) -> Rendered:
        """What request renders to: drawn by a worker process for a call that answers a chat when it is a diagram, whose
        class layout can hold the interpreter every chat shares for minutes; else in this process."""
        worker = WorkerRender(request)
        if self.call is not None and self.call.request.answers_a_chat and worker.takes_it:
            return worker.render()
        return request.render()

    @agent_instructions
    def place_rendered(self) -> str:
        """Render saved every file its results name, as path or paths: leave each where it is, and do not write it again. A render onto a code file already there kept everything the file held and gave it the new shape, so a member the model gained is there, empty, and a member the model no longer holds is still in its class, under a line that says it is no longer in the model. When a result lists migrate, migrate as your next step, before anything else, following the result's decide. Each entry names something a file held that the source no longer holds, or writes otherwise: a member of code, kept in its class under a line saying it is no longer in the model; a line of a markdown document, kept below it under a heading saying so; or a cell of a drawing or an element of a whiteboard, kept where it was. Each comes with its file and may_have_replaced_it, what the render added that may have replaced it (a rename or a move looks like one thing kept and one added). Go through every entry and decide by reading the leftover against what the source now holds: its functionality or content moved somewhere, so move it there, as when you move its body into the member that replaced it, and take the leftover out; it was merged into something else, so fold it in and take the leftover out; it is no longer needed, so remove it; or it is still wanted and the source is behind, so put it back in the source and render again. An entry that names signature_differs is a member both hold whose opening line the source now writes as model_has: decide the same way whether the file's line or the model is right, and bring the other up to date. You decide each by reading both: who added it, a person or an earlier render, and who removed it from the source play no part. Where reading both does not tell you, ask the person. Until you have decided an entry, it stays where it is. Move comments and helpers that belong with a body too. Delete the kept member and its marking line only once everything in it is placed, because nothing else holds that code. Then fill each added member that is still empty from what the model says it does. Tell the person what you decided for each entry and why, and what you asked them. Do not re-render to tidy up, and do not invent types. Render refreshed the session's graph with the files it saved; after you edit a file, call refresh with exactly the files you changed, so the session's graph holds them as they are now; nothing watches the files."""
        return "Leave each file render saved where it is; decide each entry a result lists as migrate by reading it against what the source now holds."

    @agent_instructions
    def publish_board(self) -> str:
        """A render to whiteboard is not finished until each .whiteboard file it saved is on its board in Claude: publishing is part of creating the whiteboard, not a step to leave for later. A file render saved answers with board, the address of the board kept in the file's own board field, batches, the writes that put the file on that board, and publish, what finishes the render. With a board, write each batch to that board's store with ArtifactData batch, in order. With no board, create a Whiteboard artifact with Claude's Artifact tool titled with the file's name, its title: the file name without its .whiteboard ending, such as story-map, story-map.version-2 or ordering-model, never a title of your own, so a person can tell boards apart and match each to its file; write the batches to its store, then call record_board with the file and the board's address, which writes the address into the file, so the next render updates the same board and the Files app opens it. A robot or sub-agent that cannot reach the Artifact tool reports that the board is unpublished, naming the file, and never skips it silently. A render's batches change only what the render changed, so what people moved or added on the board stays. For a .whiteboard file you wrote yourself, read its board field; with one, read that board's store into the board as it is in Claude and write only the batches Whiteboard.batches(previous) answers against it, never rebuilding the board; with none, create the artifact titled Whiteboard.title_of(file), write Whiteboard.batches(), and call record_board. A comment a person later leaves on the board goes through answer_board_comment, which names the file to change and hands over the rules of the practice that draws it."""
        return "Finish each whiteboard render by putting its file on its board in Claude, creating the board and recording its address when it has none."

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
        """The whiteboard file of the session's project whose board is at board, as the file's own board field keeps
        it; refused when none was published to it."""
        root = self.session.work_root
        for file in self.session.session_files.find(f"{root.as_posix()}/**/*{Whiteboard.SUFFIX}"):
            if Whiteboard.board_of(file) == board:
                return file
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
        """Keep url, the address of the Claude Whiteboard board the .whiteboard file at path was published to, in the file itself, as its board field, so the next render updates that board and the Files app opens it. Call it as the last step of publishing a whiteboard render to a new board. path: the whiteboard file, named from the project's root or absolute. Returns the address kept."""
        file = self.files.path_named(path)
        if file.suffix != Whiteboard.SUFFIX:
            raise ValueError(f"{path} is not a {Whiteboard.SUFFIX} file: only a {Whiteboard.SUFFIX} file is published to a board.")
        file.write_text(Whiteboard.published_to(file.read_text(encoding="utf-8"), url), encoding="utf-8")
        return url
