"""A class model rendered to code by a chat through a real cdd server: the module's classes saved in the module's own
file, in each code language. Heavy: the spec starts a cdd server of its own, on its own port, from a throwaway
``~/.cdd``, and works on a throwaway project, so it never reaches the person's server."""
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
from cdd_guidance.practices.clean_engineering.model.fixtures.ordering_code import ORDERING_FILES  # noqa: E402

_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSIONS = "space.session.sessions:Sessions"
_CALL_SECONDS = 120
_MODEL = "ordering/.context/ordering-model.md"
_CLASS_MODEL = """# Ordering

**Module:** `ordering`

## Cart

### **Cart** <<Aggregate Root>>

+ Cart(customer_id: str)
------
+ customer_id: str
"""


async def _render(server: SpecServer, project: Path, format: str, path: str) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        arguments = {"guidance": "clean-engineering-model", "format": format, "paths": [path]}
        result = await chat.call_tool("render.render", arguments=arguments)
        return bool(result.isError), result.content[0].text


def _saved(project: Path, answer: tuple[bool, str]) -> tuple[bool, list[str]]:
    """Whether the render failed, and the files its result names, as paths from the project."""
    failed, text = answer
    if failed:
        return failed, [text]
    return failed, sorted(Path(path).resolve().relative_to(project.resolve()).as_posix() for path in json.loads(text)[0]["paths"])


with description("a class model rendered to code through a cdd server") as self:
    with before.all:
        self.server = SpecServer((_RENDER, _SESSIONS))
        self.server.start()
        self.project = ThrowawayProject()
        written = {_MODEL: _CLASS_MODEL, "billing/billing.py": ORDERING_FILES["python"][1]}
        for path, text in written.items():
            (self.project.root / path).parent.mkdir(parents=True, exist_ok=True)
            (self.project.root / path).write_text(text, encoding="utf-8")
        self.answers = {format: asyncio.run(_render(self.server, self.project.root, format, _MODEL)) for format in ("python", "typescript", "javascript")}
        self.translated = asyncio.run(_render(self.server, self.project.root, "typescript", "billing/billing.py"))

    with after.all:
        OPEN_PROJECTS.close_all()
        self.server.stop()

    with context("that is a markdown model of one module"):
        with it("should save the module's classes in the module's Python file"):
            expect(_saved(self.project.root, self.answers["python"])).to(equal((False, ["ordering/ordering.py"])))

        with it("should save the module's classes in the module's TypeScript file"):
            expect(_saved(self.project.root, self.answers["typescript"])).to(equal((False, ["ordering/ordering.ts"])))

        with it("should save the module's classes in the module's JavaScript file"):
            expect(_saved(self.project.root, self.answers["javascript"])).to(equal((False, ["ordering/ordering.js"])))

        with it("should write the class the model describes into the saved file"):
            expect((self.project.root / "ordering" / "ordering.py").read_text(encoding="utf-8")).to(contain("class Cart"))

    with context("that is a module's Python file, rendered to TypeScript"):
        with it("should save the code in the same module's TypeScript file"):
            expect(_saved(self.project.root, self.translated)).to(equal((False, ["billing/billing.ts"])))

        with it("should translate each body into TypeScript statements"):
            expect((self.project.root / "billing" / "billing.ts").read_text(encoding="utf-8")).to(contain("  add(line: CartLine): void {\n    this.lines.push(line);\n  }\n"))
