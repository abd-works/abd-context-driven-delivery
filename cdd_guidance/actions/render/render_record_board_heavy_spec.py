"""Render publishing a whiteboard file to its board in Claude, called by a chat through a real cdd server: the twin of
``render_spec.py``'s stubbed examples, run against the server process as the agent calls ``render.record_board`` after
publishing a board. Heavy: the spec starts a cdd server of its own, on its own port, from a throwaway ``~/.cdd``, and
works on a throwaway project, so it runs beside any other spec and never reaches the person's server."""
import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import SpecServer
from harness.whiteboard import Whiteboard
from space.session.spec_support.throwaway_project import OPEN_PROJECTS, ThrowawayProject

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_CALL_SECONDS = 120
_BOARD = "https://claude.ai/artifact/StoryMapBoard"


async def _record_board(server: SpecServer, project: Path, path: str, url: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        result = await chat.call_tool("render.record_board", arguments={"path": path, "url": url})
        return bool(result.isError), result.content[0].text


def _open_board_file(spec) -> None:
    """Give spec, a context's state, a throwaway project of its own whose .context holds an empty story map whiteboard,
    made once before the context's examples, which read what the context's one call left."""
    spec.project = ThrowawayProject()
    spec.folder = spec.project.root / ".context"
    spec.folder.mkdir()
    spec.file = spec.folder / "story-map.whiteboard"
    spec.file.write_text(Whiteboard("Story Map").save(), encoding="utf-8")


with description("Render publishing a whiteboard file to its board in Claude") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("that the agent created a board for"):
        with before.all:
            _open_board_file(self)
            self.failed, self.answer = asyncio.run(_record_board(self.server, self.project.root, ".context/story-map.whiteboard", _BOARD))

        with it("should keep the board's address in the file, so the Files app opens the board"):
            expect(Whiteboard.board_of(self.file)).to(equal(_BOARD))

        with it("should write no record of boards beside the file"):
            expect(sorted(path.name for path in self.folder.iterdir())).to(equal(["story-map.whiteboard"]))

        with it("should answer the chat with the address kept"):
            expect((self.failed, self.answer)).to(equal((False, _BOARD)))

    with context("that is not a whiteboard file"):
        with before.all:
            _open_board_file(self)
            (self.folder / "story-map.drawio").write_text("<mxfile/>", encoding="utf-8")
            self.failed, self.answer = asyncio.run(_record_board(self.server, self.project.root, ".context/story-map.drawio", _BOARD))

        with it("should refuse to record a board for it"):
            expect((self.failed, ".whiteboard" in self.answer)).to(equal((True, True)))

        with it("should keep no address"):
            expect((self.folder / "story-map.drawio").read_text(encoding="utf-8")).to(equal("<mxfile/>"))
