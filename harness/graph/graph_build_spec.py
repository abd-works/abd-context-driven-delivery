"""A graph built for a call the cdd server answers for a chat is built in a worker process, so the server's own
interpreter keeps answering every other chat, and the graph then holds what a build in the server would have made. The
call says where its build runs; a call made in process builds in its own process."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.graph.graph import Graph
from harness.agent_tools.tool_call import ToolCall
from harness.graph.graph_build import GraphBuildFailed, WorkerBuild
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays

_CART = "export class Cart {\n  total() { return 1; }\n  place(a, b, c, d, e, f) { return a; }\n}\n"
_WALLET = "export class Wallet {\n  pay(a, b, c, d, e) { return a; }\n}\n"
_CART_REPOSITORY = "export class CartRepository {\n  find(id) { return id; }\n}\n"

# A working copy every practice reads: code, a story test with its examples, and a server spec.
_SAMPLE = Path(__file__).resolve().parent / "_examples" / "input"
_EVERY_PRACTICE = ("stories", "ddd", "ux", "clean_engineering", "bdd")
# One file each practice reads, which a refresh reads again: Clean Engineering's and DDD's classes, the story test's
# steps, the examples its steps observe, and BDD's spec. UX reads no file of a working copy.
_READ_BY_EACH_PRACTICE = (
    "src/account-credentials/account-credentials.ts",
    "src/customer/customer.ts",
    "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts",
    "tests/onboard-a-customer/authenticate-user/examples/account-credentials.examples.ts",
    "tests/onboard-a-customer/authenticate-user/authenticate_user.story.server.spec.ts",
)

# A call the cdd server answers for a chat, and one a spec or a script makes in process.
_FROM_A_CHAT = ToolCall(answers_a_chat=True)
_IN_PROCESS = ToolCall()


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


def _ddd_nodes(graph: Graph) -> list[tuple]:
    """DDD's building blocks: the type and the class of each."""
    blocks = ("EntityRoot", "Entity", "ValueObject", "Repository", "DomainService", "Factory", "Specification")
    return sorted((node.type, node.name) for node in graph.practice("ddd").in_graph.nodes() if node.type in blocks)


def _ddd_edges(graph: Graph) -> list[tuple]:
    return sorted((edge.kind, edge.parent.node_id, edge.child.node_id) for edge in graph.practice("ddd").in_graph.edges())


def _class_names(graph: Graph) -> list[str]:
    return sorted(node.name for node in graph.practice("clean_engineering").in_graph.nodes("OoadClass"))


class _CountingTakes(Graph):
    """A graph that counts the worker answers it took as changes, not as a whole graph read back."""

    def __init__(self) -> None:
        super().__init__()
        self.takes = 0

    def _take(self, changes) -> None:
        self.takes += 1
        super()._take(changes)


def _practice_state(graph: Graph, key: str) -> dict:
    """One practice's nodes where they sit with their facts, its edges, and its violations, as a build leaves them."""
    part = graph.practice(key).in_graph
    found = part.nodes()
    return {
        "nodes": sorted((node.node_id, node.type, node.source.file, node.source.start_line, node.source.end_line, _facts(node)) for node in found),
        "root": _facts(part.root),
        "edges": sorted((edge.kind, edge.parent.node_id, edge.child.node_id) for edge in part.edges()),
        "violations": sorted((violation.rule, violation.node_id, violation.message) for node in found for violation in node.rules.violations),
    }


def _facts(node) -> str:
    """The node's facts as the saved graph writes them."""
    return json.dumps(node.facts, sort_keys=True)


def _states_after_each_refresh(refreshed: dict[str, Graph], key: str) -> dict[str, dict]:
    return {file: _practice_state(graph, key) for file, graph in refreshed.items()}


def _each_file(state: dict) -> dict[str, dict]:
    return {file: state for file in _READ_BY_EACH_PRACTICE}


