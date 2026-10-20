"""BDD spec for space/record_decisions/record_decisions.py — RecordDecisions toolset."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, equal, expect
from mamba import before, context, description, it

from space.record_decisions.record_decisions import RecordDecisions
from space.session.session import Session
from harness.agent_tools.agent_tools import AgentInstructions


def _rd():
    return RecordDecisions()


def _open_session(root: Path) -> Path:
    work = root / "work"
    work.mkdir(parents=True, exist_ok=True)
    Session._current = None
    Session.new("decisions", work, root)
    return work


def _expanded(action_name: str) -> str:
    """Expand action body and return all prose joined."""
    rd = _rd()
    func = getattr(type(rd), action_name)
    body = AgentInstructions.for_callable(func, rd)
    return "\n".join(body.prompt)


with description("a RecordDecisions toolset"):
    with context("when read_cdr_format is called"):
        with it("should return the CDR format content as a string"):
            result = _rd().read_cdr_format()
            expect(result).to(be_a(str))

        with it("should include the CDR template heading"):
            result = _rd().read_cdr_format()
            expect("Template" in result).to(equal(True))

        with it("should include the when-to-offer criteria"):
            result = _rd().read_cdr_format()
            expect("When to offer" in result or "when to offer" in result.lower()).to(equal(True))

    with context("when list_cdrs is called"):
        with context("with no .context/cdr directory on the session workpath"):
            with it("should return empty string"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    _open_session(Path(tmpdir))
                    result = _rd().list_cdrs()
                    expect(result).to(equal(""))
                    Session._current = None

        with context("with an empty .context/cdr directory"):
            with it("should return empty string"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    work = _open_session(Path(tmpdir))
                    (work / ".context" / "cdr").mkdir(parents=True)
                    result = _rd().list_cdrs()
                    expect(result).to(equal(""))
                    Session._current = None

        with context("with .context/cdr containing CDR files"):
            with it("should return newline-separated paths sorted by filename"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    work = _open_session(Path(tmpdir))
                    cdr_dir = work / ".context" / "cdr"
                    cdr_dir.mkdir(parents=True)
                    (cdr_dir / "0002-bar.md").write_text("bar")
                    (cdr_dir / "0001-foo.md").write_text("foo")
                    result = _rd().list_cdrs()
                    lines = result.splitlines()
                    expect(len(lines)).to(equal(2))
                    Session._current = None

            with it("should sort filenames so lower numbers appear first"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    work = _open_session(Path(tmpdir))
                    cdr_dir = work / ".context" / "cdr"
                    cdr_dir.mkdir(parents=True)
                    (cdr_dir / "0002-bar.md").write_text("bar")
                    (cdr_dir / "0001-foo.md").write_text("foo")
                    result = _rd().list_cdrs()
                    lines = result.splitlines()
                    expect("0001-foo.md" in lines[0]).to(equal(True))
                    Session._current = None

    with context("when write_cdr is called"):
        with it("should read the record from a file when paths is set"):
            with tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                _open_session(root)
                source = root / "draft.md"
                source.write_text("# From file\n\nKept on disk.", encoding="utf-8")
                written = Path(_rd().write_cdr("from-file", paths=str(source)))
                expect(written.read_text(encoding="utf-8")).to(equal("# From file\n\nKept on disk.\n"))
                Session._current = None

        with it("should write a file at the session workpath .context/cdr/NNNN-slug.md"):
            with tempfile.TemporaryDirectory() as tmpdir:
                work = _open_session(Path(tmpdir))
                _rd().write_cdr("my-decision", "# My Decision\n\nWe chose X.")
                cdr_dir = work / ".context" / "cdr"
                files = list(cdr_dir.glob("*.md"))
                expect(len(files)).to(equal(1))
                expect(files[0].name).to(equal("0001-my-decision.md"))
                Session._current = None

        with it("should create the .context/cdr directory lazily"):
            with tempfile.TemporaryDirectory() as tmpdir:
                work = _open_session(Path(tmpdir))
                cdr_dir = work / ".context" / "cdr"
                _rd().write_cdr("lazy-dir", "# Lazy\n\nCreated lazily.")
                expect(cdr_dir.is_dir()).to(equal(True))
                Session._current = None

        with it("should return the resolved path as a string"):
            with tempfile.TemporaryDirectory() as tmpdir:
                _open_session(Path(tmpdir))
                result = _rd().write_cdr("result-path", "# Result\n\nContent.")
                expect(result).to(be_a(str))
                expect("result-path" in result).to(equal(True))
                Session._current = None

        with it("should number sequentially after existing CDR files"):
            with tempfile.TemporaryDirectory() as tmpdir:
                work = _open_session(Path(tmpdir))
                cdr_dir = work / ".context" / "cdr"
                cdr_dir.mkdir(parents=True)
                (cdr_dir / "0001-first.md").write_text("# First")
                (cdr_dir / "0002-second.md").write_text("# Second")
                rd = _rd()
                rd.write_cdr("third", "# Third\n\nContent.")
                files = sorted(cdr_dir.glob("*.md"))
                expect(len(files)).to(equal(3))
                expect(files[2].name).to(equal("0003-third.md"))
                Session._current = None

        with it("should strip trailing whitespace and append a newline to content"):
            with tempfile.TemporaryDirectory() as tmpdir:
                rd = _rd()
                _open_session(Path(tmpdir))
                path = rd.write_cdr("clean", "# Clean\n\nBody.   ")
                written = Path(path).read_text(encoding="utf-8")
                expect(written.endswith("\n")).to(equal(True))
                expect(written.rstrip()).to(equal("# Clean\n\nBody."))
                Session._current = None

    with context("whose record_decisions_session action is expanded"):
        with it("should mention read_cdr_format in its prose"):
            prose = _expanded("record_decisions_session")
            expect("read_cdr_format" in prose).to(equal(True))

        with it("should mention list_cdrs in its prose"):
            prose = _expanded("record_decisions_session")
            expect("list_cdrs" in prose).to(equal(True))

        with it("should mention write_cdr in its prose"):
            prose = _expanded("record_decisions_session")
            expect("write_cdr" in prose).to(equal(True))
