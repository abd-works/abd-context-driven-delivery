"""CDD web domain access rules — read the facts recorded on each access node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class OneClassPerObject(PracticeGraphRule):
    """Code that calls a tool by name is a second, hand-kept copy of the object's generated adapter."""

    slug = "one-class-per-object"
    node_types = ("AccessRoute", "AccessNode")

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` calls a tool directly; call the {{Object}}Adapter operation for it."
            for line, code in node.get_fact("tool_calls", [])
        ]


class StateLivesBehindTheTool(PracticeGraphRule):
    """A store beside a tool is a second copy of a fact the agent changes without telling the application."""

    slug = "state-lives-behind-the-tool"
    node_types = ("AccessNode",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` keeps a store on an object CDD owns; read it through its tool."
            for line, code in node.get_fact("store_imports", [])
        ]


class AdapterIsGenerated(PracticeGraphRule):
    """A hand-kept adapter or connection drifts from Python, and the compiler then checks the wrong thing."""

    slug = "adapter-is-generated"
    node_types = ("AccessHandWrittenAdapter", "AccessNode")

    def check(self, node, context) -> list[str]:
        if node.type == "AccessHandWrittenAdapter":
            return [f"{node.source.file}: is an adapter or connection written by hand; mark the toolset with @language_adapter and install."]
        if node.get_fact("extends_adapter", False):
            return [f"{node.source.file}: extends a generated adapter; use {{Object}}Adapter and its {{operation}}Requested directly."]
        return []


class AnnotateWhatTypeScriptReads(PracticeGraphRule):
    """An open result generates `Record<string, unknown>`, which the compiler cannot check."""

    slug = "annotate-what-typescript-reads"
    node_types = ("AccessMarkedToolset",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{operation}` returns dict[str, Any]; return a domain object whose properties are marked with @data_field."
            for line, operation in node.get_fact("open_results", [])
        ]
