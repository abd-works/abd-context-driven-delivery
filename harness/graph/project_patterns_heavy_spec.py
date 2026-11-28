"""A graph that overlays a pattern its project keeps in its own guidelines folder is built in a worker process as it is
in the process answering chats: the worker imports the project's pattern from that folder and checks the code with it."""

import shutil
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.patterns  # noqa: F401 - registers the patterns CDD ships
from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.graph.graph import Graph

# A project that keeps acme_domain_driven in its guidelines folder and disables lern_domain_driven.
_ACME = Path(__file__).resolve().parent / "_examples" / "project_guidelines"
_CART_REPOSITORY = "export class CartRepository {\n  find(id) { return id; }\n}\n"
_FROM_A_CHAT = ToolCall(request=ToolRequest(answers_a_chat=True))


def _built(project: Path, call: ToolCall | None) -> Graph:
    """A graph of the project's code, overlaying its own pattern, built in a worker when call answers a chat."""
    graph = Graph()
    graph.use_patterns_of(project)
    if call is None:
        graph.load_files(str(project), ["ddd", "clean_engineering"], ["src"], overlays=["acme_domain_driven"])
    else:
        graph.load_files(str(project), ["ddd", "clean_engineering"], ["src"], overlays=["acme_domain_driven"], call=call)
    return graph


def _violations(graph: Graph) -> list[tuple]:
    found = [node for practice in graph.practices.held.values() for node in practice.reading.in_graph.nodes()]
    return sorted((violation.rule, violation.node_id, violation.message) for node in found for violation in node.rules.violations)


with description("a graph overlaying its project's own pattern"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-worker-guidelines-"))
        self.project = self.folder / "acme"
        shutil.copytree(_ACME, self.project)
        (self.project / "src").mkdir()
        (self.project / "src" / "cart-repository.ts").write_text(_CART_REPOSITORY, encoding="utf-8")

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with a build in a worker process for a chat's call"):
        with before.all:
            self.here = _built(self.project, None)
            self.apart = _built(self.project, _FROM_A_CHAT)

        with it("should apply the project's own pattern"):
            expect([pattern.pattern for pattern in self.apart.applied_patterns.patterns]).to(equal(["acme_domain_driven"]))

        with it("should find the violations a build in this process finds"):
            expect(_violations(self.apart)).to(equal(_violations(self.here)))
