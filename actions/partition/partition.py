"""Partition kit — index, segment, completeness."""

from __future__ import annotations

import inspect
from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from partition.partition_index import PartitionIndex
from partition.segment import Segment, SegmentCompletenessConfig
from harness.agent_tools import agent_instructions, agent_toolset
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Partition(GuidanceAction):
    """Corpus partition: index, segment, completeness.

    Real toolset (not a mixin). Slash ``/partition`` runs this kit with
    ``arguments.guidance``. Workspace open and the hanging session turn come from
    ``GuidanceAction.begin`` / ``end``.
    """

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @Mcp
    @agent_tool
    def verify_segment_completeness(
        self,
        segment_path: str,
        expected_names: str = "",
        min_body_chars: int = 120,
        index_path: str = "",
    ) -> str:
        """Run named-entry completeness on a ``*-segment.md`` chunk."""
        path = Path(segment_path)
        if not path.is_file():
            return f"completeness: FAIL\nerror: segment not found: {segment_path}\n"
        segment = self._segment_for(path, expected_names, min_body_chars, index_path)
        return segment.completeness_report()

    def _segment_for(
        self,
        path: Path,
        expected_names: str,
        min_body_chars: int,
        index_path: str,
    ) -> Segment:
        index = self._read_partition_index(path, index_path)
        config = (
            index.completeness
            if index is not None
            else SegmentCompletenessConfig(min_body_chars=int(min_body_chars))
        )
        return Segment.from_text(
            path.resolve(),
            path.read_text(encoding="utf-8", errors="replace"),
            config,
            expected_names=expected_names,
        )

    @markdown
    def partition_guidance(self) -> str: ...

    def _read_partition_index(
        self, segment_path: Path, index_path: str
    ) -> PartitionIndex | None:
        resolved = (
            Path(index_path)
            if index_path.strip()
            else PartitionIndex.resolve_near(segment_path)
        )
        if resolved is None or not resolved.is_file():
            return None
        return PartitionIndex.from_text(
            resolved.resolve(),
            resolved.read_text(encoding="utf-8", errors="replace"),
        )

    @Mcp
    @agent_tool
    def index(self, context: str, out_root: str | None = None) -> str:
        """Write the partition index for this corpus under the session .context folder. Name every expected segment so completeness can be checked later."""
        return (
            "Index written for {{context}} under {session.path}/.context/ "
            "(out_root overrides session.path when set)."
        )

    @Mcp
    @agent_tool
    def segment(self, out_root: str | None = None) -> str:
        """Write verbatim source chunks from the index into segment files under the session path. Completeness must use named entries, not length alone."""
        return (
            "Verbatim source chunks written under {session.path}/{artifact}/.context/ "
            "from {subject}-index.md. "
            "Named-entry completeness verified (length-only is a false PASS)."
        )
      
    @agent_instructions
    def partition_corpus(self,
        context: str,
        mode: str = "one_go",
        out_root: str | None = None,
        slug: str = "",
        scaffold: str = ""

    ) -> str:
        """Build the index and segment files for one corpus. Fail if any new chunk misses a named entry the index required."""
        self.partition_guidance
        self.index(context, out_root)
        self.segment(out_root)
        self.verify_segment_completeness(
            segment_path="{artifact}-segment.md", index_path="{subject}-index.md"
        )
        return (
            "Partition of {{context}} finished (mode {{mode}}); "
            "docs under {session.path}/.context/. "
            "Hard fail if any new chunk fails named-entry completeness."
        )

    @Mcp
    @Skill
    @agent_instructions
    def partition(self,
        guidance: GuidanceArg,
        context: str,
        mode: str = "one_go",
        out_root: str | None = None,
    ) -> str:
        """Split the given context into an index plus verbatim segments for each listed Guidance. Fail if any new chunk misses a named entry the index required. Pass a string to partition that text once."""
        def on(item) -> None:
            if isinstance(item, str):
                self.partition_corpus(context, mode, out_root)
                return
            item.contexts
            self.partition_corpus(
                context,
                mode,
                out_root,
                slug=getattr(item, "context_index_key", None),
                scaffold=item.scaffold,
            )

        self.run(guidance, on, action="partition")
        return (
            "Partition of {{context}} finished (mode {{mode}}); "
            "docs under {session.path}/.context/. "
            "Hard fail if any new chunk fails named-entry completeness."
        )
