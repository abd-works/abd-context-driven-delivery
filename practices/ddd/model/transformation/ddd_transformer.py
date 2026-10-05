"""DDD transformation channel — folders for contexts and aggregates."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment

from harness.sketch.sketch_outline import SketchLens, SketchOutline
from harness.transformers.transformer import Transformer
from practices.ddd.model.nodes import Aggregate, BoundedContext

_NESTING_INDENT = 2
_EVENT_MAP = ("event_map", "event map")
_SNAKE = re.compile(r"([^0-9a-z]+)")


class DddTransformer(Transformer):
    logical_template_root = Path(__file__).resolve().parent / "logical"
    _tests_folder = "domain"

    def __init__(self, name: str = "", sequential_order: int = 1) -> None:
        self.name = name
        self.sequential_order = sequential_order
        self.contexts: list[BoundedContextTransformer] = []

    @classmethod
    def load(cls, sketch: str) -> "DddTransformer":
        root = cls()
        _parse_ddd_sketch(root, sketch)
        return root

    def children(self) -> list:
        return list(self.contexts)

    def attach_environment(self, environment: Environment, root: Transformer | None = None) -> None:
        environment.filters["kebab"] = _to_kebab
        super().attach_environment(environment, root)

    def _child_folder(self) -> str:
        return self._tests_folder


class BoundedContextTransformer(Transformer, BoundedContext):
    _logical_template = "bounded_context"

    def children(self) -> list:
        return list(self.contexts) + list(self.aggregates)

    def _output_path(self) -> str:
        return f"{self._child_folder()}/.context/bounded-context.md"

    def _child_folder(self) -> str:
        return f"{self._tests_folder}/{_to_kebab(self.name)}"


class AggregateTransformer(Transformer, Aggregate):
    def children(self) -> list:
        return []

    def _child_folder(self) -> str:
        return f"{self._tests_folder}/{_to_kebab(self.name)}"


def _parse_ddd_sketch(root: DddTransformer, sketch: str) -> None:
    context: BoundedContextTransformer | None = None
    body = SketchOutline(sketch, _NESTING_INDENT).body_for(SketchLens.domain_driven_design)
    for raw in body.splitlines():
        if not raw.strip() or raw.strip().startswith("-"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        level = indent // _NESTING_INDENT
        name, _, owner = raw.strip().partition("|")
        name = name.strip().rstrip("/").rstrip(":")
        owner = owner.strip()
        if name.lower() in _EVENT_MAP:
            context = None
            continue
        if level == 0:
            context = BoundedContextTransformer(name, len(root.contexts) + 1)
            context.owner = owner
            root.contexts.append(context)
            continue
        if context is None or level != 1:
            continue
        context.aggregates.append(AggregateTransformer(name, len(context.aggregates) + 1))


def _to_kebab(name: str) -> str:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return _SNAKE.sub("-", spaced.strip().lower()).strip("-") or "unnamed"
