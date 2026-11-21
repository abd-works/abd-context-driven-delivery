"""A render of Stories' scenarios and acceptance tests to code, and of story tests to markdown scenarios, saves each
file where the fidelity declares it, called by a chat through a real cdd server as an agent calls ``render.render``.
Heavy: the spec starts a cdd server of its own, on its own port, from a throwaway ``~/.cdd``, and works on throwaway
projects, so it runs beside any other spec and never reaches the person's server.

Exploratory testing, r3-sparky-07: every Stories code render in a session was refused, because the story formats
named their files ``tests/{epic}/{sub_epic}_story.test`` while the fidelities declare one file for each story under
``story_tests``; and a render of one shared story file wrote a story test for every story of the map."""
import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.pack_orders_project import PACK_ORDERS_FILES, PACK_ORDERS_STORY_MAP
from harness.mcp.spec_support import SpecServer
from space.session.throwaway_project import OPEN_PROJECTS, ThrowawayProject

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_CALL_SECONDS = 120
_PACK_ORDERS = "story_tests/fulfil-order/pack-orders"


def _project_written_as(format_name: str) -> ThrowawayProject:
    """A throwaway project holding the Pack Orders story map and its story files written in format_name."""
    project = ThrowawayProject()
    for file, text in {".context/story-map.md": PACK_ORDERS_STORY_MAP, **PACK_ORDERS_FILES[format_name]}.items():
        path = project.root / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return project


async def _render(server: SpecServer, project: Path, guidance: str, format: str, paths: list[str]) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        result = await chat.call_tool("render.render", arguments={"guidance": guidance, "format": format, "paths": paths})
        return bool(result.isError), result.content[0].text


def _files_under(project: ThrowawayProject, pattern: str) -> list[str]:
    return sorted(path.relative_to(project.root).as_posix() for path in project.root.glob(pattern))


with description("A Stories render called through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("of markdown scenarios to Python, at the scenarios fidelity"):
        with before.all:
            self.project = _project_written_as("markdown")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "stories-scenarios", "python", ["story_tests"]))

        with it("should save a story test for each story, in the story's own folder under its sub-epic's"):
            expect(_files_under(self.project, "story_tests/**/*_story.test.py")).to(equal([
                f"{_PACK_ORDERS}/cancel-order/cancel_order_story.test.py",
                f"{_PACK_ORDERS}/pack-order/pack_order_story.test.py",
            ]))

        with it("should answer the chat with the saved files rather than the code"):
            expect((self.failed, "pack_order_story.test.py" in self.answer, "with story(" in self.answer)).to(equal((False, True, False)))

    with context("of markdown scenarios to TypeScript, at the acceptance tests fidelity"):
        with before.all:
            self.project = _project_written_as("markdown")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "stories-acceptance-tests", "typescript", ["story_tests"]))

        with it("should save each story's test and the step library where the fidelity declares them"):
            expect(_files_under(self.project, "story_tests/**/*.ts")).to(equal([
                f"{_PACK_ORDERS}/cancel-order/cancel_order_story.test.ts",
                f"{_PACK_ORDERS}/pack-order/pack_order_story.test.ts",
                "story_tests/story-test.ts",
            ]))

        with it("should refuse nothing"):
            expect(self.failed).to(equal(False))

    with context("of markdown scenarios to JavaScript, at the acceptance tests fidelity"):
        with before.all:
            self.project = _project_written_as("markdown")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "stories-acceptance-tests", "javascript", ["story_tests"]))
            self.story_test = self.project.root / _PACK_ORDERS / "pack-order" / "pack_order_story.test.js"

        with it("should save each story's test and the step library where the fidelity declares them"):
            expect(_files_under(self.project, "story_tests/**/*.js")).to(equal([
                f"{_PACK_ORDERS}/cancel-order/cancel_order_story.test.js",
                f"{_PACK_ORDERS}/pack-order/pack_order_story.test.js",
                "story_tests/story-test.js",
            ]))

        with it("should import the step library by the path from the folder the story test is saved in"):
            expect(self.story_test.read_text(encoding="utf-8")).to(contain('from "../../../story-test.js";'))

    with context("of one shared story file in TypeScript to Python"):
        with before.all:
            self.project = _project_written_as("typescript")
            named = [f"{_PACK_ORDERS}/pack-orders.story.shared.ts"]
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "stories-acceptance-tests", "python", named))

        with it("should save a story test only for the story that file holds"):
            expect(_files_under(self.project, "story_tests/**/*_story.test.py")).to(equal([f"{_PACK_ORDERS}/cancel-order/cancel_order_story.test.py"]))

    with context("of a folder of TypeScript story tests to markdown scenarios"):
        with before.all:
            self.project = _project_written_as("typescript")
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "stories-scenarios", "markdown", ["story_tests"]))

        with it("should save a scenarios file for each story, in its sub-epic's folder"):
            expect(_files_under(self.project, "story_tests/**/*_story.test.md")).to(equal([
                f"{_PACK_ORDERS}/cancel_order_story.test.md",
                f"{_PACK_ORDERS}/pack_order_story.test.md",
            ]))

        with it("should refuse nothing"):
            expect(self.failed).to(equal(False))

    # The person's answer of 2026-11-21: a render reshapes an existing file and loses nothing. The scenarios gained a
    # step and renamed one; the story test a person wrote keeps its code, and the new steps come in empty.
    with context("of scenarios that changed, onto the Python story test a person already wrote"):
        with before.all:
            self.project = _project_written_as("python")
            scenarios = PACK_ORDERS_FILES["markdown"][f"{_PACK_ORDERS}/pack_order_story.test.md"]
            changed = scenarios.replace(
                "*Then* the Order paid order has status packed\n",
                "*Then* the Order paid order has status packed\n  *And* the Shop Clerk sees the Order in the packed list\n",
            ).replace("*Given* the Shop keeps Order unpaid order\n*When* the Shop Clerk packs the Order", "*Given* the Shop keeps Order unpaid order\n*When* the Shop Clerk packs the unpaid Order")
            (self.project.root / _PACK_ORDERS / "pack_order_story.test.md").write_text(changed, encoding="utf-8")
            self.story_test = self.project.root / _PACK_ORDERS / "pack-order" / "pack_order_story.test.py"
            self.before = self.story_test.read_text(encoding="utf-8")
            named = [f"{_PACK_ORDERS}/pack_order_story.test.md"]
            self.failed, self.answer = asyncio.run(_render(self.server, self.project.root, "stories-acceptance-tests", "python", named))
            self.after = self.story_test.read_text(encoding="utf-8")

        with it("should refuse nothing"):
            expect(self.failed).to(equal(False))

        with it("should keep every line the story test held"):
            held = self.after.splitlines()
            expect([line for line in self.before.splitlines() if line.strip() and not any(line.strip() in kept for kept in held)]).to(equal([]))

        with it("should write the step the scenarios gained into the story test, with no code yet"):
            expect(self.after).to(contain('with and_("the Shop Clerk sees the Order in the packed list"):\n            pass'))

        with it("should keep the step the scenarios renamed, with its code, marked as no longer in the model"):
            expect(self.after).to(contain('no longer in the model: step the Shop Clerk packs the Order of scenario Refuse to pack an unpaid order'))

        with it("should tell the chat which step to migrate"):
            expect(self.answer).to(contain("the Shop Clerk packs the unpaid Order"))
