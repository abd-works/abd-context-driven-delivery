"""CDD access rules — read the facts recorded on each access node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class RoutesAskTheObject(PracticeGraphRule):
    """A route that calls a tool has skipped the object's typed operation."""

    slug = "routes-ask-the-object"
    node_types = ("AccessRoute",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` calls a tool from a route; ask the {{Object}}Node for its operation."
            for line, code in node.get_fact("tool_calls", [])
        ]


class OneClassPerObject(PracticeGraphRule):
    """A node that calls tools by name is a second, hand-kept copy of its generated class."""

    slug = "one-class-per-object"
    node_types = ("AccessNode",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` calls a tool directly; call the operation it inherits from {{Object}}Tools."
            for line, code in node.get_fact("tool_calls", [])
        ]


class NodeExtendsTheAdapter(PracticeGraphRule):
    """Everything on the server has one object to talk to only when the node is that object."""

    slug = "node-extends-the-adapter"
    node_types = ("AccessNode",)

    def check(self, node, context) -> list[str]:
        if not node.get_fact("reaches_cdd", False) or node.get_fact("extends_tools", False):
            return []
        return [f"{node.source.file}: imports the language adapter without extending {{Object}}Tools; make it {{Object}}Node extends {{Object}}Tools."]


class StateLivesBehindTheTool(PracticeGraphRule):
    """A store beside a tool is a second copy of a fact the agent changes without telling the application."""

    slug = "state-lives-behind-the-tool"
    node_types = ("AccessNode",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` keeps a store on an object CDD owns; read it through its tool."
            for line, code in node.get_fact("store_imports", [])
        ]


class ConnectionOnlyCarries(PracticeGraphRule):
    """A tool name in the connection is an operation that belongs on its object."""

    slug = "connection-only-carries"
    node_types = ("AccessConnection",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` names a tool; the connection carries calls and names none."
            for line, code in node.get_fact("named_tools", [])
        ]


class TextThatIsNotJsonIsAFailure(PracticeGraphRule):
    """The MCP server sends a failed operation's error as plain text, so a blind parse loses the real reason."""

    slug = "text-that-is-not-json-is-a-failure"
    node_types = ("AccessConnection",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` parses without a guard; raise CddToolError with the text when it is not JSON."
            for line, code in node.get_fact("bare_parses", [])
        ]


class AdapterIsGenerated(PracticeGraphRule):
    """A hand-kept tools class drifts from Python, and the compiler then checks the wrong thing."""

    slug = "adapter-is-generated"
    node_types = ("AccessHandWrittenTools",)

    def check(self, node, context) -> list[str]:
        return [f"{node.source.file}: is a tools class written by hand; mark the toolset with @language_adapter and install."]


class AnnotateWhatTypeScriptReads(PracticeGraphRule):
    """An open result generates `Record<string, unknown>`, which the compiler cannot check."""

    slug = "annotate-what-typescript-reads"
    node_types = ("AccessMarkedToolset",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{operation}` returns dict[str, Any]; annotate it with a TypedDict."
            for line, operation in node.get_fact("open_results", [])
        ]
