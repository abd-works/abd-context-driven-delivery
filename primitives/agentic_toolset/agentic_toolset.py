"""One type. Two author wrappers: @agent_tool and @agent_instructions."""
from __future__ import annotations

import inspect
from typing import Any, Callable, Mapping


def agent_instructions(func: Callable[..., Any]) -> Callable[..., Any]:
    func._is_agent_instructions = True  # type: ignore[attr-defined]
    return func


def agent_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    func._is_agent_tool = True  # type: ignore[attr-defined]
    return func


def agentic_toolset(cls: type) -> type:
    cls._is_agentic_toolset = True  # type: ignore[attr-defined]
    return cls


def _unbound(member: Any) -> Any:
    return getattr(member, "__func__", member)


class AgenticToolset:
    @property
    def toolset_name(self) -> str:
        explicit = getattr(type(self), "domain_slug", None)
        if explicit:
            return str(explicit)
        name = type(self).__name__
        stepped = []
        for i, ch in enumerate(name):
            if ch.isupper() and i and (name[i - 1].islower() or (i + 1 < len(name) and name[i + 1].islower())):
                stepped.append("-")
            stepped.append(ch.lower())
        return "".join(stepped).replace("_", "-")

    @property
    def tools(self) -> dict[str, Callable[..., Any]]:
        found: dict[str, Callable[..., Any]] = {}
        for name, member in inspect.getmembers(type(self), predicate=inspect.isfunction):
            if getattr(member, "_is_agent_tool", False):
                found[name] = member
        return found

    @property
    def instructions_registry(self) -> Mapping[str, Callable[..., Any]]:
        found: dict[str, Callable[..., Any]] = {}
        for name, member in inspect.getmembers(type(self), predicate=inspect.isfunction):
            if getattr(member, "_is_agent_instructions", False):
                found[name] = member
        return found

    @property
    def instructions(self) -> str:
        parts: list[str] = []
        own = (type(self).__doc__ or "").strip()
        if own:
            parts.append(own)
        for name, member in self.instructions_registry.items():
            text = (inspect.getdoc(member) or "").strip()
            if text:
                parts.append(text)
        return "\n\n".join(parts)

    def guidance(self) -> str:
        return self.instructions

    def tools_call(self, *calls: Callable[..., Any]) -> list[Any]:
        return [call() if callable(call) else call for call in calls]

    def instructions_call(self, *calls: Callable[..., Any]) -> str:
        parts = []
        for call in calls:
            if callable(call):
                doc = inspect.getdoc(call) or ""
                parts.append(doc.strip())
        return "\n\n".join(p for p in parts if p)
