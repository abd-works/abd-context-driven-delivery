"""BDD spec for space/handoff/handoff.py – Handoff toolset.
"""

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

from space.handoff.handoff import Handoff
from space.session.session import Session


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


with description("write_handoff"):
    with context("given the current session"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            _open_session(self.root)
            self.toolset = Handoff()

        with after.each:
            Session._current = None
            self.tmp.cleanup()

        with it("should write a file named handoff-{timestamp}.md in the session handoffs folder"):
            path = Path(self.toolset.write_handoff("# Handoff\n\nContent here.\n"))
            expect(path.is_file()).to(equal(True))
            expect(path.parent).to(equal(self.root / "sessions" / "my-session" / "handoffs"))
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
            latest = self.root / "sessions" / "my-session" / "handoff-latest.md"
            expect(latest.exists()).to(equal(False))

    with context("given no current session"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            Session._current = Session(repo_root=self.tmp.name)

        with after.each:
            Session._current = None
            self.tmp.cleanup()

        with it("should refuse to write a handoff"):
            expect(lambda: Handoff().write_handoff("content")).to(raise_error(ValueError))
