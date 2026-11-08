"""A graph built for a chat's call is built in a worker process, so the cdd server's own interpreter keeps answering
every other chat, and the graph then holds what a build in the server would have made."""

import shutil
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.graph.graph import Graph
from harness.mcp.tool_calls import answering_a_chat
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_CART = "export class Cart {\n  total() { return 1; }\n  place(a, b, c, d, e, f) { return a; }\n}\n"
_WALLET = "export class Wallet {\n  pay(a, b, c, d, e) { return a; }\n}\n"


class _CountingReads(Graph):
    """A graph that counts how often this process reads a working copy into it."""

    def __init__(self) -> None:
        super().__init__()
        self.reads = 0

    def _read_working_copy(self) -> None:
        self.reads += 1
        super()._read_working_copy()


def _nodes(graph: Graph) -> list[tuple]:
    found = graph.practice("clean_engineering").in_graph.nodes()
    return sorted((node.node_id, node.type, node.source.file, node.source.start_line, node.source.end_line) for node in found)


def _violations(graph: Graph) -> list[tuple]:
    found = graph.practice("clean_engineering").in_graph.nodes()
    return sorted((violation.rule, violation.node_id, violation.line, violation.message) for node in found for violation in node.rules.violations)


def _class_names(graph: Graph) -> list[str]:
    return sorted(node.name for node in graph.practice("clean_engineering").in_graph.nodes("OoadClass"))


with description("a graph built for a chat's call"):
    with before.all:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "src").mkdir()
        (self.root / "src" / "cart.ts").write_text(_CART, encoding="utf-8")
        self.here = _CountingReads()
        self.here.load_files(str(self.root), ["clean_engineering"], ["src"])
        self.apart = _CountingReads()
        with answering_a_chat():
            self.apart.load_files(str(self.root), ["clean_engineering"], ["src"])

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should read the working copy in a worker process, never in the process answering chats"):
        expect(self.apart.reads).to(equal(0))

    with it("should hold the nodes a build in this process holds"):
        expect(_nodes(self.apart)).to(equal(_nodes(self.here)))

    with it("should hold the violations a build in this process finds"):
        expect(_violations(self.apart)).to(equal(_violations(self.here)))

    with context("that is refreshed with a file an action wrote"):
        with before.all:
            (self.root / "src" / "wallet.ts").write_text(_WALLET, encoding="utf-8")
            with answering_a_chat():
                self.apart.refresh(["src/wallet.ts"])

        with it("should hold the new file's classes beside those it held"):
            expect(_class_names(self.apart)).to(equal(["Cart", "Wallet"]))

        with it("should still read nothing in the process answering chats"):
            expect(self.apart.reads).to(equal(0))

    with context("that is opened again from its saved graph"):
        with before.all:
            self.here.save_json()
            self.reopened = _CountingReads()
            with answering_a_chat():
                self.reopened.open_saved(self.root)

        with it("should run the rules again on what it read back"):
            expect(_violations(self.reopened)).to(equal(_violations(self.here)))

    with context("whose worker reports its progress"):
        with before.all:
            self.heard: list[str] = []
            from harness.agent_tools.progress import reporting_to

            with reporting_to(self.heard.append), answering_a_chat():
                _CountingReads().load_files(str(self.root), ["clean_engineering"], ["src"])

        with it("should pass on the worker's reports, before its own of what the worker built"):
            expect(self.heard.count("Loading saved clean_engineering nodes")).to(equal(2))
