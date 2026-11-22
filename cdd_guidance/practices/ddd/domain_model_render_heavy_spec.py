"""A domain model rendered to code by a chat through a real cdd server: each aggregate's classes saved in the
aggregate's own file, in each code language. Heavy: the spec starts a cdd server of its own, on its own port, from a
throwaway ``~/.cdd``, and works on a throwaway project, so it never reaches the person's server."""
import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect  # noqa: E402
from mamba import after, before, context, description, it  # noqa: E402

from harness.mcp.spec_support import SpecServer  # noqa: E402
from space.session.spec_support.throwaway_project import OPEN_PROJECTS, ThrowawayProject  # noqa: E402

import cdd_guidance.practices  # noqa: E402, F401

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_CALL_SECONDS = 120
_MODEL = ".context/domain-model.md"
_DOMAIN_MODEL = """# Domain Model — Bookshop

---

## Ordering | custom

### Cart

A cart holds one line per book.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
----
+ total(): Money

### Order

An order is a cart a customer submitted.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
----
+ submit(): void
"""
_EXTENSIONS = {"python": "py", "typescript": "ts", "javascript": "js"}


async def _render(server: SpecServer, project: Path, format: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        arguments = {"guidance": "ddd-model", "format": format, "paths": [_MODEL]}
        result = await chat.call_tool("render.render", arguments=arguments)
        return bool(result.isError), result.content[0].text


def _saved(project: Path, answer: tuple[bool, str]) -> tuple[bool, list[str]]:
    """Whether the render failed, and the files its result names, as paths from the project."""
    failed, text = answer
    if failed:
        return failed, [text]
    return failed, sorted(Path(path).resolve().relative_to(project.resolve()).as_posix() for path in json.loads(text)[0]["paths"])


with description("a domain model rendered to code through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()
        self.project = ThrowawayProject()
        (self.project.root / ".context").mkdir(exist_ok=True)
        (self.project.root / _MODEL).write_text(_DOMAIN_MODEL, encoding="utf-8")
        self.answers = {format: asyncio.run(_render(self.server, self.project.root, format)) for format in _EXTENSIONS}

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("to Python"):
        with it("should save each aggregate's classes in the aggregate's own file"):
            expect(_saved(self.project.root, self.answers["python"])).to(equal((False, ["ordering/cart/cart.py", "ordering/order/order.py"])))

    with context("to TypeScript"):
        with it("should save each aggregate's classes in the aggregate's own file"):
            expect(_saved(self.project.root, self.answers["typescript"])).to(equal((False, ["ordering/cart/cart.ts", "ordering/order/order.ts"])))

    with context("to JavaScript"):
        with it("should save each aggregate's classes in the aggregate's own file"):
            expect(_saved(self.project.root, self.answers["javascript"])).to(equal((False, ["ordering/cart/cart.js", "ordering/order/order.js"])))

        with it("should write the aggregate root with the building blocks it is, and no types"):
            expect((self.project.root / "ordering" / "cart" / "cart.js").read_text(encoding="utf-8")).to(contain("<<Aggregate Root>> <<Entity>> */\nclass Cart {", "  total() {"))
