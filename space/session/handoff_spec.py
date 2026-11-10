"""BDD spec for a session's handoff: Session.write_handoff and the handoff_session instructions (session.py)."""

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, match, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import AgentToolSet
from space.session.session import Session, SessionNotFoundError
from space.session.sessions import Sessions
from space.session.throwaway_project import ThrowawayProject
from space.work_state import WorkState


def _open_session(root: Path, name: str = "my-session") -> Path:
    work = root / "work"
    work.mkdir(parents=True, exist_ok=True)
    Sessions(root).switch(name, work)
    return work


def _save_current(root: Path, name: str) -> None:
    WorkState(root).session = name


with description("a session's handoff tools"):
    with it("should offer write_handoff as a tool"):
        tools = AgentToolSet.instantiate(Session).tools
        expect(tools["write_handoff"].kind).to(equal("tool"))

    with it("should offer handoff_session as instructions"):
        tools = AgentToolSet.instantiate(Session).tools
        expect(tools["handoff_session"].kind).to(equal("instructions"))

    with it("should read the handoff format, then call write_handoff, when running the handoff_session instructions"):
        tools = AgentToolSet.instantiate(Session).tools["handoff_session"].tools
        expect(tools).to(equal(["read_handoff_format", "write_handoff"]))


with description("a session writing a handoff"):
    with context("with a project whose current session is named"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            _save_current(self.root, "my-session")
            self.session = Sessions(self.root).current()

        with after.each:
            self.tmp.cleanup()

        with it("should write a file named handoff-{timestamp}.md in that session's folder"):
            path = Path(self.session.write_handoff("# Handoff\n\nContent here.\n"))
            expect(path.is_file()).to(equal(True))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "my-session"))
            expect(path.name).to(match(r"^handoff-\d{8}T\d{6}\.md$"))

        with it("should write the content verbatim"):
            content = "# Handoff\n\n## Outcome\nDone.\n"
            path = Path(self.session.write_handoff(content))
            expect(path.read_text(encoding="utf-8")).to(equal(content))

        with it("should return the absolute path of the written file"):
            path_str = self.session.write_handoff("content")
            expect(Path(path_str).is_absolute()).to(equal(True))

        with it("should read the handoff from a file when paths is set"):
            source = self.root / "draft.md"
            source.write_text("from the file\n", encoding="utf-8")
            written = Path(self.session.write_handoff(paths=str(source)))
            expect(written.read_text(encoding="utf-8")).to(equal("from the file\n"))

        with it("should not write a handoff-latest.md"):
            self.session.write_handoff("content")
            latest = self.root / ".sessions" / "my-session" / "handoff-latest.md"
            expect(latest.exists()).to(equal(False))

        with it("should show the handoff as its latest handoff"):
            path = Path(self.session.write_handoff("content"))
            expect(self.session.latest_handoff).to(equal(f".sessions/my-session/{path.name}"))

        with it("should write nothing when there is no handoff to write"):
            answer = self.session.write_handoff()
            expect(answer).to(match("^Nothing written"))
            expect(list((self.root / ".sessions").rglob("handoff-*.md"))).to(equal([]))

        with it("should ignore a session open in another checkout"):
            other = self.root / "tool-checkout"
            _open_session(other, "someone-elses-session")
            path = Path(Sessions(self.root).current().write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "my-session"))

    with context("with a project that has no named current session"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)

        with after.each:
            self.tmp.cleanup()

        with it("should write into the main session folder"):
            path = Path(Sessions(self.root).current().write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "main"))

        with it("should write into the main session folder when the saved current is main"):
            _save_current(self.root, "main")
            path = Path(Sessions(self.root).current().write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "main"))


with description("a handoff asked for a board ticket's session"):
    with before.each:
        self.project = ThrowawayProject()
        self.root = self.project.root
        for name in ("checkout-flow", "billing-report"):
            folder = self.root / ".sessions" / name
            folder.mkdir(parents=True)
            (folder / "session.json").write_text(json.dumps({"name": name}), encoding="utf-8")
        _save_current(self.root, "billing-report")
        self.tool = AgentToolSet.instantiate(Session).tools["write_handoff"]

    with after.each:
        ThrowawayProject.close_all()

    with context("that names a ticket other than the open session"):
        with it("should write into the named ticket's session folder"):
            path = Path(self.tool.invoke({"session": ".sessions/checkout-flow/session.json", "content": "content"}, project=self.root))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "checkout-flow"))

        with it("should leave the open session's folder without a handoff"):
            self.tool.invoke({"session": ".sessions/checkout-flow/session.json", "content": "content"}, project=self.root)
            expect(list((self.root / ".sessions" / "billing-report").glob("handoff-*.md"))).to(equal([]))

    with context("that names no session"):
        with it("should refuse rather than write into whichever session is open"):
            write = lambda: self.tool.invoke({"session": "", "content": "content"}, project=self.root)
            expect(write).to(raise_error(SessionNotFoundError))

    with context("that names a session the project does not have"):
        with it("should refuse rather than write into another session"):
            write = lambda: self.tool.invoke({"session": ".sessions/no-such-ticket/session.json", "content": "content"}, project=self.root)
            expect(write).to(raise_error(SessionNotFoundError))

    with context("through its MCP tool"):
        with it("should take the session as the tool's first argument"):
            expect(list(self.tool.input_schema["properties"])[0]).to(equal("session"))
