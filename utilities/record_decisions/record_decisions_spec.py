# @toolset-manifest python -m tools manifest record_decisions.record_decisions:RecordDecisions
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/record_decisions/record_decisions.py — RecordDecisions toolset."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, contain, equal, expect
from mamba import before, context, description, it

from record_decisions.record_decisions import RecordDecisions
from primitives.actions.action import _ActionExpander


def _rd():
    return RecordDecisions()


def _expanded(action_name: str) -> str:
    """Expand action body and return all prose joined."""
    rd = _rd()
    func = getattr(type(rd), action_name)
    body = _ActionExpander.instance().parse_body(func, rd)
    return "\n".join(body.prose_parts)


with description("a RecordDecisions toolset"):
    with context("when read_cdr_format is called"):
        with it("should return the CDR format content as a string"):
            # Arrange / Act
            result = _rd().read_cdr_format()
            # Assert
            expect(result).to(be_a(str))

        with it("should include the CDR template heading"):
            # Arrange / Act
            result = _rd().read_cdr_format()
            # Assert
            expect("Template" in result).to(equal(True))

        with it("should include the when-to-offer criteria"):
            # Arrange / Act
            result = _rd().read_cdr_format()
            # Assert
            expect("When to offer" in result or "when to offer" in result.lower()).to(equal(True))

    with context("when list_cdrs is called"):
        with context("with no .context/cdr directory at root"):
            with it("should return empty string"):
                # Arrange
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Act
                    result = _rd().list_cdrs(tmpdir)
                    # Assert
                    expect(result).to(equal(""))

        with context("with an empty .context/cdr directory"):
            with it("should return empty string"):
                # Arrange
                with tempfile.TemporaryDirectory() as tmpdir:
                    cdr_dir = Path(tmpdir) / ".context" / "cdr"
                    cdr_dir.mkdir(parents=True)
                    # Act
                    result = _rd().list_cdrs(tmpdir)
                    # Assert
                    expect(result).to(equal(""))

        with context("with .context/cdr containing CDR files"):
            with it("should return newline-separated paths sorted by filename"):
                # Arrange
                with tempfile.TemporaryDirectory() as tmpdir:
                    cdr_dir = Path(tmpdir) / ".context" / "cdr"
                    cdr_dir.mkdir(parents=True)
                    (cdr_dir / "0002-bar.md").write_text("bar")
                    (cdr_dir / "0001-foo.md").write_text("foo")
                    # Act
                    result = _rd().list_cdrs(tmpdir)
                    lines = result.splitlines()
                    # Assert
                    expect(len(lines)).to(equal(2))

            with it("should sort filenames so lower numbers appear first"):
                # Arrange
                with tempfile.TemporaryDirectory() as tmpdir:
                    cdr_dir = Path(tmpdir) / ".context" / "cdr"
                    cdr_dir.mkdir(parents=True)
                    (cdr_dir / "0002-bar.md").write_text("bar")
                    (cdr_dir / "0001-foo.md").write_text("foo")
                    # Act
                    result = _rd().list_cdrs(tmpdir)
                    lines = result.splitlines()
                    # Assert
                    expect("0001-foo.md" in lines[0]).to(equal(True))

    with context("when write_cdr is called"):
        with it("should write a file at root/.context/cdr/NNNN-slug.md"):
            # Arrange
            with tempfile.TemporaryDirectory() as tmpdir:
                # Act
                _rd().write_cdr(tmpdir, "my-decision", "# My Decision\n\nWe chose X.")
                cdr_dir = Path(tmpdir) / ".context" / "cdr"
                files = list(cdr_dir.glob("*.md"))
                # Assert
                expect(len(files)).to(equal(1))
                expect(files[0].name).to(equal("0001-my-decision.md"))

        with it("should create the .context/cdr directory lazily"):
            # Arrange
            with tempfile.TemporaryDirectory() as tmpdir:
                cdr_dir = Path(tmpdir) / ".context" / "cdr"
                # Act
                _rd().write_cdr(tmpdir, "lazy-dir", "# Lazy\n\nCreated lazily.")
                # Assert
                expect(cdr_dir.is_dir()).to(equal(True))

        with it("should return the resolved path as a string"):
            # Arrange
            with tempfile.TemporaryDirectory() as tmpdir:
                # Act
                result = _rd().write_cdr(tmpdir, "result-path", "# Result\n\nContent.")
                # Assert
                expect(result).to(be_a(str))
                expect("result-path" in result).to(equal(True))

        with it("should number sequentially after existing CDR files"):
            # Arrange
            with tempfile.TemporaryDirectory() as tmpdir:
                cdr_dir = Path(tmpdir) / ".context" / "cdr"
                cdr_dir.mkdir(parents=True)
                (cdr_dir / "0001-first.md").write_text("# First")
                (cdr_dir / "0002-second.md").write_text("# Second")
                rd = _rd()
                # Act
                rd.write_cdr(tmpdir, "third", "# Third\n\nContent.")
                files = sorted(cdr_dir.glob("*.md"))
                # Assert
                expect(len(files)).to(equal(3))
                expect(files[2].name).to(equal("0003-third.md"))

        with it("should strip trailing whitespace and append a newline to content"):
            # Arrange
            with tempfile.TemporaryDirectory() as tmpdir:
                rd = _rd()
                # Act
                path = rd.write_cdr(tmpdir, "clean", "# Clean\n\nBody.   ")
                written = Path(path).read_text(encoding="utf-8")
                # Assert
                expect(written.endswith("\n")).to(equal(True))
                expect(written.rstrip()).to(equal("# Clean\n\nBody."))

    with context("whose record_decisions_session action is expanded"):
        with it("should mention read_cdr_format in its prose"):
            # Arrange / Act
            prose = _expanded("record_decisions_session")
            # Assert
            expect("read_cdr_format" in prose).to(equal(True))

        with it("should mention list_cdrs in its prose"):
            # Arrange / Act
            prose = _expanded("record_decisions_session")
            # Assert
            expect("list_cdrs" in prose).to(equal(True))

        with it("should mention write_cdr in its prose"):
            # Arrange / Act
            prose = _expanded("record_decisions_session")
            # Assert
            expect("write_cdr" in prose).to(equal(True))
