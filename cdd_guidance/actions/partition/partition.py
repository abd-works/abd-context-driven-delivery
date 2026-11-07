"""Partition action: index a corpus, cut it into verbatim segments, and check each segment's named entries."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from cdd_guidance.actions.partition.partition_index import PartitionIndex
from cdd_guidance.actions.partition.segment import MIN_ENTRY_BODY_CHARS, Segment
from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp

@agent_toolset
class Partition(GuidanceAction):
    """Corpus partition: index, segment, completeness.

    Slash ``/partition`` runs this action once for each listed guidance, in the session the call works in.
    """

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
        """partition_guidance.md for one listed practice, naming that practice's own file and the Scaffold subsection
        of the fidelity it works at, which says what the index lists. Text guidance, and a practice with no current
        fidelity, have none."""
        fidelity = None if isinstance(item, str) else self.fidelity_of(item)
        if fidelity is None:
            return ""
        return self.partition_guidance.replace("{{slug}}", item.key).replace("{{scaffold}}", fidelity.scaffold)

    def _folder(self, out_root: str | None) -> Path:
        """The folder the index and segments go under: out_root when the call names one, else the session's root."""
        return self.path_named(out_root) if out_root else self.session.root

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
        return f"Index the corpus at {source} under {self._folder(out_root).as_posix()}/.context/. Read those files locally."

    @mcp
    @agent_tool
    def segment(self, out_root: str | None = None) -> str:
        """Write verbatim source chunks from the index into segment files under out_root (from the project's root, or absolute), or under the session's root when out_root is omitted. Completeness must use named entries, not length alone."""
        return (
            f"Verbatim source chunks written under {self._folder(out_root).as_posix()}/{{artifact}}/.context/ "
            "from {subject}-index.md. "
            "Named-entry completeness verified (length-only is a false PASS)."
        )

    def _corpus_steps(self, item, context: str, out_root: str | None, paths: list[str] | str | None) -> str:
        """What partitioning the corpus asks for one listed guidance: what its index lists, then the index and the
        segments, both in the folder the call names."""
        steps = (self._guidance_to_index_by(item), self.index(context, out_root, paths), self.segment(out_root))
        return "\n\n".join(step for step in steps if step)

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
        """Split the given context into an index plus verbatim segments for each listed guidance. Fail if any new chunk misses a named entry the index required.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the corpus in context.
        context: in-process text. Leave this empty on an MCP call.
        mode: one_go, or the named partition mode.
        out_root: folder for the index and segments. Omit it to use the session path."""
        self._work_on(guidance)
        source = self.source_label(context, paths)

        def on(item) -> str:
            return self._corpus_steps(item, context, out_root, paths)

        self.run(on, action="partition")
        "After writing the index and segments, call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."
        if self._session is not None:
            tools(self.graph.refresh)
        return (
            f"Partition of {source} finished (mode {mode}); "
            f"docs under {self._folder(out_root).as_posix()}/.context/. "
            "Read those files locally. "
            "Hard fail if any new chunk fails named-entry completeness."
        )
