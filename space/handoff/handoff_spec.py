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

from expects import equal, expect, match
from mamba import after, before, context, description, it

from space.handoff.handoff import Handoff
from space.session.session import Session


def _restore_project(previous: str | None) -> None:
    if previous is None:
        os.environ.pop("CDD_PROJECT", None)
    else:
        os.environ["CDD_PROJECT"] = previous


def _open_session(root: Path, name: str = "my-session") -> Path:
    work = root / "work"
    work.mkdir(parents=True, exist_ok=True)
    Session._current = None
    Session.new(name, work, root)
    return work


with description("the Handoff toolset manifest"):
    with it("should expose write_handoff tool and handoff_session action"):
        sig = Handoff.manifest.signature
        expect(sig["write_handoff"]["kind"]).to(equal("tool"))
        expect(sig["handoff_session"]["kind"]).to(equal("action"))

    with it("should not expose legacy tools"):
        sig = Handoff.manifest.signature
        expect("resolve_working_folder" in sig).to(equal(False))
        expect("collect_session_state" in sig).to(equal(False))
        expect("compact_handoff" in sig).to(equal(False))

    with it("should not expose lifecycle begin or end"):
        sig = Handoff.manifest.signature
        expect("begin" in sig).to(equal(False))
        expect("end" in sig).to(equal(False))

    with it("should call write_handoff when running the handoff_session action"):
        tools = Handoff.manifest.signature["handoff_session"]["tools"]
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
            Session._current = None
            self.toolset = Handoff()

        with after.each:
            _restore_project(self._prev_project)
            Session._current = None
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
            Session._current = None
            self.toolset = Handoff()

        with after.each:
            _restore_project(self._prev_project)
            Session._current = None
            self.tmp.cleanup()

        with it("should write into the default session folder"):
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "default"))

        with it("should write into the default session folder when the saved current is default"):
            _save_current(self.root, "default")
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "default"))

    with context("given no CDD_PROJECT"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self._prev_project = os.environ.pop("CDD_PROJECT", None)
            self._prev_cwd = Path.cwd()
            os.chdir(self.root)
            Session._current = None
            self.toolset = Handoff()

        with after.each:
            os.chdir(self._prev_cwd)
            _restore_project(self._prev_project)
            Session._current = None
            self.tmp.cleanup()

        with it("should write under the current working folder's default session"):
            path = Path(self.toolset.write_handoff("content"))
            expect(path.parent).to(equal(self.root.resolve() / ".sessions" / "default"))
