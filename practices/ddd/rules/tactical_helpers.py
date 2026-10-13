"""Shared checks for DDD tactical graph rules."""

from __future__ import annotations

import re

from practices.ddd.model.stereotypes import class_stereotypes, inferred_tactical_kind, plain_class_name

_TECHNICAL_SUFFIXES = frozenset({"result", "response", "dto", "request"})
_AGENT_NOUNS = frozenset({"manager", "helper", "processor", "handler", "controller"})
_CAMEL = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])")


def ident_tokens(name: str) -> list[str]:
    return [token.lower() for token in _CAMEL.findall(name or "") if token]

_REPOSITORY_LIFECYCLE = re.compile(
    r"^(?:add|remove|delete|find|get|load|save|store|fetch|by_id|find_by)",
    re.IGNORECASE,
)
_UI_METHODS = frozenset({"open", "isshowing", "close", "show", "hide", "select"})
_DERIVE_PREFIX = re.compile(r"^derive\w*", re.IGNORECASE)


def stereotyped_declaration_name(text: str, class_name: str) -> str:
    match = re.search(rf"(?:export\s+)?(?:abstract\s+)?class\s+{re.escape(class_name)}\b", text)
    if match is None:
        return class_name
    prefix = text[max(0, match.start() - 240) : match.start()]
    comment = re.search(r"/\*\*([\s\S]*?)\*/\s*$", prefix)
    if comment is None:
        return class_name
    tags = re.findall(r"<<[^>]+>>", comment.group(1))
    if not tags:
        return class_name
    return f"{class_name} {' '.join(tags)}"


def class_names_in_text(context, node) -> set[str]:
    model = context.clean_engineering_model(node)
    if model is None:
        return set()
    return {cls.name for module in model.modules for cls in module.classes}


def name_reflects_tactical_kind(class_name: str, kind: str, names: set[str]) -> bool:
    plain = plain_class_name(class_name)
    if kind == "Repository":
        return plain.endswith("Repository")
    if kind == "DomainService":
        return plain.endswith("Service")
    if kind == "Specification":
        return plain.endswith("Specification") or "Specification" in plain
    if kind == "ValueObject":
        return any(plain.endswith(suffix) for suffix in ("Token", "Code", "Message", "Value"))
    if kind == "EntityRoot":
        return plain.endswith("Root") or f"{plain}Repository" in names
    if kind == "Entity":
        return plain.endswith("Entity") or (plain.endswith("Root") and kind == "EntityRoot")
    return False


def has_tactical_stereotype(context, node) -> bool:
    text = context.text(node)
    decorated = stereotyped_declaration_name(text, node.name)
    if class_stereotypes(decorated):
        return True
    names = class_names_in_text(context, node)
    kind = inferred_tactical_kind(decorated, names) or node.type
    mapped = kind if kind in {
        "Entity",
        "EntityRoot",
        "ValueObject",
        "Repository",
        "DomainService",
        "Specification",
    } else node.type
    return name_reflects_tactical_kind(node.name, mapped, names)


def technical_name_violation(class_name: str) -> str | None:
    tokens = ident_tokens(class_name)
    if not tokens:
        return None
    if tokens[-1] in _TECHNICAL_SUFFIXES or any(token in _AGENT_NOUNS for token in tokens):
        return f"Class '{class_name}' uses a technical name instead of a domain concept."
    return None


def repository_lifecycle_ops(context, node) -> list[str]:
    oclass = context.ce_class(node)
    if oclass is None:
        return []
    return [
        op.name
        for op in oclass.operations
        if op.name and _REPOSITORY_LIFECYCLE.search(op.name) and not op.name.startswith("_")
    ]


def is_screen_driver_class(context, node) -> bool:
    oclass = context.ce_class(node)
    if oclass is None:
        return False
    public = {
        op.name.lower()
        for op in oclass.operations
        if op.name and not str(op.name).startswith("_")
    }
    if public & _UI_METHODS and ("open" in public or "isshowing" in public):
        return True
    return bool(re.search(r"^(Select|Screen|Dialog|Modal|View|Page)\w*$", node.name))


def other_classes_reference(context, node, target: str) -> bool:
    model = context.clean_engineering_model(node)
    if model is None:
        return False
    for module in model.modules:
        for oclass in module.classes:
            if oclass.name == target:
                continue
            blob = context.text(node)
            if re.search(rf"\b{re.escape(target)}\b", blob):
                return True
            for op in oclass.operations:
                if target in (op.return_type or ""):
                    return True
                for param in op.parameters:
                    if target in (param.type_hint or ""):
                        return True
    return False
