# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for Partition - kit prose on BaseContextTool hosts."""

import re
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_none, be_true, equal, expect
from mamba import before, context, description, it

from partition.partition_index import PartitionIndex
from partition.partition import Partition
from partition.segment import Segment, SegmentCompletenessConfig, SegmentEntry

from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

_KIT_DIR = Path(__file__).resolve().parent
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_STORIES_TOOLSET = "context_tools.stories.stories:Stories"
_DEFAULT_PARTITION_SNIPPET = "Hard fail"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().invoke_action(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    return Instruction(_path_for_name(_KIT_DIR, name), _KIT_DIR).expand()


with description("Partition kit prose"):
    with it("should document partition, index (Step 1), and segment (Step 2) in partition.md"):
        content = _section("partition")
        expect(content.startswith("# Partition")).to(be_true)
        expect("# Step 1 \u2014 Index" in content).to(be_true)
        expect("# Step 2 \u2014 Segment" in content).to(be_true)


with description("Partition kit on hosts"):
    with it("should not expose partition on BaseContextTool hosts"):
        from context_tools.base.base_context_tool import BaseContextTool

        cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
        host = cls()
        expect("partition" in host.actions).to(equal(False))


class _FakeWorkspace:
    def __init__(self, steps: list[str]) -> None:
        self.steps = steps

    def open(self, host: Any, **_kwargs: Any) -> str:
        self.steps.append("workspace.open")
        return "ok"


class _FakeTurn:
    def __init__(self, steps: list[str]) -> None:
        self.steps = steps

    def open(self, host: Any) -> str:
        self.steps.append("turn.open")
        return "ok"

    def finish_turn(self, *args: Any, **kwargs: Any) -> str:
        self.steps.append("finish_turn")
        return "ok"


class _PartitionHost:
    def __init__(self, steps: list[str]) -> None:
        self.steps = steps
        self.domain_slug = "test_domain"
        self.workspace = _FakeWorkspace(steps)
        self.turn = _FakeTurn(steps)

    @property
    def contexts(self) -> Instruction:
        self.steps.append("contexts")
        return Instruction("", _KIT_DIR)

    @property
    def scaffold(self) -> Instruction:
        return Instruction("", _KIT_DIR)


class _PartitionKit(Partition):
    def __init__(self, steps: list[str]) -> None:
        super().__init__()
        self.steps = steps

    def partition_corpus(
        self,
        context: str = "",
        mode: str = "one_go",
        out_root: str | None = None,
        slug: str = "",
        scaffold: str = "",
    ) -> str:
        self.steps.append("partition_corpus")
        return "ok"


with description("a partition action"):
    with context("that is given one context tool"):
        with it("should open workspace and turn, run partition_corpus, and finish_turn"):
            steps: list[str] = []
            _PartitionKit(steps).partition(
                tools=[_PartitionHost(steps)],
                context="corpus/",
                mode="one_go",
            )
            expect(steps).to(
                equal(
                    [
                        "workspace.open",
                        "contexts",
                        "turn.open",
                        "partition_corpus",
                        "finish_turn",
                    ]
                )
            )


# ---------------------------------------------------------------------------
# Test fixtures for unit-level coverage
# ---------------------------------------------------------------------------

_SEGMENT_ALL_OK = """\
<!-- expected-entries
HERO
VILLAIN
-->
HERO
A hero is a brave person who fights for justice and protects the innocent from harm in any way.
This entry body is long enough to pass the minimum character threshold with ease overall.

VILLAIN
A villain is an evil character who causes harm and chaos in the world around them consistently.
This entry body is also long enough to satisfy the minimum character threshold requirement here.
"""

_SEGMENT_WITH_STUB = """\
<!-- expected-entries
HERO
-->
HERO
Short.
"""

_SEGMENT_MISSING_ENTRY = """\
<!-- expected-entries
HERO
VILLAIN
-->
HERO
A hero is a brave person who fights for justice and protects the innocent from harm in any way.
This entry body is long enough to pass the minimum character threshold with ease overall.
"""

_SEGMENT_NO_MARKER = """\
HERO
A hero is a brave person who fights for justice and protects the innocent from harm.
"""

_INDEX_WITH_CONFIG = """\
# Test Index

## Config

<!-- partition-config
non-entry-headers:
  - NAME
  - COST
short-body-pattern: \\bRANK
min-body-chars: 80
-->
"""

_INDEX_NO_CONFIG = """\
# Test Index

No partition-config block present in this document.
"""


# ---------------------------------------------------------------------------
# SegmentCompletenessConfig
# ---------------------------------------------------------------------------

with description("a SegmentCompletenessConfig"):
    with context("that uses all defaults"):
        with before.each:
            self.config = SegmentCompletenessConfig()

        with it("should set min_body_chars to 120"):
            expect(self.config.min_body_chars).to(equal(120))

        with it("should set non_entry_headers to an empty frozenset"):
            expect(self.config.non_entry_headers).to(equal(frozenset()))

        with it("should set short_body_pattern to None"):
            expect(self.config.short_body_pattern).to(be_none)


# ---------------------------------------------------------------------------
# SegmentEntry
# ---------------------------------------------------------------------------

with description("a SegmentEntry"):
    with context("that has no body"):
        with before.each:
            self.entry = SegmentEntry("Hero", None, SegmentCompletenessConfig())

        with it("should have status MISSING_HEADER"):
            expect(self.entry.status).to(equal("MISSING_HEADER"))

        with it("should not be complete"):
            expect(self.entry.is_complete).to(be_false)

        with it("should have zero body chars"):
            expect(self.entry.body_chars).to(equal(0))

        with it("should expose the name"):
            expect(self.entry.name).to(equal("Hero"))

        with it("should expose the body as None"):
            expect(self.entry.body).to(be_none)

    with context("that has a body long enough to pass"):
        with before.each:
            self.entry = SegmentEntry("Hero", "A" * 120, SegmentCompletenessConfig())

        with it("should have status OK"):
            expect(self.entry.status).to(equal("OK"))

        with it("should be complete"):
            expect(self.entry.is_complete).to(be_true)

        with it("should report the correct body char count"):
            expect(self.entry.body_chars).to(equal(120))

    with context("that has a body shorter than min_body_chars"):
        with before.each:
            self.entry = SegmentEntry("Hero", "Short body.", SegmentCompletenessConfig())

        with it("should have status STUB"):
            expect(self.entry.status).to(equal("STUB"))

        with it("should not be complete"):
            expect(self.entry.is_complete).to(be_false)

    with context("that has a short body matching the short_body_pattern"):
        with before.each:
            config = SegmentCompletenessConfig(
                min_body_chars=120,
                short_body_pattern=re.compile(r"\bRANK\b", re.I),
            )
            # 48 chars: >= 40 threshold, pattern matches
            self.entry = SegmentEntry(
                "Hero", "This body mentions RANK and has forty chars now.", config
            )

        with it("should have status OK when body meets pattern threshold"):
            expect(self.entry.status).to(equal("OK"))

        with it("should be complete"):
            expect(self.entry.is_complete).to(be_true)


# ---------------------------------------------------------------------------
# Segment
# ---------------------------------------------------------------------------

with description("a Segment"):
    with context("that is built from text with no expected-entries marker"):
        with before.each:
            self.segment = Segment.from_text(
                Path("/fake/test.md"), _SEGMENT_NO_MARKER, SegmentCompletenessConfig()
            )

        with it("should have no expected names"):
            expect(self.segment.expected_names).to(equal([]))

        with it("should report has_expected_names as False"):
            expect(self.segment.has_expected_names).to(be_false)

    with context("that is built from text with an expected-entries block marker"):
        with before.each:
            self.segment = Segment.from_text(
                Path("/fake/test.md"), _SEGMENT_ALL_OK, SegmentCompletenessConfig()
            )

        with it("should parse expected names from the block marker"):
            expect(self.segment.expected_names).to(equal(["HERO", "VILLAIN"]))

        with it("should report has_expected_names as True"):
            expect(self.segment.has_expected_names).to(be_true)

        with it("should expose the path"):
            expect(self.segment.path).to(equal(Path("/fake/test.md")))

        with it("should expose the config"):
            expect(self.segment.config.min_body_chars).to(equal(120))

    with context("that is built with an expected_names argument overriding the marker"):
        with before.each:
            self.segment = Segment.from_text(
                Path("/fake/test.md"),
                _SEGMENT_ALL_OK,
                SegmentCompletenessConfig(),
                expected_names="HERO",
            )

        with it("should use only the argument names"):
            expect(self.segment.expected_names).to(equal(["HERO"]))

    with context("that has all expected entries complete"):
        with before.each:
            self.segment = Segment.from_text(
                Path("/fake/test.md"), _SEGMENT_ALL_OK, SegmentCompletenessConfig()
            )

        with it("should report is_complete as True"):
            expect(self.segment.is_complete).to(be_true)

        with it("should include PASS in the completeness report"):
            expect("PASS" in self.segment.completeness_report()).to(be_true)

    with context("that has an expected entry with a missing header"):
        with before.each:
            self.segment = Segment.from_text(
                Path("/fake/test.md"), _SEGMENT_MISSING_ENTRY, SegmentCompletenessConfig()
            )

        with it("should report is_complete as False"):
            expect(self.segment.is_complete).to(be_false)

        with it("should include FAIL in the completeness report"):
            expect("FAIL" in self.segment.completeness_report()).to(be_true)

    with context("that has an expected entry that is a stub"):
        with before.each:
            self.segment = Segment.from_text(
                Path("/fake/test.md"), _SEGMENT_WITH_STUB, SegmentCompletenessConfig()
            )

        with it("should report is_complete as False"):
            expect(self.segment.is_complete).to(be_false)

        with it("should include STUB in the completeness report"):
            expect("STUB" in self.segment.completeness_report()).to(be_true)


# ---------------------------------------------------------------------------
# PartitionIndex
# ---------------------------------------------------------------------------

with description("a PartitionIndex"):
    with context("that is built from text with a partition-config block"):
        with before.each:
            self.index = PartitionIndex.from_text(
                Path("/fake/index.md"), _INDEX_WITH_CONFIG
            )

        with it("should parse min_body_chars from the config block"):
            expect(self.index.min_body_chars).to(equal(80))

        with it("should parse non_entry_headers from the config block"):
            expect("NAME" in self.index.non_entry_headers).to(be_true)
            expect("COST" in self.index.non_entry_headers).to(be_true)

        with it("should parse short_body_pattern from the config block"):
            expect(self.index.short_body_pattern).not_to(be_none)

        with it("should expose the completeness config"):
            expect(self.index.completeness.min_body_chars).to(equal(80))

        with it("should expose the path"):
            expect(self.index.path).to(equal(Path("/fake/index.md")))

        with it("should expose the text"):
            expect(self.index.text).to(equal(_INDEX_WITH_CONFIG))

    with context("that is built from text without a partition-config block"):
        with before.each:
            self.index = PartitionIndex.from_text(
                Path("/fake/index.md"), _INDEX_NO_CONFIG
            )

        with it("should use the default min_body_chars of 120"):
            expect(self.index.min_body_chars).to(equal(120))

    with context("with resolve_near called"):
        with context("that finds an index in a parent .context directory"):
            with before.all:
                self._tmpdir = tempfile.mkdtemp()
                _ctx = Path(self._tmpdir) / ".context"
                _ctx.mkdir()
                (_ctx / "corpus-index.md").write_text("# Index\n")
                _seg = Path(self._tmpdir) / "module" / ".context"
                _seg.mkdir(parents=True)
                (_seg / "module-segment.md").write_text("# Segment\n")
                self._found = PartitionIndex.resolve_near(_seg / "module-segment.md")

            with it("should return a path to the index file"):
                expect(self._found).not_to(be_none)

            with it("should point at the correct index filename"):
                expect(self._found.name).to(equal("corpus-index.md"))

        with context("that finds no index nearby"):
            with before.all:
                self._tmpdir2 = tempfile.mkdtemp()
                _seg2 = Path(self._tmpdir2) / "no-index-segment.md"
                _seg2.write_text("# Segment\n")
                self._not_found = PartitionIndex.resolve_near(_seg2)

            with it("should return None"):
                expect(self._not_found).to(be_none)


# ---------------------------------------------------------------------------
# Partition - verify_segment_completeness tool
# ---------------------------------------------------------------------------

with description("Partition verifying segment completeness"):
    with context("that segment path does not exist"):
        with it("should return completeness FAIL with file-not-found error"):
            result = Partition().verify_segment_completeness(
                segment_path="/nonexistent/path/segment.md"
            )
            expect("completeness: FAIL" in result).to(be_true)
            expect("segment not found" in result).to(be_true)

    with context("that segment has no expected-entries marker"):
        with before.all:
            _dir = tempfile.mkdtemp()
            _path = Path(_dir) / "no-marker-segment.md"
            _path.write_text(_SEGMENT_NO_MARKER)
            self._result = Partition().verify_segment_completeness(
                segment_path=str(_path)
            )

        with it("should return completeness FAIL"):
            expect("completeness: FAIL" in self._result).to(be_true)

        with it("should include no-marker error text"):
            expect("no expected_names" in self._result).to(be_true)

    with context("that segment has all entries OK"):
        with before.all:
            _dir = tempfile.mkdtemp()
            _path = Path(_dir) / "ok-segment.md"
            _path.write_text(_SEGMENT_ALL_OK)
            self._result = Partition().verify_segment_completeness(
                segment_path=str(_path)
            )

        with it("should return completeness PASS"):
            expect("completeness: PASS" in self._result).to(be_true)

    with context("that segment has incomplete entries"):
        with before.all:
            _dir = tempfile.mkdtemp()
            _path = Path(_dir) / "stub-segment.md"
            _path.write_text(_SEGMENT_WITH_STUB)
            self._result = Partition().verify_segment_completeness(
                segment_path=str(_path)
            )

        with it("should return completeness FAIL"):
            expect("completeness: FAIL" in self._result).to(be_true)
