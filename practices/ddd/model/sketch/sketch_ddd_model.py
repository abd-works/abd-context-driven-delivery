"""Sketch channel — indent bounded-context map from a DDD sketch."""

from __future__ import annotations

import re

from practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContext,
    MarkdownBoundedContextMap,
    _aggregates_in,
    _services_in,
    _wire_event,
)

_FENCE = re.compile(r"```(?:\w*)\n(.*?)```", re.DOTALL)
_KEYS = (
    "owner:",
    "system:",
    "emits:",
    "consumes:",
    "members:",
    "integrations:",
    "refs:",
    "depends:",
    "repo:",
    "events:",
    "event_map:",
    "event map:",
)


class SketchDddModel(MarkdownBoundedContextMap):
    def parse(self, text: str) -> "SketchDddModel":
        model = type(self)()
        body = _FENCE.sub(lambda match: "\n" + match.group(1) + "\n", text)
        context: MarkdownBoundedContext | None = None
        aggregate: MarkdownAggregate | None = None
        event_lines: list[str] = []
        in_events = False
        for raw in body.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith(("//", "#", "---")):
                continue
            lowered = stripped.lower()
            if lowered.startswith("fidelity:"):
                continue
            if lowered in {"event_map:", "event map:", "event_map", "event map"}:
                in_events = True
                continue
            if in_events:
                if stripped.startswith("- "):
                    event_lines.append(stripped[2:])
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            level = indent // 2
            if lowered.startswith("owner:") and context is not None:
                context.owner = stripped.split(":", 1)[1].strip()
                continue
            if lowered.startswith("system:"):
                continue
            if any(lowered.startswith(key) for key in _KEYS) and aggregate is not None:
                aggregate._body.append(raw)
                continue
            if level <= 0:
                name = stripped.rstrip(":")
                context = MarkdownBoundedContext(name, len(model.contexts) + 1)
                context._map = model
                model.contexts.append(context)
                aggregate = None
                continue
            if context is None:
                continue
            if level == 1 and not lowered.startswith("-"):
                name = stripped.rstrip(":")
                if "<<" in name:
                    name = name.split("<<", 1)[0].strip()
                aggregate = MarkdownAggregate(name, len(context.aggregates) + 1)
                context.append_aggregate(aggregate)
                continue
            if aggregate is not None:
                aggregate._body.append(raw)
        for item in model.contexts:
            for child in item.aggregates:
                if isinstance(child, MarkdownAggregate):
                    child.load_root()
        aggregates = {row.name: row for row in _aggregates_in(model)}
        services = {row.name: row for row in _services_in(model)}
        for line in event_lines:
            _wire_event(line, aggregates, services)
        return model

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return _as_sketch(canonical or self)


def _as_sketch(model: MarkdownBoundedContextMap) -> str:
    lines: list[str] = []
    for context in model.contexts:
        heading = context.name
        if context.owner:
            heading = f"{context.name} | {context.owner}"
        lines.append(heading)
        for aggregate in context.aggregates:
            lines.append(f"  {aggregate.name}:")
            if isinstance(aggregate, MarkdownAggregate) and aggregate._body:
                lines.extend(aggregate._body)
        lines.append("")
    return "\n".join(lines)
