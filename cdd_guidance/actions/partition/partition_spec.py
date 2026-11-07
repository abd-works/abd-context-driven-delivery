"""BDD spec for the Partition action, its index, and its segments."""

import re
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_false, be_none, be_true, contain, equal, expect, start_with
from mamba import after, before, context, description, it

from cdd_guidance.actions.partition.partition_index import PartitionIndex
from cdd_guidance.actions.partition.partition import Partition
from cdd_guidance.actions.partition.segment import Segment, SegmentCompletenessConfig, SegmentEntry

from harness.markdown import Markdown
from space.session.throwaway_project import ThrowawayProject
from harness.agent_tools.agent_tools import AgentToolSet
from harness.agent_tools.tool_call import ToolCall

_CAR_CHRONICLE_TOOLSET = (
    "cdd_guidance.builders.create_practice_guidance._examples.car_chronicle.car_chronicle:CarChronicle"
)
_STORIES_TOOLSET = "cdd_guidance.practices.stories.stories:Stories"
_DEFAULT_PARTITION_SNIPPET = "Hard fail"


def _session_of(project: Path):
    """The session open in project, as a call on that project works in it."""
    return ToolCall(project=project).session


def _section(name: str) -> str:
    return Markdown.from_label(Partition(), name).extract()


with description("the partition action's guidance"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with it("should document partition, index (Step 1), and segment (Step 2) in partition.md"):
        content = _section("partition")
        expect(content.startswith("# Partition")).to(be_true)
        expect("# Step 1 \u2014 Index" in content).to(be_true)
        expect("# Step 2 \u2014 Segment" in content).to(be_true)


with description("a practice guidance beside the partition action"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with it("should not expose partition on practice Guidance"):
        cls = type(AgentToolSet.instantiate(_CAR_CHRONICLE_TOOLSET))
        practice = cls()
        expect("partition" in practice.tools).to(equal(False))


with description("a partition action"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        self.project = ThrowawayProject().root

    with after.each:
        ThrowawayProject.close_all()

    with context("that runs on a practice"):
        with it("should finish partitioning the corpus for that practice"):
            result = Partition(session=_session_of(self.project)).partition("stories", paths="README.md")
            expect(result).to(start_with("Partition of README.md finished"))

    with context("that an agent calls on a fidelity"):
        with before.each:
            operation = Partition()._discover_instruction_members()["partition"]
            arguments = {"guidance": "stories-story-map", "paths": "README.md", "context": "", "mode": "one_go", "out_root": None}
            self.reply = operation.invoke(arguments, project=self.project)
            self.root = _session_of(self.project).root.as_posix()

        with it("should name what the index lists from that fidelity's Scaffold subsection"):
            expect("verb-noun Epic, Sub-Epic, and Story names" in self.reply).to(be_true)

        with it("should name that practice's own file"):
            expect("`stories.md` cited" in self.reply).to(be_true)

        with it("should name no partition guidance placeholder"):
            expect("{{" in self.reply).to(be_false)

        with it("should write under the session's root"):
            expect(f"docs under {self.root}/.context/" in self.reply).to(be_true)

    with context("that names an out_root"):
        with it("should index the corpus under that folder"):
            folder = Path(tempfile.mkdtemp())
            reply = Partition().index(paths="README.md", out_root=str(folder))
            expect(f"under {folder.resolve().as_posix()}/.context/" in reply).to(be_true)

    with context("that names an out_root from the project's root"):
        with it("should index the corpus under that folder in the session's project"):
            reply = Partition(session=_session_of(self.project)).index(paths="README.md", out_root="docs")
            expect(f"under {(self.project / 'docs').resolve().as_posix()}/.context/" in reply).to(be_true)

    with context("that checks a segment named from the project's root"):
        with it("should read the segment in the session's project"):
            segment = self.project / "docs" / "heroes-segment.md"
            segment.parent.mkdir(parents=True, exist_ok=True)
            segment.write_text(_SEGMENT_ALL_OK, encoding="utf-8")
            report = Partition(session=_session_of(self.project)).verify_segment_completeness("docs/heroes-segment.md")
            expect(report).to(contain("completeness: PASS"))

    with context("that checks a segment against an index named from the project's root"):
        with it("should read that index's config in the session's project"):
            (self.project / "docs").mkdir(parents=True, exist_ok=True)
            (self.project / "docs" / "heroes-segment.md").write_text(_SEGMENT_WITH_STUB, encoding="utf-8")
            (self.project / "docs" / "test-index.md").write_text(_INDEX_WITH_SHORT_MINIMUM, encoding="utf-8")
            report = Partition(session=_session_of(self.project)).verify_segment_completeness(
                "docs/heroes-segment.md", index_path="docs/test-index.md"
            )
            expect(report).to(contain("completeness: PASS"))

    with context("that an agent calls on a fidelity with an out_root"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp()).resolve().as_posix()
            operation = Partition()._discover_instruction_members()["partition"]
            arguments = {"guidance": "stories-story-map", "paths": "README.md", "context": "", "mode": "one_go", "out_root": self.folder}
            self.reply = operation.invoke(arguments, project=self.project)

        with it("should index the named corpus under that folder"):
            expect(f"Index the corpus at README.md under {self.folder}/.context/" in self.reply).to(be_true)

        with it("should write the segments under that folder"):
            expect(f"Verbatim source chunks written under {self.folder}/" in self.reply).to(be_true)

    with context("that an agent calls on two practices"):
        with before.each:
            operation = Partition()._discover_instruction_members()["partition"]
            arguments = {"guidance": "stories-story-map ddd-bounded-context", "paths": "README.md", "context": "", "mode": "one_go", "out_root": None}
            self.reply = operation.invoke(arguments, project=self.project)

        with it("should name what each practice's index lists from its own file"):
            expect(("`stories.md` cited" in self.reply, "`ddd.md` cited" in self.reply)).to(equal((True, True)))


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

_INDEX_WITH_SHORT_MINIMUM = """\
# Test Index

<!-- partition-config
min-body-chars: 3
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
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

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
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

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
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

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
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that is built from text with a partition-config block"):
        with before.each:
            self.index = PartitionIndex.from_text(
                Path("/fake/index.md"), _INDEX_WITH_CONFIG
            )

        with it("should parse min_body_chars from the config block"):
            expect(self.index.completeness.min_body_chars).to(equal(80))

        with it("should parse non_entry_headers from the config block"):
            expect("NAME" in self.index.completeness.non_entry_headers).to(be_true)
            expect("COST" in self.index.completeness.non_entry_headers).to(be_true)

        with it("should parse short_body_pattern from the config block"):
            expect(self.index.completeness.short_body_pattern).not_to(be_none)

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
            expect(self.index.completeness.min_body_chars).to(equal(120))

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
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that segment path does not exist"):
        with it("should return completeness FAIL with file-not-found error"):
            result = Partition().verify_segment_completeness(
                segment_path=str(Path(tempfile.gettempdir()) / "nonexistent" / "segment.md")
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


with description("a partition that is given files") as self:
    with before.each:
        self.throwaway = ThrowawayProject()

    with after.each:
        self.throwaway.close()

    with it("should name the file and leave the corpus out of the result"):
        folder = Path(tempfile.mkdtemp())
        corpus = folder / "corpus.md"
        corpus.write_text("a very long corpus that must stay on disk\n", encoding="utf-8")
        result = Partition(session=_session_of(self.throwaway.root)).partition("corpus note", paths=str(corpus))
        expect(str(corpus) in result).to(equal(True))
        expect("must stay on disk" in result).to(equal(False))
