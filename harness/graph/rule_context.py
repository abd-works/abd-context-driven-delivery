"""Shared context for graph rule checks — model parse caches and graph helpers."""

from __future__ import annotations

import hashlib
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
        self._story_model = None
        self._story_model_failed = False

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
        if node.type == "Operation" and text and node.name:
            relative = (node.source.file or "").lower()
            matched = self.ce_operation(node)
            if relative.endswith(".py") and matched is not None:
                _oclass, operation = matched
                if operation.line and operation.line_count:
                    start = operation.line
                    end = operation.line + operation.line_count - 1
            elif relative.endswith((".ts", ".tsx", ".js", ".jsx", ".java", ".mjs")):
                from harness.graph.working_copy import _method_span

                method_start, method_end = _method_span(text, node.name, start or 1)
                if method_end >= method_start:
                    start, end = method_start, method_end
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
        model = channel().parse(text)
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

    def children(self, node, edge_kind: str) -> list:
        return [
            edge.child
            for edge in self.practice.edges.get(edge_kind, [])
            if edge.parent is node
        ]

    def module_folder(self, node) -> Path | None:
        if not self.source_root or not node.source.file:
            return None
        folder = node.source.file.strip("./")
        return self.source_root / folder if folder else self.source_root

    def story_model(self):
        if self._story_model_failed:
            return None
        if self._story_model is not None:
            return self._story_model
        if not self.source_root:
            self._story_model_failed = True
            return None
        try:
            from practices.stories.model.story_model import StoryModel

            self._story_model = StoryModel.load(self.source_root)
        except Exception:
            self._story_model_failed = True
            return None
        return self._story_model

    def operation_fingerprint(self, node, operation: Operation) -> str:
        span = self.span(node).strip()
        if not span:
            return ""
        normalized = re.sub(r"\s+", " ", span)
        return hashlib.sha256(normalized.encode()).hexdigest()[:24]

    def ce_parameter(self, node):
        if node.type != "Parameter":
            return None
        owner = _owner_class_name(node)
        op_name = _operation_name_from_param_node(node)
        model = self.clean_engineering_model(node)
        if model is None:
            return None
        for module in model.modules:
            for oclass in module.classes:
                if owner and oclass.name != owner:
                    continue
                for op in oclass.operations:
                    if op_name and op.name != op_name:
                        continue
                    for param in op.parameters:
                        if param.name == node.name:
                            return param
        return None


def _operation_name_from_param_node(node) -> str:
    parts = str(node.node_id or "").split(":")
    if len(parts) >= 2:
        tail = parts[-1]
        if "." in tail:
            return tail.rsplit(".", 1)[-1]
    return ""


def _owner_class_name(node) -> str:
    parts = str(node.node_id or "").split(":")
    if len(parts) >= 2 and parts[-1]:
        return parts[-1]
    match = re.search(r":([A-Za-z]\w*)$", str(node.node_id or ""))
    return match.group(1) if match else ""
