"""JSON line host for CodeQLGraph. The app calls these operations. It does not keep a second graph."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_GRAPH = Path(__file__).resolve().parents[1]
if str(_GRAPH) not in sys.path:
    sys.path.insert(0, str(_GRAPH))

from graph import CodeQLGraph, CodeQLNode


class GraphHost:
    """One CodeQLGraph. Each operation is the graph operation of the same name."""

    def __init__(self, graph: CodeQLGraph | None = None) -> None:
        self.graph = graph or CodeQLGraph()

    def load_working_copy(self, folder: str, practices: dict[str, str], database: str | None = None) -> str:
        return self.graph.load_working_copy(folder, practices, database)

    def inventory(self) -> dict:
        return self.graph.inventory()

    def return_nodes(self, selection: dict | None = None) -> list[dict]:
        self._apply_filter(selection or {})
        return json.loads(self.graph.return_nodes())

    def filter_choices(self, selection: dict | None = None) -> dict:
        picked = selection or {}
        self.graph.filter.clear()
        practices = list(picked.get("practices") or [])
        node_types = list(picked.get("node_types") or [])
        if practices:
            self.graph.filter.select_practices(practices)
        if node_types:
            self.graph.filter.select_node_types(node_types)
        chosen = self.graph.filter
        return {
            "node_types": list(chosen.node_types),
            "relationships": list(chosen.relationships),
            "rules": list(chosen.rules),
        }

    def source(self, node_id: str) -> dict:
        node = self._node(node_id)
        if node is None:
            return {}
        return {
            "node_id": node.node_id,
            "name": node.name,
            "type": node.type,
            "file": node.source.file,
            "text": node.source.text,
            "start_line": node.source.start_line,
            "end_line": node.source.end_line,
            "members": self._members(),
        }

    def create_database(self, folder: str, practices: dict[str, str], database: str | None = None) -> str:
        message = self.graph.create_database(folder, practices, database)
        self.graph.load_working_copy(folder, practices, database)
        return message

    def reload_working_copy(self) -> str:
        return self.graph.reload_working_copy()

    def update_working_copy(self, paths: list[str]) -> str:
        return self.graph.update_working_copy(paths)

    def choose_folder(self) -> str:
        import tkinter
        from tkinter import filedialog

        window = tkinter.Tk()
        window.withdraw()
        window.attributes("-topmost", True)
        chosen = filedialog.askdirectory(title="Select a repo folder")
        window.destroy()
        return chosen or ""

    def handle(self, request: dict) -> dict:
        operation = str(request.get("operation", ""))
        runner = self._operations().get(operation)
        if runner is None:
            return {"ok": False, "error": f"Unknown operation {operation}"}
        return {"ok": True, "result": runner(request)}

    def _operations(self) -> dict:
        return {
            "load_working_copy": self._load,
            "inventory": lambda _request: self.inventory(),
            "return_nodes": lambda request: self.return_nodes(request.get("filter")),
            "filter_choices": lambda request: self.filter_choices(request.get("filter")),
            "source": lambda request: self.source(str(request.get("node_id", ""))),
            "create_database": self._create,
            "reload_working_copy": lambda _request: self.reload_working_copy(),
            "update_working_copy": lambda request: self.update_working_copy(list(request.get("paths") or [])),
            "choose_folder": lambda _request: self.choose_folder(),
        }

    def _load(self, request: dict) -> str:
        return self.load_working_copy(
            str(request.get("folder", "")),
            dict(request.get("practices") or {}),
            request.get("database"),
        )

    def _create(self, request: dict) -> str:
        return self.create_database(
            str(request.get("folder", "")),
            dict(request.get("practices") or {}),
            request.get("database"),
        )

    def _apply_filter(self, selection: dict) -> None:
        self.graph.filter.clear()
        practices = list(selection.get("practices") or [])
        node_types = list(selection.get("node_types") or [])
        relationships = list(selection.get("relationships") or [])
        rules = list(selection.get("rules") or [])
        if practices:
            self.graph.filter.select_practices(practices)
        if node_types:
            self.graph.filter.select_node_types(node_types)
        if relationships:
            self.graph.filter.select_relationships(relationships)
        if selection.get("violations"):
            self.graph.filter.select_rules(rules)
            self.graph.filter.select_violations()

    def _members(self) -> list[dict]:
        classes = {
            "OoadClass",
            "Entity",
            "EntityRoot",
            "ValueObject",
            "Aggregate",
            "Repository",
            "DomainEvent",
            "DomainService",
            "Specification",
        }
        wanted = classes | {"Operation", "Property"}
        members: list[dict] = []
        for practice in self.graph.practices.values():
            for node in practice.by_id.values():
                if node.type not in wanted:
                    continue
                members.append(
                    {
                        "id": node.node_id,
                        "name": node.name,
                        "kind": node.type,
                        "owner": "" if node.type in classes else self._owner(node, classes),
                        "text": node.source.text,
                        "file": node.source.file,
                        "start": node.source.start_line,
                        "end": node.source.end_line,
                    }
                )
        return members

    def _owner(self, node: CodeQLNode, classes: set[str]) -> str:
        parent = node.parent
        while parent is not None:
            if parent.type in classes:
                return parent.name
            parent = parent.parent
        return ""

    def _node(self, node_id: str) -> CodeQLNode | None:
        for practice in self.graph.practices.values():
            node = practice.by_id.get(node_id)
            if node is not None:
                return node
        return None


def serve() -> None:
    host = GraphHost()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = host.handle(request)
        except Exception as error:
            response = {"ok": False, "error": str(error)}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    serve()
