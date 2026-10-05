"""BDD transformation channel — wrap Description, Context, and Observation."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment

from harness.sketch.sketch_outline import SketchLens, SketchOutline
from harness.transformers.transformer import Transformer
from practices.bdd.model.nodes import Context, Description, Observation

_NESTING_INDENT = 2
_SNAKE = re.compile(r"([^0-9a-z]+)")


class BddTransformer(Transformer):
    logical_template_root = Path(__file__).resolve().parent / "logical" / "python"

    def __init__(self, name: str = "", sequential_order: int = 1) -> None:
        self.name = name
        self.sequential_order = sequential_order
        self.descriptions: list[DescriptionTransformer] = []

    @classmethod
    def load(cls, sketch: str) -> "BddTransformer":
        root = cls()
        _parse_bdd_sketch(root, sketch)
        return root

    def children(self) -> list:
        return list(self.descriptions)

    def attach_environment(self, environment: Environment, root: Transformer | None = None) -> None:
        environment.filters["snake"] = _to_snake
        super().attach_environment(environment, root)


class DescriptionTransformer(Transformer, Description):
    _logical_template = "description"
    _tests_folder = "tests"

    def children(self) -> list:
        return []

    def _output_path(self) -> str:
        return f"{self._tests_folder}/{_to_snake(self.name)}_spec.py"


class ContextTransformer(Transformer, Context):
    pass


class ObservationTransformer(Transformer, Observation):
    pass


def _parse_bdd_sketch(root: BddTransformer, sketch: str) -> None:
    description: DescriptionTransformer | None = None
    stack: list[tuple[int, ContextTransformer]] = []
    body = SketchOutline(sketch, _NESTING_INDENT).body_for(
        SketchLens.behavior_driven_development
    )
    for raw in body.splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        level = indent // 2
        if stripped.startswith("it "):
            host = stack[-1][1] if stack else None
            if host is None:
                continue
            name = stripped[3:].strip() if stripped.startswith("it ") else stripped
            host.observations.append(
                ObservationTransformer(name, len(host.observations) + 1)
            )
            continue
        if level == 0:
            description = DescriptionTransformer(stripped, len(root.descriptions) + 1)
            root.descriptions.append(description)
            stack = []
            continue
        if description is None:
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_contexts = stack[-1][1].contexts if stack else description.contexts
        context = ContextTransformer(stripped, len(parent_contexts) + 1)
        parent_contexts.append(context)
        stack.append((level, context))


def _to_snake(name: str) -> str:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return _SNAKE.sub("_", spaced.strip().lower()).strip("_") or "unnamed"
