"""BDD spec for utilities/handoff/handoff.py – Handoff toolset.
"""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("handoff", None)

from expects import be_none, contain, equal, expect, match, start_with
from mamba import before, context, description, it

from handoff.handoff import Handoff


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
    with context("given a workspace with an active session folder"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self.sessions = self.root / ".sessions"
            self.session_folder = self.sessions / "my-session"
            self.session_folder.mkdir(parents=True)
            (self.session_folder / "session.md").write_text("# session", encoding="utf-8")
            self.toolset = Handoff(path=str(self.root))

        with it("should write a file named handoff-{timestamp}.md in the session folder"):
            path = Path(self.toolset.write_handoff("# Handoff\n\nContent here.\n"))
            expect(path.is_file()).to(equal(True))
            expect(path.name).to(match(r"^handoff-\d{8}T\d{6}\.md$"))

        with it("should write the content verbatim"):
            content = "# Handoff\n\n## Outcome\nDone.\n"
            path = Path(self.toolset.write_handoff(content))
            expect(path.read_text(encoding="utf-8")).to(equal(content))

        with it("should return the absolute path of the written file"):
            path_str = self.toolset.write_handoff("content")
            expect(Path(path_str).is_absolute()).to(equal(True))

    with context("given a workspace with no active session"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self.toolset = Handoff(path=str(self.root))

        with it("should create a fallback session folder and write the file there"):
            path = Path(self.toolset.write_handoff("fallback content"))
            expect(path.is_file()).to(equal(True))
            expect(path.name).to(match(r"^handoff-\d{8}T\d{6}\.md$"))

        with it("should not write a handoff-latest.md"):
            self.toolset.write_handoff("content")
            latest = self.root / ".sessions" / "session" / "handoff-latest.md"
            expect(latest.exists()).to(equal(False))
