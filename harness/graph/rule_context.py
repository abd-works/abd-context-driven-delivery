"""Shared context for graph rule checks — model parse caches and graph helpers."""

from __future__ import annotations

import re
from pathlib import Path

from practices.clean_engineering.model.base_class_model import CleanEngineeringModel, OoadClass, Operation

_CE_CHANNELS: dict[str, type] = {}


def _ce_channels() -> dict[str, type]:
    global _CE_CHANNELS
    if _CE_CHANNELS:
        return _CE_CHANNELS
    from practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
    from practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
    from practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel

    _CE_CHANNELS.update(
        {
            ".py": PythonCleanEngineeringModel,
            ".ts": TypeScriptCleanEngineeringModel,
            ".tsx": TypeScriptCleanEngineeringModel,
            ".js": JavaScriptCleanEngineeringModel,
            ".jsx": JavaScriptCleanEngineeringModel,
        }
    )
    return _CE_CHANNELS


class RuleCheckContext:
    """File text and parsed models for one practice load."""

    def __init__(self, practice, source_root: Path | None) -> None:
        self.practice = practice
        self.source_root = source_root
        self._files: dict[str, str] = {}
        self._ce_models: dict[str, CleanEngineeringModel] = {}

    def text(self, node) -> str:
        if not self.source_root or not node.source.file:
            return ""
        relative = node.source.file
        if relative not in self._files:
            path = self.source_root / relative
            self._files[relative] = path.read_text(encoding="utf-8") if path.is_file() else ""
        return self._files[relative]

    def span(self, node) -> str:
        text = self.text(node)
        start = node.source.start_line
        end = node.source.end_line
        if not text or not start or not end or end < start:
            return text
        return "\n".join(text.splitlines()[start - 1 : end])

    def clean_engineering_model(self, node) -> CleanEngineeringModel | None:
        if not node.source.file:
            return None
        relative = node.source.file
        if relative in self._ce_models:
            return self._ce_models[relative]
        path = (self.source_root or Path(".")) / relative
        channel = _ce_channels().get(path.suffix.lower())
        if channel is None:
            return None
        text = self.text(node)
        if not text:
            return None
        model = channel.parse(text)
        self._ce_models[relative] = model
        return model

    def ce_class(self, node) -> OoadClass | None:
        if node.type != "OoadClass":
            return None
        model = self.clean_engineering_model(node)
        if model is None:
            return None
        for module in model.modules:
            for oclass in module.classes:
                if oclass.name == node.name:
                    return oclass
        return None

    def ce_operation(self, node) -> tuple[OoadClass, Operation] | None:
        if node.type != "Operation":
            return None
        model = self.clean_engineering_model(node)
        if model is None:
            return None
        owner = _owner_class_name(node)
        for module in model.modules:
            for oclass in module.classes:
                if owner and oclass.name != owner:
                    continue
                for op in oclass.operations:
                    if op.name == node.name or (op.name == "constructor" and node.name == "constructor"):
                        return oclass, op
        return None

    def child_count(self, node, edge_kinds: tuple[str, ...]) -> int:
        count = 0
        for kind in edge_kinds:
            for edge in self.practice.edges.get(kind, []):
                if edge.parent is node:
                    count += 1
        return count


def _owner_class_name(node) -> str:
    parts = str(node.node_id or "").split(":")
    if len(parts) >= 2 and parts[-1]:
        return parts[-1]
    match = re.search(r":([A-Za-z]\w*)$", str(node.node_id or ""))
    return match.group(1) if match else ""
