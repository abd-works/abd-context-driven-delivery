"""Bridge between the DDD aggregate model and the Clean Engineering class model.

Code channels (python, typescript) speak Clean Engineering: modules of classes. The aggregate model speaks
bounded contexts, aggregates, and stereotyped class cards. Each class carries where it lives and what it is
in its intent's first line — `<<Aggregate Root>> <<Entity>> Customer · Customer Profile` — so the docstring
or JSDoc that the code channels already write is enough to rebuild the aggregate view from code.
"""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.ddd.model.markdown.class_cards import (
    ClassCard,
    ordered_stereotypes,
    plain_properties,
    stereotypes_in,
)
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContext,
    MarkdownBoundedContextMap,
    MarkdownEntity,
    MarkdownIntegration,
)
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

_PLACE = " · "
_STEREOTYPE = re.compile(r"<<\s*[^>]+?\s*>>")
_DEFAULT_CONTEXT = "Domain"


def to_clean_engineering(bounded_context_map: BoundedContextMap) -> CleanEngineeringModel:
    """One module per aggregate; each class keeps its stereotypes and place in its intent."""
    model = CleanEngineeringModel("model", 1)
    for context, aggregate in _placed_aggregates(bounded_context_map.contexts, []):
        place = _PLACE.join(context + [aggregate.name])
        module = Module(place, len(model.modules) + 1)
        for card in _cards_in_order(aggregate):
            module.classes.append(_class_from_card(card, place, len(module.classes) + 1))
        if module.classes and aggregate.integrations:
            module.classes[0].intent += "\n" + "\n".join(_integration_text(aggregate))
        if not module.classes and aggregate.root is not None:
            root = OoadClass(aggregate.root.name, 1, intent=place)
            root.operations = [item.clone() for item in aggregate.root.operations]
            module.classes.append(root)
        model.modules.append(module)
    return model


def from_clean_engineering(model: CleanEngineeringModel) -> MarkdownBoundedContextMap:
    """Rebuild contexts and aggregates from each class's place, or group classes around their roots."""
    bounded_context_map = MarkdownBoundedContextMap()
    contexts: dict[tuple[str, ...], MarkdownBoundedContext] = {}
    aggregates: dict[tuple[str, ...], MarkdownAggregate] = {}
    unplaced: list[tuple[str, ClassCard]] = []
    for module in model.modules:
        for oclass in module.classes:
            if oclass.name.startswith("_"):
                continue
            card, place = _card_from_class(oclass)
            if len(place) >= 2:
                _aggregate(bounded_context_map, contexts, aggregates, place[:-1], place[-1]).cards.append(card)
            else:
                unplaced.append((module.name or _DEFAULT_CONTEXT, card))
    for context_name, aggregate_name, card in _grouped(unplaced):
        _aggregate(bounded_context_map, contexts, aggregates, [context_name], aggregate_name).cards.append(card)
    for aggregate in aggregates.values():
        _infer_relationships(aggregate)
        _take_integrations(aggregate)
        aggregate._take_root_card()
        if aggregate.root is None:
            aggregate.root = MarkdownEntity(aggregate.name, 1)
    return bounded_context_map


def _placed_aggregates(contexts, path: list[str]):
    for context in contexts:
        label = f"{context.name} | {context.owner}" if context.owner else context.name
        for aggregate in context.aggregates:
            yield path + [label], aggregate
        yield from _placed_aggregates(context.contexts, path + [label])


def _cards_in_order(aggregate) -> list[ClassCard]:
    cards = list(getattr(aggregate, "cards", []) or [])
    roots = [card for card in cards if card.is_root]
    repositories = [card for card in cards if card.is_repository]
    return roots + repositories + [card for card in cards if card not in roots and card not in repositories]


def _class_from_card(card: ClassCard, place: str, order: int) -> OoadClass:
    tags = " ".join(f"<<{item}>>" for item in card.stereotypes)
    intent = f"{tags} {place}".strip()
    if card.node.intent:
        intent = f"{intent}\n{card.node.intent}"
    oclass = OoadClass(card.node.name, order, intent=intent)
    oclass.properties = [item.clone() for item in plain_properties(card.node)]
    oclass.operations = [item.clone() for item in card.node.operations]
    return oclass


def _card_from_class(oclass: OoadClass) -> tuple[ClassCard, list[str]]:
    first, _, rest = (oclass.intent or "").partition("\n")
    marks = stereotypes_in(first)
    place_text = _STEREOTYPE.sub("", first).strip() if marks else ""
    place = [part.strip() for part in place_text.split("·") if part.strip()] if place_text else []
    if not marks:
        rest = oclass.intent or ""
    stereotypes = ordered_stereotypes(marks or _stereotypes_by_name(oclass.name))
    heading = f"{oclass.name} {' '.join(f'<<{item}>>' for item in stereotypes)}"
    node_type = MarkdownAggregate().building_block_type(heading)
    if not isinstance(node_type, type) or not issubclass(node_type, OoadClass):
        node_type = OoadClass
    node = node_type(oclass.name, oclass.sequential_order)
    node.intent = rest.strip()
    node.properties = [item.clone() for item in oclass.properties]
    node.operations = [item.clone() for item in oclass.operations if item.name not in (oclass.name, "constructor", "__init__")]
    return ClassCard(node, stereotypes), place


