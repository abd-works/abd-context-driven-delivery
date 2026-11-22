"""A class diagram rendered for a call the cdd server answers for a chat is drawn in a worker process, so routing its
arrows, minutes of CPU-bound Python on a large model, never holds the server's own interpreter while every other chat
waits on it. The drawing it saves is the one a render in the server would have saved. Heavy: each render starts a
worker process."""

import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.render.render import Render
from cdd_guidance.actions.render.render_order import RenderFailed
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import ArrowRouter
from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.agent_tools.worker_process import WorkerProcess
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_MODEL = "clean-engineering-model"
_CODE = '''\
class Wallet:
    """Wallet pays for orders."""

    def pay(self, amount: int) -> None:
        self.amount = amount


class Cart:
    """Cart holds line items and places orders."""

    def __init__(self, wallet: Wallet) -> None:
        self.wallet = wallet

    def place(self) -> None:
        self.wallet.pay(1)
'''

# A call the cdd server answers for a chat.
_FROM_A_CHAT = ToolCall(request=ToolRequest(answers_a_chat=True))


class _CountedRoutes:
    """Counts the class diagrams whose arrows this process routes while it is open."""

    def __init__(self) -> None:
        self.routes = 0
        self._route = ArrowRouter.route

    def __enter__(self) -> "_CountedRoutes":
        route, counter = self._route, self

        def counted(router: ArrowRouter) -> list:
            counter.routes += 1
            return route(router)

        ArrowRouter.route = counted
        return self

    def __exit__(self, *_exception: object) -> None:
        ArrowRouter.route = self._route


def _code_in_a_folder(root: Path, name: str) -> Path:
    folder = root / name
    folder.mkdir()
    code = folder / "cart.py"
    code.write_text(_CODE, encoding="utf-8")
    return code


def _render(action: Render, code: Path) -> list:
    return action.render(_MODEL, format="drawio", paths=[str(code)], source="python")


with description("a class diagram rendered for a chat's call"):
    with before.all:
        self.root = Path(tempfile.mkdtemp(prefix="render-worker-"))
        here = _code_in_a_folder(self.root, "here")
        _render(Render(), here)
        self.drawn_here = (here.parent / "cart.drawio").read_text(encoding="utf-8")
        self.code = _code_in_a_folder(self.root, "apart")
        with _CountedRoutes() as counted:
            self.results = _render(Render(call=_FROM_A_CHAT), self.code)
        self.routes_here = counted.routes
        self.drawing = self.code.parent / "cart.drawio"

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should route its arrows in a worker process, never in the process answering chats"):
        expect(self.routes_here).to(equal(0))

    with it("should save the drawing a render in this process saves"):
        expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.drawn_here))

    with it("should answer with the file it saved"):
        expect(self.results[0].path).to(equal(str(self.drawing)))

    with context("by a worker that fails"):
        with before.all:
            self.before_failure = self.drawing.read_text(encoding="utf-8")
            run = WorkerProcess.run
            WorkerProcess.run = lambda worker, arguments, errors: errors.write("the worker failed") and 1
            try:
                _render(Render(call=_FROM_A_CHAT), self.code)
            except RenderFailed as failure:
                self.failure = failure
            finally:
                WorkerProcess.run = run

        with it("should fail the render, naming what the worker wrote"):
            expect(str(self.failure)).to(contain("the worker failed"))

        with it("should leave the drawing as it was"):
            expect(self.drawing.read_text(encoding="utf-8")).to(equal(self.before_failure))