with description("a graph built for a chat's call"):
    with before.all:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "src").mkdir()
        (self.root / "src" / "cart.ts").write_text(_CART, encoding="utf-8")
        self.here = _CountingReads()
        self.here.load_files(str(self.root), ["clean_engineering"], ["src"])
        self.apart = _CountingReads()
        self.apart.load_files(str(self.root), ["clean_engineering"], ["src"], call=_FROM_A_CHAT)

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
            self.apart.refresh(["src/wallet.ts"], _FROM_A_CHAT)

        with it("should hold the new file's classes beside those it held"):
            expect(_class_names(self.apart)).to(equal(["Cart", "Wallet"]))

        with it("should still read nothing in the process answering chats"):
            expect(self.apart.reads).to(equal(0))

        # A build that failed left the graph with its rules' findings dropped, which a validate then read as clean.
        with context("again, by a worker that fails"):
            with before.all:
                self.before_failure = (_nodes(self.apart), _violations(self.apart))
                run = WorkerBuild._run
                WorkerBuild._run = lambda build, arguments, errors: errors.write("the worker failed") and 1
                try:
                    self.apart.refresh(["src/wallet.ts"], _FROM_A_CHAT)
                except GraphBuildFailed as failure:
                    self.failure = failure
                finally:
                    WorkerBuild._run = run

            with it("should fail the refresh"):
                expect(str(self.failure)).to(contain("the worker failed"))

            with it("should still hold every node and every violation it held"):
                expect((_nodes(self.apart), _violations(self.apart))).to(equal(self.before_failure))

    with context("for a call made in process"):
        with before.all:
            self.in_process = _CountingReads()
            self.in_process.load_files(str(self.root), ["clean_engineering"], ["src/cart.ts"], call=_IN_PROCESS)

        with it("should read the working copy in this process"):
            expect(self.in_process.reads).to(equal(1))

    with context("that is opened again from its saved graph"):
        with before.all:
            self.here.save_json()
            self.reopened = _CountingReads()
            self.reopened.open_saved(self.root)

        with it("should hold the violations it was saved with"):
            expect(_violations(self.reopened)).to(equal(_violations(self.here)))

        with it("should run no build to open it"):
            expect(self.reopened.reads).to(equal(0))

    with context("that holds DDD beside the Clean Engineering practice it extends"):
        with before.all:
            self.domain = Path(tempfile.mkdtemp())
            (self.domain / "cart").mkdir()
            # The folder is a bounded context, so DDD reads the classes' names as the building blocks they name.
            (self.domain / ".context").mkdir()
            (self.domain / ".context" / "bounded-context.md").write_text("# Sales\n", encoding="utf-8")
            (self.domain / "cart" / "cart.ts").write_text(_CART, encoding="utf-8")
            (self.domain / "cart" / "cart_repository.ts").write_text(_CART_REPOSITORY, encoding="utf-8")
            practices = {"clean_engineering": ".", "ddd": "."}
            self.domain_here = Graph()
            self.domain_here.load_working_copy(str(self.domain), practices)
            self.domain_apart = Graph()
            self.domain_apart.load_working_copy(str(self.domain), practices, force=True, call=_FROM_A_CHAT)
            self.domain_reopened = Graph()
            self.domain_reopened.open_saved(self.domain)

        with after.all:
            shutil.rmtree(self.domain, ignore_errors=True)

        with it("should give DDD the building blocks a build in this process gives it"):
            expect(_ddd_nodes(self.domain_apart)).to(equal(_ddd_nodes(self.domain_here)))

        with context("that is refreshed with one of the files it read"):
            with before.all:
                (self.domain / "cart" / "cart_repository.ts").write_text(_CART_REPOSITORY.replace("}\n}", "}\n  remove(cart) { return cart; }\n}"), encoding="utf-8")
                self.domain_here.refresh(["cart/cart_repository.ts"])
                self.domain_apart.refresh(["cart/cart_repository.ts"], _FROM_A_CHAT)
                self.domain_reopened.refresh(["cart/cart_repository.ts"], _FROM_A_CHAT)

            with it("should still give DDD the building block of every class, in a worker"):
                expect(_ddd_nodes(self.domain_apart)).to(equal([("EntityRoot", "Cart"), ("Repository", "CartRepository")]))

            with it("should keep the repository it read again accessing the root it keeps, in a worker"):
                accesses = [(parent, child) for kind, parent, child in _ddd_edges(self.domain_apart) if kind == "accesses"]
                expect(accesses).to(equal([("ddd:Repository:cart/cart_repository.ts:CartRepository", "ddd:EntityRoot:cart/cart.ts:Cart")]))

            with it("should give DDD the building blocks a refresh in this process gives it"):
                expect(_ddd_nodes(self.domain_apart)).to(equal(_ddd_nodes(self.domain_here)))

            with it("should link DDD's blocks as a refresh in this process links them"):
                expect(_ddd_edges(self.domain_apart)).to(equal(_ddd_edges(self.domain_here)))

            with it("should link DDD's blocks the same way in a graph opened again from its saved graph, in a worker"):
                expect(_ddd_edges(self.domain_reopened)).to(equal(_ddd_edges(self.domain_here)))

    # A worker refresh restores every node it does not read again as a plain node holding its saved facts. A reader
    # that read a parsed object's attribute off one of them failed (Stories' step bodies) or quietly found less (Clean
    # Engineering's class fields), so a validate's result hung on which practices other chats had loaded first.
    with context("that holds every practice of a working copy, opened again from its saved graph"):
        with before.all:
            self.every = Path(tempfile.mkdtemp()) / "input"
            shutil.copytree(_SAMPLE, self.every)
            practices = {key: "." for key in _EVERY_PRACTICE}
            fresh = Graph()
            fresh.load_working_copy(str(self.every), practices, overlays=["lern_domain_driven"], force=True)
            self.fresh = {key: _practice_state(fresh, key) for key in _EVERY_PRACTICE}
            self.reopened = Graph()
            self.reopened.open_saved(self.every)
            self.refreshed = {}
            for file in _READ_BY_EACH_PRACTICE:
                held = Graph()
                held.open_saved(self.every)
                held.refresh([file], _FROM_A_CHAT)
                self.refreshed[file] = held

        with after.all:
            shutil.rmtree(self.every.parent, ignore_errors=True)

        with it("should hold every practice as the build that saved it held it"):
            expect({key: _practice_state(self.reopened, key) for key in _EVERY_PRACTICE}).to(equal(self.fresh))

        with context("that is refreshed in a worker with a file one practice reads"):
            with it("should give Stories what a fresh build gives it, whichever practice's file it refreshed"):
                expect(_states_after_each_refresh(self.refreshed, "stories")).to(equal(_each_file(self.fresh["stories"])))

            with it("should give Clean Engineering what a fresh build gives it, whichever practice's file it refreshed"):
                expect(_states_after_each_refresh(self.refreshed, "clean_engineering")).to(equal(_each_file(self.fresh["clean_engineering"])))

            with it("should give DDD what a fresh build gives it, whichever practice's file it refreshed"):
                expect(_states_after_each_refresh(self.refreshed, "ddd")).to(equal(_each_file(self.fresh["ddd"])))

            with it("should give BDD what a fresh build gives it, whichever practice's file it refreshed"):
                expect(_states_after_each_refresh(self.refreshed, "bdd")).to(equal(_each_file(self.fresh["bdd"])))

            with it("should give UX what a fresh build gives it, whichever practice's file it refreshed"):
                expect(_states_after_each_refresh(self.refreshed, "ux")).to(equal(_each_file(self.fresh["ux"])))

        # Validators refresh one session graph one after another. Each order after the first names the worker's last
        # answer instead of the server writing its graph out, and the server takes back only what the refresh changed.
        with context("that is refreshed in a worker with each practice's file in turn"):
            with before.all:
                self.chained = _CountingTakes()
                self.chained.open_saved(self.every)
                for file in _READ_BY_EACH_PRACTICE:
                    self.chained.refresh([file], _FROM_A_CHAT)

            with it("should take each refresh after the first as the changes its worker answers"):
                expect(self.chained.takes).to(equal(len(_READ_BY_EACH_PRACTICE) - 1))

            with it("should hold every practice as a fresh build gives it"):
                expect({key: _practice_state(self.chained, key) for key in _EVERY_PRACTICE}).to(equal(self.fresh))

    with context("whose worker reports its progress"):
        with before.all:
            self.heard: list[str] = []
            from harness.agent_tools.progress import reporting_to

            with reporting_to(self.heard.append):
                _CountingReads().load_files(str(self.root), ["clean_engineering"], ["src"], call=_FROM_A_CHAT)

        with it("should pass on the worker's reports, before its own of what the worker built"):
            expect(self.heard.count("Loading saved clean_engineering nodes")).to(equal(2))
