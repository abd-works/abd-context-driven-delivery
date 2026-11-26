"""LERN tier rules: node repositories, routes, web paths, and the test reset — read from tier facts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding
from cdd_guidance.patterns.lern_domain_driven import fact_names

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class NodeRepositoryParsesOnRead(PracticeGraphRule):
    """`{Domain}RepositoryNode` reads its store through Zod and the lowdb helpers, never raw file IO.

    Checked on the `-node.ts` file: node repositories are not tactical Repository nodes in the graph.
    """

    slug = "node-repository-parses-on-read"
    node_types = ("NodeRoot",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        messages: list[str] = []
        for repository in node.get_fact(fact_names.NODE_REPOSITORIES, []):
            name = repository["name"]
            messages += [
                f"{name} line {line}: `{found}` reads or writes the store by hand; use the lowdb helpers."
                for line, found in repository["raw_io"]
            ]
            if not repository["parses_on_read"]:
                messages.append(f"{name} never runs a Zod `.parse(` on what it reads from its JSON store.")
        return [Finding(node, message) for message in messages]


class PostedBodyParsedInNode(PracticeGraphRule):
    """The posted body is read once, in the node, through a Zod schema.

    A route hands `req` to `{Domain}Node.fromRequest`. A node passes `req.body` straight into a schema
    `.parse(` / `.safeParse(`. The framework-free core (`<aggregate>.ts`) never touches the request.
    """

    slug = "posted-body-parsed-in-node"
    node_types = ("Route", "NodeRoot", "Aggregate")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if node.type == "Aggregate":
            return [
                Finding(node, f"{relative}:{line}: `{code}` in the framework-free core; the node reads the request and hands the core plain values.")
                for relative, line, code in node.get_fact(fact_names.CORE_REQUEST_READS, [])
            ]
        if node.type == "NodeRoot":
            return [
                Finding(node, f"{node.source.file}:{line}: `req.body` is read without a schema; pass it straight into the posted schema's `.parse(`.")
                for line in node.get_fact(fact_names.UNPARSED_BODY_READS, [])
            ]
        return [
            Finding(node, f"{node.source.file}:{line}: `{found}` reads the posted body loosely; pass `req` to the node's `fromRequest`, which parses it.")
            for line, found in node.get_fact(fact_names.LOOSE_BODY_READS, [])
        ]


class ThrowHttpExceptions(PracticeGraphRule):
    """Routes and nodes fail with `HttpException`; one error middleware turns it into the reply."""

    slug = "throw-http-exceptions"
    node_types = ("Route", "NodeRoot")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [Finding(node, message) for message in [
            f"{node.source.file}:{line}: `{found}` throws an ad hoc value; throw an `HttpException`."
            for line, found in node.get_fact(fact_names.AD_HOC_THROWS, [])
        ] + [
            f"{node.source.file}:{line}: `{found}` answers an error by hand; throw an `HttpException` for the error middleware."
            for line, found in node.get_fact(fact_names.ERROR_REPLIES, [])
        ]]


class OneHomeForWebPaths(PracticeGraphRule):
    """Browser paths are string literals in one `*-paths.ts` module; every other file imports them."""

    slug = "one-home-for-web-paths"
    node_types = ("Aggregate",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{relative}:{line}: web path {path!r} is a literal; import it from the aggregate's `*-paths.ts` module.")
            for relative, line, path in node.get_fact(fact_names.WEB_PATH_LITERALS, [])
        ]


class ResetEveryRepository(PracticeGraphRule):
    """Every exported repository instance is reset by the test setup, so no story sees another's state.

    In-memory repositories are checked on their Repository node, node repositories on the `-node.ts` file.
    """

    slug = "reset-every-repository"
    node_types = ("Repository", "NodeRoot")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"`{instance}` ({class_name}) is never reset by the test setup; add it to the repositories every story resets.")
            for instance, class_name in node.get_fact(fact_names.UNRESET_INSTANCES, [])
        ]
