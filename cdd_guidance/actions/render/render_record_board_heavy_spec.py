"""Render publishing a whiteboard file to its board in Claude, called by a chat through a real cdd server: the twin of
``render_spec.py``'s stubbed examples, run against the server process as the agent calls ``render.record_board`` after
publishing a board. Heavy: the spec starts a cdd server of its own, on its own port, from a throwaway ``~/.cdd``, and
works on a throwaway project, so it runs beside any other spec and never reaches the person's server."""
import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import SpecServer
from harness.whiteboard import BoardLinks, Whiteboard
from space.session.throwaway_project import OPEN_PROJECTS, ThrowawayProject

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_CALL_SECONDS = 120
_BOARD = "https://claude.ai/artifact/StoryMapBoard"


async def _record_board(server: SpecServer, project: Path, path: str, url: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        result = await chat.call_tool("render.record_board", arguments={"path": path, "url": url})
        return bool(result.isError), result.content[0].text


with description("Render publishing a whiteboard file to its board in Claude") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()

    with after.all:
        self.server.stop()

    with before.each:
        self.project = ThrowawayProject()
        self.folder = self.project.root / ".context"
        self.folder.mkdir()
        self.file = self.folder / "story-map.whiteboard"
        self.file.write_text(Whiteboard("Story Map").save(), encoding="utf-8")

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("that the agent created a board for"):
        with before.each:
            self.failed, self.answer = asyncio.run(_record_board(self.server, self.project.root, ".context/story-map.whiteboard", _BOARD))

        with it("should keep the board's address beside the file, so the Files app opens the board"):
            expect(BoardLinks.beside(self.file).of(self.file)).to(equal(_BOARD))

        with it("should write the address into the folder's whiteboards.json, by the file's name"):
            expect(json.loads((self.folder / BoardLinks.RECORD).read_text(encoding="utf-8"))).to(equal({"story-map.whiteboard": _BOARD}))

        with it("should answer the chat with the address kept"):
            expect((self.failed, self.answer)).to(equal((False, _BOARD)))

    with context("that is not a whiteboard file"):
        with before.each:
            (self.folder / "story-map.drawio").write_text("<mxfile/>", encoding="utf-8")
            self.failed, self.answer = asyncio.run(_record_board(self.server, self.project.root, ".context/story-map.drawio", _BOARD))

        with it("should refuse to record a board for it"):
            expect((self.failed, ".whiteboard" in self.answer)).to(equal((True, True)))

        with it("should keep no address"):
            expect((self.folder / BoardLinks.RECORD).exists()).to(equal(False))
