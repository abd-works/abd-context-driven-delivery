"""The CDD access rules, proven through the graph a validate run loads, so a rule the schema does not allow cannot pass."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect, have_key
from mamba import before, context, description, it

from harness.graph.graph import Graph

_FAULTY_ROUTE = "routes.post('/x', async () => { await cdd.call('ticket.move_next', {}) })\n"
_FAULTY_NODE = "import { TicketTools } from '@cdd/harness/kanban/ticket'\nimport { Low } from 'lowdb'\nexport class TicketNode {\n  go() { return this.cdd.call<string>('ticket.close', {}) }\n}\n"
_REPAIRED_NODE = "import { TicketTools } from '@cdd/harness/kanban/ticket'\nexport class TicketNode extends TicketTools {}\n"
_FAULTY_CONNECTION = "export class CddConnectionNode {\n  show() { return this.call('board.show', {}) }\n  read(text: string) { return JSON.parse(text) }\n}\n"
_REPAIRED_CONNECTION = "export class CddConnectionNode {\n  read(text: string) {\n    try {\n      return JSON.parse(text)\n    } catch {\n      throw new CddToolError(text)\n    }\n  }\n}\n"
_FAULTY_PYTHON = "@language_adapter(language=\"typescript\")\n@agent_toolset\nclass Thing:\n    @mcp\n    @agent_tool\n    def show(self) -> dict[str, Any]:\n        return {}\n\n    def to_json(self) -> dict[str, Any]:\n        return {}\n"
_FAULTY_SHARED = "import { TicketNode } from '@src/kanban/ticket/ticket-node'\n"
_FAULTY_E2E = "itBehavesLike(a, b)\nawait page.route('x', y)\n"


def _write(root, files):
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _violations(files):
    """slug -> messages, from a graph loaded the way validate loads one."""
    root = Path(tempfile.mkdtemp(prefix="access-rules-"))
    _write(root, files)
    graph = Graph()
    roots = {name: str(root) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
    graph.load_working_copy(str(root), roots, database=str(root), overlays=["cdd_access", "lern_domain_driven"], force=True)
    found = {}
    for practice in ("ddd", "bdd"):
        for node in graph.practice(practice).by_id.values():
            for slug, message in node.rules.violations():
                found.setdefault(slug, []).append(message)
    return found


with description("the cdd_access pattern rules"):
    with context("with an application that breaks them"):
        with before.all:
            self.found = _violations({
                "src/kanban/ticket/ticket-routes.ts": _FAULTY_ROUTE,
                "src/kanban/ticket/ticket-node.ts": _FAULTY_NODE,
                "src/cdd/cdd-connection-node.ts": _FAULTY_CONNECTION,
                "src/kanban/ticket/ticket-tools.ts": "export class TicketTools {}\n",
                "harness/thing/thing.py": _FAULTY_PYTHON,
                "tests/kanban/x/x.spec.shared.ts": _FAULTY_SHARED,
                "tests/kanban/x/x.behavior.e2e.ts": _FAULTY_E2E,
            })

        with it("should flag a route that calls a tool itself"):
            expect(self.found).to(have_key("routes-ask-the-object"))

        with it("should flag a node that calls a tool itself"):
            expect(self.found).to(have_key("one-class-per-object"))

        with it("should flag a node that does not extend the adapter"):
            expect(self.found).to(have_key("node-extends-the-adapter"))

        with it("should flag a store for what the tool owns"):
            expect(self.found).to(have_key("state-lives-behind-the-tool"))

        with it("should flag a connection that names a tool"):
            expect(self.found).to(have_key("connection-only-carries"))

        with it("should flag a connection that parses blindly"):
            expect(self.found).to(have_key("text-that-is-not-json-is-a-failure"))

        with it("should flag a tools class written by hand"):
            expect(self.found).to(have_key("adapter-is-generated"))

        with it("should flag an open result on a marked toolset"):
            expect(self.found).to(have_key("annotate-what-typescript-reads"))

        with it("should run the shared behavior rules through the same graph"):
            expect(self.found).to(have_key("shared-behavior-stays-tier-free"))

        with it("should run the e2e rule through the same graph"):
            expect(self.found).to(have_key("e2e-runs-the-whole-stack"))

    with context("with a CDD-backed aggregate, which has no domain class of its own"):
        with before.all:
            self.found = _violations({
                "src/kanban/ticket/ticket-routes.ts": "router.post('/x', async (req, res) => { res.json(req.body.title) })\n",
                "src/kanban/ticket/ticket-node.ts": _REPAIRED_NODE,
                "tests/kanban/x/helper.ts": "export class ExampleRepository {}\n",
            })

        with it("should still run the LERN rules on its folder"):
            expect(self.found).to(have_key("posted-body-parsed-in-node"))

        with it("should leave test folders out of the aggregates"):
            expect(" ".join(sum(self.found.values(), []))).not_to(contain("Module 'x'"))

    with context("with an API path, which is the server's address and not a browser page"):
        with before.all:
            self.found = _violations({
                "src/kanban/ticket/ticket-routes.ts": "routes.get('/tickets', answer(() => ticket.list()))\n",
                "src/kanban/ticket/ticket-node.ts": _REPAIRED_NODE,
                "src/kanban/ticket/ticket-client.tsx": "export class TicketClient { load() { return this.api.get<Ticket>('/tickets') } }\n",
            })

        with it("should not ask for it in a paths module"):
            expect(self.found).not_to(have_key("one-home-for-web-paths"))

    with context("with a connection that starts a program by its file name"):
        with before.all:
            self.found = _violations({"src/cdd/cdd-connection-node.ts": "const PYTHON = join('.venv', 'python.exe')\n"})

        with it("should not read the file name as a tool"):
            expect(self.found).not_to(have_key("connection-only-carries"))

    with context("with an application that follows them"):
        with before.all:
            self.found = _violations({
                "src/kanban/ticket/ticket-routes.ts": "routes.post('/x', async () => { await TicketNode.fromRequest(cdd, request).moveNext() })\n",
                "src/kanban/ticket/ticket-node.ts": _REPAIRED_NODE,
                "src/cdd/cdd-connection-node.ts": _REPAIRED_CONNECTION,
            })

        with it("should find no access rule broken"):
            broken = {"routes-ask-the-object", "one-class-per-object", "node-extends-the-adapter", "connection-only-carries", "text-that-is-not-json-is-a-failure"}
            expect(broken & set(self.found)).to(equal(set()))
