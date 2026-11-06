"""BDD spec for space/handoff/handoff.py – Handoff toolset.
"""

import json
import os
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
from space.handoff.handoff import Handoff
from space.session.session import Session, SessionNotFoundError
from space.session.throwaway_project import ThrowawayProject


def _restore_project(previous: str | None) -> None:
    if previous is None:
        os.environ.pop("CDD_PROJECT", None)
    else:
        os.environ["CDD_PROJECT"] = previous


def _open_session(root: Path, name: str = "my-session") -> Path:
    work = root / "work"
    work.mkdir(parents=True, exist_ok=True)
    Session.forget_current()
    Session.new(name, work, root)
    return work


with description("the Handoff toolset's tools"):
    with it("should expose write_handoff tool and handoff_session action"):
        tools = AgentToolSet.instantiate(Handoff).tools
        expect(tools["write_handoff"].kind).to(equal("tool"))
        expect(tools["handoff_session"].kind).to(equal("instructions"))

    with it("should not expose legacy tools"):
        sig = AgentToolSet.instantiate(Handoff).tools
        expect("resolve_working_folder" in sig).to(equal(False))
        expect("collect_session_state" in sig).to(equal(False))
        expect("compact_handoff" in sig).to(equal(False))

    with it("should not expose lifecycle begin or end"):
        sig = AgentToolSet.instantiate(Handoff).tools
        expect("begin" in sig).to(equal(False))
        expect("end" in sig).to(equal(False))

    with it("should call write_handoff when running the handoff_session action"):
        tools = AgentToolSet.instantiate(Handoff).tools["handoff_session"].tools
        expect(tools).to(equal(["write_handoff"]))


def _save_current(root: Path, name: str) -> None:
    sessions = root / ".sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    (sessions / "session.json").write_text(json.dumps({"current": name}), encoding="utf-8")


with description("write_handoff"):
    with context("given a project with a named current session"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self._prev_project = os.environ.get("CDD_PROJECT")
            os.environ["CDD_PROJECT"] = str(self.root)
            _save_current(self.root, "my-session")
            Session.forget_current()
            self.toolset = Handoff()

        with after.each:
            _restore_project(self._prev_project)
            Session.forget_current()
            self.tmp.cleanup()

        with it("should write a file named handoff-{timestamp}.md in that session's folder"):
            path = Path(self.toolset.write_handoff("# Handoff\n\nContent here.\n"))
            expect(path.is_file()).to(equal(True))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "my-session"))
            expect(path.name).to(match(r"^handoff-\d{8}T\d{6}\.md$"))

        with it("should write the content verbatim"):
            content = "# Handoff\n\n## Outcome\nDone.\n"
            path = Path(self.toolset.write_handoff(content))
            expect(path.read_text(encoding="utf-8")).to(equal(content))

        with it("should return the absolute path of the written file"):
            path_str = self.toolset.write_handoff("content")
            expect(Path(path_str).is_absolute()).to(equal(True))

        with it("should read the handoff from a file when paths is set"):
            source = self.root / "draft.md"
            source.write_text("from the file\n", encoding="utf-8")
            written = Path(self.toolset.write_handoff(paths=str(source)))
            expect(written.read_text(encoding="utf-8")).to(equal("from the file\n"))

        with it("should not write a handoff-latest.md"):
            self.toolset.write_handoff("content")
            latest = self.root / ".sessions" / "my-session" / "handoff-latest.md"
            expect(latest.exists()).to(equal(False))

        with it("should write nothing when there is no handoff to write"):
            answer = self.toolset.write_handoff()
            expect(answer).to(match("^Nothing written"))
            expect(list((self.root / ".sessions").rglob("handoff-*.md"))).to(equal([]))

        with it("should ignore a session open in another checkout"):
            other = self.root / "tool-checkout"
            _open_session(other, "someone-elses-session")
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "my-session"))

    with context("given a project with no named current session"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self._prev_project = os.environ.get("CDD_PROJECT")
            os.environ["CDD_PROJECT"] = str(self.root)
            Session.forget_current()
            self.toolset = Handoff()

        with after.each:
            _restore_project(self._prev_project)
            Session.forget_current()
            self.tmp.cleanup()

        with it("should write into the main session folder"):
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "main"))

        with it("should write into the main session folder when the saved current is main"):
            _save_current(self.root, "main")
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "main"))

    with context("given no CDD_PROJECT"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self._prev_project = os.environ.pop("CDD_PROJECT", None)
            self._prev_cwd = Path.cwd()
            os.chdir(self.root)
            Session.forget_current()
            self.toolset = Handoff()

        with after.each:
            os.chdir(self._prev_cwd)
            _restore_project(self._prev_project)
            Session.forget_current()
            self.tmp.cleanup()

        with it("should write under the current working folder's main session"):
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "main"))


with description("a handoff for a named session"):
    with before.each:
        self.project = ThrowawayProject()
        self.root = self.project.root
        for name in ("checkout-flow", "billing-report"):
            folder = self.root / ".sessions" / name
            folder.mkdir(parents=True)
            (folder / "session.json").write_text(json.dumps({"name": name}), encoding="utf-8")
        _save_current(self.root, "billing-report")
        Session.forget_current()

    with after.each:
        ThrowawayProject.close_all()

    with context("that names a board ticket other than the open session"):
        with it("should write into the named ticket's session folder"):
            path = Path(Handoff.for_session("checkout-flow").write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "checkout-flow"))

        with it("should leave the open session's folder without a handoff"):
            Handoff.for_session("checkout-flow").write_handoff("content")
            expect(list((self.root / ".sessions" / "billing-report").glob("handoff-*.md"))).to(equal([]))

    with context("that names no session"):
        with it("should write into the open session's folder"):
            path = Path(Handoff.for_session("").write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "billing-report"))

    with context("that names a session the project does not have"):
        with it("should refuse rather than write into another session"):
            expect(lambda: Handoff.for_session("no-such-ticket")).to(raise_error(SessionNotFoundError))

    with context("asked for through its MCP tool"):
        with it("should take the session as the tool's first argument"):
            tool = AgentToolSet.instantiate(Handoff).tools["write_handoff"]
            expect(list(tool.input_schema["properties"])[0]).to(equal("session"))
