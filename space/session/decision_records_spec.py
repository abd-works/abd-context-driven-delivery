"""BDD spec for a session's Context Decision Records: Session.read_cdr_format, list_cdrs, write_cdr, and the
record_decisions_session instructions (session.py, decision_records.py)."""
import json
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

from expects import be_a, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions, AgentToolSet
from space.session.session import Session, SessionNotFoundError
from space.session.sessions import Sessions
from space.session.throwaway_project import ThrowawayProject


def _open_session(root: Path) -> Path:
    work = root / "work"
    work.mkdir(parents=True, exist_ok=True)
    Sessions(root).switch("decisions", work)
    return work


def _expanded(action_name: str) -> str:
    """Expand the instructions' body and return all prose joined."""
    session = AgentToolSet.instantiate(Session)
    body = AgentInstructions.for_callable(getattr(Session, action_name), session)
    return "\n".join(body.prompt)


with description("a session's decision records"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.work = _open_session(self.root)
        self.session = Sessions(self.root).current()
        self.cdr_dir = self.work / ".context" / "cdr"

    with after.each:
        self.tmp.cleanup()

    with context("whose format is read"):
        with it("should return the CDR format content as a string"):
            expect(self.session.read_cdr_format()).to(be_a(str))

        with it("should include the CDR template heading"):
            expect("Template" in self.session.read_cdr_format()).to(equal(True))

        with it("should include the when-to-offer criteria"):
            expect("when to offer" in self.session.read_cdr_format().lower()).to(equal(True))

    with context("with no .context/cdr folder on the session workpath"):
        with it("should list no records"):
            expect(self.session.list_cdrs()).to(equal(""))

    with context("with an empty .context/cdr folder"):
        with it("should list no records"):
            self.cdr_dir.mkdir(parents=True)
            expect(self.session.list_cdrs()).to(equal(""))

    with context("with .context/cdr holding records"):
        with before.each:
            self.cdr_dir.mkdir(parents=True)
            (self.cdr_dir / "0002-bar.md").write_text("bar")
            (self.cdr_dir / "0001-foo.md").write_text("foo")

        with it("should list each record on its own line"):
            expect(len(self.session.list_cdrs().splitlines())).to(equal(2))

        with it("should list lower numbers first"):
            expect("0001-foo.md" in self.session.list_cdrs().splitlines()[0]).to(equal(True))

        with it("should number a new record one past the highest"):
            written = Path(self.session.write_cdr(slug="third", content="# Third\n\nContent."))
            expect(written.name).to(equal("0003-third.md"))

    with context("that writes a record"):
        with it("should read the record from a file when paths is set"):
            source = self.root / "draft.md"
            source.write_text("# From file\n\nKept on disk.", encoding="utf-8")
            written = Path(self.session.write_cdr(slug="from-file", paths=str(source)))
            expect(written.read_text(encoding="utf-8")).to(equal("# From file\n\nKept on disk.\n"))

        with it("should write the first record as 0001-slug.md under the session workpath's .context/cdr"):
            written = Path(self.session.write_cdr(slug="my-decision", content="# My Decision\n\nWe chose X."))
            expect(written).to(equal(self.cdr_dir / "0001-my-decision.md"))

        with it("should create the .context/cdr folder when it writes the first record"):
            self.session.write_cdr(slug="lazy-dir", content="# Lazy\n\nCreated lazily.")
            expect(self.cdr_dir.is_dir()).to(equal(True))

        with it("should return the written path as a string"):
            result = self.session.write_cdr(slug="result-path", content="# Result\n\nContent.")
            expect("result-path" in result).to(equal(True))

        with it("should strip trailing whitespace and end the record with a newline"):
            written = Path(self.session.write_cdr(slug="clean", content="# Clean\n\nBody.   "))
            expect(written.read_text(encoding="utf-8")).to(equal("# Clean\n\nBody.\n"))

    with context("whose record_decisions_session instructions are expanded"):
        with it("should mention read_cdr_format in its prose"):
            expect("read_cdr_format" in _expanded("record_decisions_session")).to(equal(True))

        with it("should mention list_cdrs in its prose"):
            expect("list_cdrs" in _expanded("record_decisions_session")).to(equal(True))

        with it("should mention write_cdr in its prose"):
            expect("write_cdr" in _expanded("record_decisions_session")).to(equal(True))


with description("decision records of the main session"):
    with before.each:
        self.project = ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that has no workpath of its own"):
        with it("should write the record under the project's .context/cdr"):
            written = Path(Sessions(self.project.root).current().write_cdr(slug="main", content="# Main"))
            expect(written.parent).to(equal(self.project.root.resolve() / ".context" / "cdr"))


with description("decision records asked for a board ticket's session"):
    with before.each:
        self.project = ThrowawayProject()
        self.root = self.project.root
        self.ticket_work = self.root / "ticket-work"
        self.ticket_work.mkdir()
        folder = self.root / ".sessions" / "checkout-flow"
        folder.mkdir(parents=True)
        (folder / "session.json").write_text(
            json.dumps({"name": "checkout-flow", "workpath": str(self.ticket_work)}), encoding="utf-8"
        )
        self.open_work = _open_session(self.root)
        self.tool = AgentToolSet.instantiate(Session).tools["write_cdr"]

    with after.each:
        ThrowawayProject.close_all()

    with context("that names a ticket other than the open session"):
        with it("should write the record under the named session's workpath"):
            written = Path(self.tool.invoke({"session": ".sessions/checkout-flow/session.json", "slug": "named", "content": "# Named"}, project=self.root))
            expect(written.parent).to(equal(self.ticket_work / ".context" / "cdr"))

        with it("should leave the open session's workpath without a record"):
            self.tool.invoke({"session": ".sessions/checkout-flow/session.json", "slug": "named", "content": "# Named"}, project=self.root)
            expect((self.open_work / ".context" / "cdr").exists()).to(equal(False))

    with context("that names no session"):
        with it("should refuse rather than write under whichever session is open"):
            write = lambda: self.tool.invoke({"session": "", "slug": "open", "content": "# Open"}, project=self.root)
            expect(write).to(raise_error(SessionNotFoundError))

    with context("that names a session the project does not have"):
        with it("should refuse rather than write into another session"):
            write = lambda: self.tool.invoke({"session": ".sessions/no-such-ticket/session.json", "slug": "x", "content": "# X"}, project=self.root)
            expect(write).to(raise_error(SessionNotFoundError))
