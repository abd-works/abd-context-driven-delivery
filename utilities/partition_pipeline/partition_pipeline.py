"""Partition pipeline kit - mergeable into BaseContextTool."""

from __future__ import annotations

from pathlib import Path

from partition_pipeline.partition_index import PartitionIndex
from partition_pipeline.segment import Segment, SegmentCompletenessConfig
from primitives.actions.action import action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from tools.tool import tool


class PartitionPipeline:
    """Thin corpus partition: index, segment, completeness."""

    @instruction(override=True)
    def partition_guidance(self) -> str:
        """Domain partition.md when present; otherwise base default guidance."""
        path = self.module_dir / "partition.md"
        if path.is_file():
            return Instruction.ref(self, "partition").expand()
        return (
            "Determine top-level structure based on user suggestion, available context, "
            "skill-provided material, and what is evident in the source. "
            "Keep it thin - only enough to ground partitions; TODOs are fine."
        )

    @tool
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

    @action
    def index(self, context: str, out_root: str | None = None) -> str:
        """index"""
        self.session
        self.session_guidance
        self.contexts
        self.partition_guidance
        return (
            "Index written for {{context}} under {session.path}/.context/ "
            "(out_root overrides session.path when set)."
        )

    @action
    def segment(self, out_root: str | None = None) -> str:
        """segment"""
        self.session
        self.session_guidance
        self.contexts
        self.partition_guidance
        self.verify_segment_completeness()
        return (
            "Verbatim source chunks written under {session.path}/{module}/.context/ "
            "from {subject}-index.md (same tree as generated modules). "
            "Named-entry completeness verified (length-only is a false PASS)."
        )

    @action
    def partition(
        self,
        context: str,
        mode: str = "one_go",
        out_root: str | None = None,
    ) -> str:
        """partition"""
        self.session
        self.session_guidance
        self.contexts
        self.partition_guidance
        self.index(context, out_root)
        self.segment(out_root)
        self.verify_segment_completeness()
        return (
            "Partition of {{context}} finished (mode {{mode}}); "
            "docs under {session.path}/.context/. "
            "Hard fail if any new chunk fails named-entry completeness."
        )