def _stereotypes_by_name(name: str) -> list[str]:
    return ["Repository"] if name.endswith("Repository") and name != "Repository" else []


def _grouped(unplaced: list[tuple[str, ClassCard]]):
    """Classes with no place: each root, or each class nobody composes, opens an aggregate; the rest join it."""
    names = {card.node.name: (context, card) for context, card in unplaced}
    owner: dict[str, str] = {}
    for context, card in unplaced:
        for prop in card.node.properties:
            for target in re.split(r"[\[\]<>|,\s]+", prop.type_hint or ""):
                if target in names and target != card.node.name and not names[target][1].is_root:
                    owner.setdefault(target, card.node.name)
        if card.is_repository:
            root = card.node.name[: -len("Repository")]
            if root in names:
                owner.setdefault(card.node.name, root)
                if not names[root][1].stereotypes:
                    # A class the business keeps in its own repository is an aggregate root.
                    names[root][1].stereotypes = ["Aggregate Root", "Entity"]
    for context, card in unplaced:
        top = card.node.name
        seen = set()
        while top in owner and top not in seen:
            seen.add(top)
            top = owner[top]
        yield context, top, card


def _aggregate(bounded_context_map, contexts, aggregates, path: list[str], aggregate_name: str) -> MarkdownAggregate:
    context = _context(bounded_context_map, contexts, tuple(path))
    key = tuple(path) + (aggregate_name,)
    if key not in aggregates:
        aggregate = MarkdownAggregate(aggregate_name, len(context.aggregates) + 1)
        context.append_aggregate(aggregate)
        aggregates[key] = aggregate
    return aggregates[key]


def _context(bounded_context_map, contexts, path: tuple[str, ...]) -> MarkdownBoundedContext:
    # A nested context is a context whose parent is a context.
    if path in contexts:
        return contexts[path]
    name, _, owner = path[-1].partition("|")
    context = MarkdownBoundedContext(name.strip(), 1)
    context.owner = owner.strip()
    context._map = bounded_context_map
    if len(path) == 1:
        context.sequential_order = len(bounded_context_map.contexts) + 1
        bounded_context_map.contexts.append(context)
    else:
        parent = _context(bounded_context_map, contexts, path[:-1])
        context.sequential_order = len(parent.contexts) + 1
        parent.append_context(context)
    contexts[path] = context
    return context


def _infer_relationships(aggregate: MarkdownAggregate) -> None:
    # Code holds `identity: Identity`, not `<< composition >>`; the aggregate's own members say which kind it is.
    members = {card.node.name for card in aggregate.cards if not card.is_root and not card.is_repository}
    roots = {card.node.name for card in aggregate.cards if card.is_root}
    for card in aggregate.cards:
        for prop in plain_properties(card.node):
            if prop.stereotype:
                continue
            named = [part for part in re.split(r"[\[\]<>|,\s]+", prop.type_hint or "") if part]
            if card.is_repository and any(part in roots for part in named[1:]):
                prop.stereotype = "aggregation"
            elif named and named[0] in members:
                prop.stereotype = "composition"


_INTEGRATION_FIELDS = ("pattern", "direction", "crosses", "integration")


def _integration_text(aggregate) -> list[str]:
    # The map's arcs ride in the root's doc comment, one field per line, so code keeps them.
    lines = ["Integrations:"]
    for item in aggregate.integrations:
        lines.append(f"- {item.target}")
        lines.extend(f"{key}: {getattr(item, key)}" for key in _INTEGRATION_FIELDS if getattr(item, key))
    return lines


def _take_integrations(aggregate: MarkdownAggregate) -> None:
    for card in aggregate.cards:
        intent = card.node.intent or ""
        if "Integrations:" not in intent:
            continue
        kept, _, arcs = intent.partition("Integrations:")
        card.node.intent = kept.strip()
        current = None
        for line in (line.strip() for line in arcs.splitlines()):
            if line.startswith("- "):
                current = MarkdownIntegration()
                current.target = line[2:].strip()
                context, aggregate_name, _ = _target_parts(current.target)
                current.context, current.aggregate = context, aggregate_name
                aggregate.integrations.append(current)
            elif current is not None and ":" in line:
                key, value = (part.strip() for part in line.split(":", 1))
                if key in _INTEGRATION_FIELDS:
                    setattr(current, key, value)


def _target_parts(target: str) -> tuple[str, str, str]:
    from cdd_guidance.practices.ddd.model.markdown.nodes import _parse_arrow_target

    return _parse_arrow_target(target)
