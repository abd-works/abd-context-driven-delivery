"""BDD development — Session lazy graph and practices.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a session.
"""
import sys
import tempfile
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, equal, expect
from mamba import before, context, description, it

from harness.guidance.guidance import PracticeGuidance
from harness.hooks.hook_server import HandlerCatalog, HookPayload, HookServer
from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph
from harness.mcp.mcp_server import McpServer
from harness.session import Session


with description("a session"):
    with context("that has no graph yet"):
        with before.each:
            self.session = Session()

        with it("should instantiate a knowledge graph on get"):
            graph = self.session.knowledge_graph
            expect(graph).to(be_a(KnowledgeGraph))

    with context("that has no practices yet"):
        with before.each:
            self.session = Session()

        with it("should instantiate practice guidance on get"):
            practices = self.session.practices
            expect(all(isinstance(item, PracticeGuidance) for item in practices.values())).to(
                equal(True)
            )

    with context("that has been given a knowledge graph"):
        with before.each:
            self.session = Session()
            self.given = KnowledgeGraph()
            self.session.knowledge_graph = self.given

        with it("should return that graph on get"):
            expect(self.session.knowledge_graph).to(equal(self.given))

    with context("that has been reset"):
        with before.each:
            self.session = Session()
            self.prior_graph = self.session.knowledge_graph
            self.prior_practices = self.session.practices
            self.session.reset()

        with it("should instantiate a knowledge graph on the next get"):
            expect(self.session.knowledge_graph is self.prior_graph).to(equal(False))

        with it("should instantiate practice guidance on the next get"):
            expect(self.session.practices is self.prior_practices).to(equal(False))

    with context("that the hook server holds"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            self.server = HookServer(self.root, HandlerCatalog([], self.root))
            self.session = self.server.session

        with it("should live on the persistent hook server"):
            expect(self.session).to(be_a(Session))

        with it("should be the same object across hook runs"):
            from harness.hooks.hook_daemon import HookDaemon

            marker = self.root / ".cursor" / "hook-server.json"
            original = HookServer.state_path
            HookServer.state_path = classmethod(lambda cls, repo: marker)
            try:
                thread = threading.Thread(
                    target=HookDaemon().serve,
                    args=(self.root,),
                    kwargs={"inner": self.server},
                    daemon=True,
                )
                thread.start()
                client = HookServer(self.root)._wait_until_connected(marker)
                first = self.server.session
                client.handle_stdin(b'{"hook_event_name":"stop"}')
                client.handle_stdin(b'{"hook_event_name":"stop"}')
                expect(self.server.session is first).to(equal(True))
            finally:
                HookServer.state_path = original

        with it("should expose a knowledge graph"):
            expect(self.session.knowledge_graph).to(be_a(KnowledgeGraph))

        with it("should expose each practice guidance"):
            expect(
                all(isinstance(item, PracticeGuidance) for item in self.session.practices.values())
            ).to(equal(True))

        with it("should not load toolsets on each hook event"):
            first = self.session.practices
            self.server.dispatch(HookPayload({"hook_event_name": "stop"}))
            self.server.dispatch(HookPayload({"hook_event_name": "stop"}))
            expect(self.server.session.practices is first).to(equal(True))

    with context("that the mcp server holds"):
        with before.each:
            self.hooks = HookServer(Path(tempfile.mkdtemp()), HandlerCatalog([]))
            self.mcp = McpServer(repo=_REPO_ROOT, project=_REPO_ROOT)

        with it("should be a session"):
            expect(self.mcp.session).to(be_a(Session))

        with it("should not be the hook server session"):
            expect(self.mcp.session is self.hooks.session).to(equal(False))

        with it("should expose a knowledge graph"):
            expect(self.mcp.session.knowledge_graph).to(be_a(KnowledgeGraph))

        with it("should expose each practice guidance"):
            expect(
                all(
                    isinstance(item, PracticeGuidance)
                    for item in self.mcp.session.practices.values()
                )
            ).to(equal(True))

        with it("should not load toolsets on each mcp call"):
            first = self.mcp.session.practices
            self.mcp.session.knowledge_graph
            expect(self.mcp.session.practices is first).to(equal(True))
