"""DDD transformation channel — folders for contexts and aggregates."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment

from harness.transformers.transformer import Transformer
from practices.ddd.model.nodes import Aggregate, BoundedContext

_LENS = "ddd:"
_NEXT_LENSES = ("stories:", "ce:", "bdd:", "ux:")
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
    for raw in _lens_body(sketch).splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        level = indent // 2
        name, _, owner = raw.strip().partition("|")
        name = name.strip().rstrip("/")
        owner = owner.strip()
        if level <= 1:
            context = BoundedContextTransformer(name, len(root.contexts) + 1)
            context.owner = owner
            root.contexts.append(context)
            continue
        if context is None or level != 2:
            continue
        context.aggregates.append(AggregateTransformer(name, len(context.aggregates) + 1))


def _to_kebab(name: str) -> str:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return _SNAKE.sub("-", spaced.strip().lower()).strip("-") or "unnamed"


def _lens_body(sketch: str) -> str:
    lines = sketch.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(_LENS)), None)
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if any(lines[index].startswith(marker) for marker in _NEXT_LENSES):
            end = index
            break
    return "\n".join(lines[start + 1 : end])
