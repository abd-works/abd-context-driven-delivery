"""Partition action: convert a corpus to markdown, index it, cut it into verbatim segments, check each segment's named
entries, and embed the segments into a searchable index."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.guidance_actions import GuidanceArg, GuidanceAction
from cdd_guidance.actions.partition.partition_index import PartitionIndex
from cdd_guidance.actions.partition.segment import MIN_ENTRY_BODY_CHARS, SEGMENT_FILE, Segment
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from harness.agent_tools.recipe import RecipePlaceholders
from harness.agent_tools.tool_call import ToolCall
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp
from cdd_guidance.context_setup.context_setup import ContextSetup

@agent_toolset
class Partition(GuidanceAction):
    """Corpus partition: index, segment, completeness.

    Slash ``/partition`` runs this action once for each listed guidance, in the session the call works in. It runs the
    whole documents pipeline: Context Setup's convert turns documents that are not markdown or code into markdown first,
    and Context Index's embed indexes the segments it wrote, so they can be searched.
    """

    def __init__(self, session: Any = None, call: ToolCall | None = None, context_setup: ContextSetup | None = None) -> None:
        """A ContextSetup left out is made here; the one held works in this partition's session, and its ContextIndex
        embeds the segments."""
        super().__init__(session, call)
        self._context_setup = context_setup if context_setup is not None else ContextSetup()

    def made_for(self, session: Any, call: ToolCall | None = None) -> Partition:
        """A partition made for session and call, holding the same ContextSetup, so its embedding provider carries over."""
        return type(self)(session=session, call=call, context_setup=self._context_setup)

    # The two below answer Any, not their classes: a property typed as a toolset is a collection whose tools the
    # installer publishes again under partition, and Context Setup and Context Index publish their own.
    @property
    def context_setup(self) -> Any:
        """Context Setup working in this partition's session: its convert turns documents into markdown to partition."""
        return self._context_setup.in_session(self._session)

    @property
    def context_index(self) -> Any:
        """Context Index working in this partition's session: its embed indexes the segments the partition wrote."""
        return self.context_setup.context_index

    @mcp
    @agent_tool
    def verify_segment_completeness(
        self,
        segment_path: str,
        expected_names: str = "",
        min_body_chars: int = MIN_ENTRY_BODY_CHARS,
        index_path: str = "",
    ) -> str:
        """Run named-entry completeness on a ``*-segment.md`` chunk.
        segment_path, index_path: from the project's root, or absolute."""
        path = self.path_named(segment_path)
        if not path.is_file():
            return f"completeness: FAIL\nerror: segment not found: {segment_path}\n"
        index = PartitionIndex.at(self.path_named(index_path)) if index_path.strip() else PartitionIndex.near(path)
        segment = Segment.at(path, index, expected_names=expected_names, min_body_chars=min_body_chars)
        return segment.completeness_report()

    @markdown
    def partition_guidance(self) -> str: ...

    def _guidance_to_index_by(self, item) -> str:
        """partition_guidance.md for one listed practice, handed over at the fidelity this partition works at, naming
        that practice's own file and the fidelity's Scaffold subsection, which says what the index lists. Text guidance,
        and a practice with no current fidelity, have none."""
        fidelity = None if isinstance(item, str) else self.fidelity_of(item)
        if fidelity is None:
            return ""
        values = {"slug": self.practice_of(item).key, "scaffold": fidelity.scaffold}
        return RecipePlaceholders(values, set(values)).filled(self.partition_guidance)

    def _folder(self, out_root: str | None) -> Path:
        """The folder the index and segments go under: out_root when the call names one, else the session's root."""
        return self.path_named(out_root) if out_root else self.session.work_root

    def _corpus(self, source: str) -> str:
        """The corpus a line names: the paths or text the call gave, else a request to ask for them, so no line tells
        the agent to work on a blank."""
        return f"the corpus at {source}" if source else "the corpus the user names (ask which files or folder, then pass them as paths)"

    @mcp
    @agent_tool
    def index(
        self,
        context: str = "",
        out_root: str | None = None,
        paths: list[str] | str | None = None,
    ) -> str:
        """Write the partition index for this corpus in the .context folder under out_root (from the project's root, or absolute), or under the session's root when out_root is omitted. Name every expected segment so completeness can be checked later.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the corpus in context.
        context: in-process text. Leave this empty on an MCP call."""
        source = self.source_label(context, paths)
        return f"Index {self._corpus(source)} under {self._folder(out_root).as_posix()}/.context/. Read those files locally."

    @mcp
    @agent_tool
    def segment(self, out_root: str | None = None) -> str:
        """Write verbatim source chunks from the index into segment files under out_root (from the project's root, or absolute), or under the session's root when out_root is omitted. Completeness must use named entries, not length alone."""
        return (
            f"Verbatim source chunks written as {self._folder(out_root).as_posix()}/{SEGMENT_FILE} "
            "from {subject}-index.md. "
            "Named-entry completeness verified (length-only is a false PASS)."
        )

    @mcp
    @agent_tool
    def segment_files(self, out_root: str | None = None) -> list[str]:
        """List the segment files a partition wrote under out_root (from the project's root, or absolute), or under the session's root when out_root is omitted, each as an absolute path: the files context_index.embed reads."""
        return [path.as_posix() for path in Segment.files_under(self._folder(out_root))]

    @mcp
    @skill
    @agent_instructions
    def partition(self,
        guidance: GuidanceArg,
        context: str = "",
        mode: str = "one_go",
        out_root: str | None = None,
        paths: list[str] | str | None = None,
    ) -> str:
        """Split the given context into an index plus verbatim segments for each listed guidance, converting documents to markdown first and embedding the segments into a searchable index after. Fail if any new chunk misses a named entry the index required.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the corpus in context.
        context: in-process text. Leave this empty on an MCP call.
        mode: one_go, or the named partition mode.
        out_root: folder for the index and segments. Omit it to use the session's root, the folder it works in."""
        self._work_on(guidance)
        source = self.source_label(context, paths)
        folder = self._folder(out_root).as_posix()
        "Step 0 — Convert: when the corpus holds documents that are not markdown or code (.docx, .doc, .pdf, .pptx, .ppt, .txt, .html, .htm), call context_setup.convert with the folder that holds them, and partition the markdown_files it returns in their place. A structure note with heading_depth 0 and word_count over 200 is a document with no headings: tell the user it may need a semantic pass, and carry on."
        tools(self.context_setup.convert)
        self.run(self._guidance_to_index_by, action="partition")
        instructions(self.index(context, out_root, paths))
        instructions(self.segment(out_root))
        "After writing the index and segments, call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."
        if self._session is not None:
            tools(self.graph.refresh)
        f"Step 4 — Embed: call segment_files with the same out_root, and pass the list it returns as segments_paths to context_index.embed, with out_path={folder}/rag, so the segments can be searched. If the list is empty, the partition wrote no segments: say so and embed nothing. Report the index_path embed returns."
        tools(self.segment_files)
        tools(self.context_index.embed)
        return (
            f"Partition{f' of {source}' if source else ''} finished (mode {mode}); "
            f"docs under {self._folder(out_root).as_posix()}/.context/. "
            "Read those files locally. "
            "Hard fail if any new chunk fails named-entry completeness."
        )
