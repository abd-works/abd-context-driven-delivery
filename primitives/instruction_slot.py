from __future__ import annotations

import functools
import inspect
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from .instruction import Instruction

F = TypeVar("F", bound=Callable[..., Any])


def instruction(
    func: F | None = None,
    *,
    collection: bool = False,
    group: str | None = None,
    filter_key: str | None = None,
    override: bool = False,
) -> F | Callable[[F], F]:
    def decorate(target: F) -> F:
        label = target.__name__

        if override:
            wrapped = target
        else:
            @functools.wraps(target)
            def wrapped(instance: Any) -> Any:
                from .instruction import Instruction

                return Instruction.ref(
                    instance,
                    label,
                    collection=collection,
                    group=group,
                    filter_key=filter_key,
                )

        wrapped._is_instruction_slot = True  # type: ignore[attr-defined]
        wrapped._instruction_collection = collection  # type: ignore[attr-defined]
        wrapped._instruction_group = group  # type: ignore[attr-defined]
        wrapped._instruction_filter_key = filter_key  # type: ignore[attr-defined]
        return wrapped  # type: ignore[return-value]

    if func is not None:
        return decorate(func)
    return decorate


def instruction_slot_names(toolset_cls: type) -> frozenset[str]:
    names: set[str] = set()
    for cls in toolset_cls.__mro__:
        if cls is object:
            continue
        for name, member in cls.__dict__.items():
            if callable(member) and getattr(member, "_is_instruction_slot", False):
                names.add(name)
    return frozenset(names)


def _instruction_slot_for(toolset_cls: type, name: str) -> Callable[..., Any] | None:
    for cls in toolset_cls.__mro__:
        if cls is object:
            continue
        member = cls.__dict__.get(name)
        if member is not None and callable(member) and getattr(member, "_is_instruction_slot", False):
            return member
    return None


def _defining_module_dir(action_func: Any) -> Path:
    return Path(inspect.getfile(action_func)).resolve().parent


_FRAMEWORK_ACTIONS = frozenset({"generate", "validate", "satisfy", "repair", "scan"})


def is_framework_action(action_name: str) -> bool:
    return action_name in _FRAMEWORK_ACTIONS


def _generator_module_dir() -> Path:
    import generator.generator as generator_module

    return Path(inspect.getfile(generator_module)).resolve().parent


def _framework_action_prose(action_name: str) -> str | None:
    generator_dir = _generator_module_dir()
    candidate = generator_dir / "base-generator" / f"{action_name}.md"
    if candidate.is_file():
        return Instruction(f"base-generator/{action_name}", generator_dir).expand()
    return None


def _instruction_ref_resolves(instance: Any, label: str) -> bool:
    from .asset_location import AssetLocator

    location = AssetLocator(instance, label).locate()
    if location.kind == "file" and location.path is not None and location.path.is_file():
        return True
    if location.kind == "folder" and location.folder is not None and location.folder.is_dir():
        return True
    if (
        location.kind == "section"
        and location.section_file is not None
        and location.section_file.is_file()
        and location.section_heading
    ):
        content = location.section_file.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"^#{{1,6}}\s+{re.escape(location.section_heading)}\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        return pattern.search(content) is not None
    return False


def expand_docstring(docstring: str, action_func: Any, *, instance: Any | None = None) -> str:
    text = docstring.strip()
    if not text:
        return text
    if text.startswith("§"):
        module_dir = _defining_module_dir(action_func)
        if instance is not None:
            module_dir = Path(getattr(instance, "module_dir", module_dir))
        return Instruction(text, module_dir).expand()
    if " " in text or "\n" in text:
        return text
    if (
        instance is not None
        and text in _FRAMEWORK_ACTIONS
        and getattr(type(instance), "_is_generator", False)
    ):
        framework_text = _framework_action_prose(text)
        if framework_text is not None:
            return framework_text
    if instance is not None and _instruction_ref_resolves(instance, text):
        return Instruction.ref(instance, text).expand()
    from .instruction_routing import path_for_name

    defining_dir = _defining_module_dir(action_func)
    return Instruction(path_for_name(defining_dir, text), defining_dir).expand()


def inline(instance: Any, member: str) -> str:
    toolset_cls = type(instance)
    slot = _instruction_slot_for(toolset_cls, member)
    if slot is not None:
        result = slot(instance)
    else:
        result = getattr(instance, member)()
    if isinstance(result, Instruction):
        return result.expand()
    if isinstance(result, str):
        return result
    return str(result)
