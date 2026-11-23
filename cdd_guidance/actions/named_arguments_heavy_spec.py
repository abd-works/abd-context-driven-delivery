"""The guidance actions refusing what a chat names wrongly, called through a real cdd server: a misspelt guidance slug, a
mapping whose toolset is a slug, a path that is not there, a rule by its name, and the session's graph asked for with no
paths. The twin of the unit examples in ``guidance_actions_spec.py``, ``document_spec.py`` and ``validate_spec.py``,
run as an agent calls the tools, where the tool's schema and the server's error answer are part of the behaviour.
Heavy: the spec starts a cdd server of its own from a throwaway ``~/.cdd`` and works on a throwaway project."""
import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import SpecServer
from space.session.throwaway_project import OPEN_PROJECTS, ThrowawayProject

_TOOLSETS = (
    "cdd_guidance.actions.generate.generate:Generate",
    "cdd_guidance.actions.validate.validate:Validate",
    "cdd_guidance.actions.document.document:Document",
    "space.session.sessions:Sessions",
)
_CALL_SECONDS = 120
_STORY_MAP = """\
# (E) Manage Customer Orders

## (E) Place New Order

### (S) Customer --> Browse Product Catalog
"""
_OVER_LIMIT = "export class Order {\n  place(a: string, b: string, c: string, d: string, e: string): void {}\n}\n"


async def _called(server: SpecServer, project: Path, tool: str, arguments: dict) -> tuple[bool, str]:
    async with server.chat(project, _CALL_SECONDS) as chat:
        result = await chat.call_tool(tool, arguments=arguments)
        return bool(result.isError), result.content[0].text


with description("A guidance action called through a cdd server") as self:
    with before.all:
        self.server = SpecServer(_TOOLSETS)
        self.server.start()

    with after.all:
        self.server.stop()

    with before.each:
        self.project = ThrowawayProject()
        folder = self.project.root / ".context"
        folder.mkdir()
        (folder / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        self.call = lambda tool, arguments: asyncio.run(_called(self.server, self.project.root, tool, arguments))

    with after.each:
        OPEN_PROJECTS.close_all()

    with context("with a guidance word shaped like a slug that names nothing"):
        with it("should refuse generate, naming the word and listing the slugs"):
            failed, answer = self.call("generate.generate", {"guidance": "stories_story_map"})
            expect((failed, "no practice or fidelity has the slug 'stories_story_map'" in answer, "stories-story-map" in answer)).to(equal((True, True, True)))

    with context("with a guidance mapping whose toolset is a practice's slug"):
        with it("should generate at the fidelity the mapping names"):
            failed, answer = self.call("generate.generate", {"guidance": {"toolset": "stories", "fidelity": "story_map"}})
            expect((failed, "verb-noun-format" in answer)).to(equal((False, True)))

    with context("with document asked to scan a path that is not there"):
        with it("should refuse the path by name"):
            failed, answer = self.call("document.document", {"guidance": "stories-story-map", "paths": ["nope/missing.md"]})
            expect((failed, "nothing at nope/missing.md" in answer)).to(equal((True, True)))

    with context("with document asked to scan the story map"):
        with it("should name the file to scan"):
            failed, answer = self.call("document.document", {"guidance": "stories-story-map", "paths": [".context/story-map.md"]})
            expect((failed, "Scan these paths: .context/story-map.md" in answer)).to(equal((False, True)))

    with context("with validate naming one rule by its name"):
        with it("should hand the judge that rule"):
            failed, answer = self.call("validate.validate", {"guidance": "stories-story-map", "rule": "verb-noun-format", "paths": [".context/story-map.md"]})
            expect((failed, "this rule (verb-noun-format)" in answer, "this rule (child-count-fits-layer)" in answer)).to(equal((False, True, False)))

        with it("should refuse a name no rule has, naming it"):
            failed, answer = self.call("validate.validate", {"guidance": "stories-story-map", "rule": "no-such-rule", "paths": [".context/story-map.md"]})
            expect((failed, "no rule 'no-such-rule'" in answer)).to(equal((True, True)))

    with context("with code written under the practice's root"):
        with before.each:
            code = self.project.root / "src" / "orders" / "order.ts"
            code.parent.mkdir(parents=True)
            code.write_text(_OVER_LIMIT, encoding="utf-8")

        with it("should check the session's graph, built from what is written, when validate names graph true and no paths"):
            failed, answer = self.call("validate.validate", {"guidance": "clean-engineering-code", "graph": True})
            expect((failed, "limit-operation-parameters" in answer and "src/orders/order.ts" in answer)).to(equal((False, True)))

        with it("should check the written folders when validate names no graph and no paths"):
            failed, answer = self.call("validate.validate", {"guidance": "clean-engineering-code"})
            expect((failed, "src/orders/order.ts" in answer)).to(equal((False, True)))
