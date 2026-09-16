"""Walk marked operations on a host class — deploy uses this, not instructions_registry."""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Iterator


@dataclass(frozen=True)
class OperationWrite:
    kind: str
    deploy_name: str | None
    operation: str
    doc: str
    invoke: str
    mcp: bool = False
    hook: bool = False
    member: Any = None


def _functions(host: Any) -> Iterator[tuple[str, Any]]:
    cls = host if isinstance(host, type) else type(host)
    seen: set[str] = set()
    for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name in seen:
            continue
        seen.add(name)
        yield name, member, cls
    for name, member in inspect.getmembers(cls, predicate=inspect.isdatadescriptor):
        fget = getattr(member, "fget", None)
        if fget is not None and name not in seen:
            seen.add(name)
            yield name, fget, cls


def operation_writes(host: Any) -> list[OperationWrite]:
    rows: list[OperationWrite] = []
    for name, member, cls in _functions(host):
        is_skill = getattr(member, "_skill", False)
        is_command = getattr(member, "_command", False)
        is_rules = getattr(member, "_rules", False)
        is_ai = getattr(member, "_is_agent_instructions", False)
        is_tool = getattr(member, "_is_agent_tool", False)
        is_mcp = getattr(member, "_mcp", False)
        is_hook = getattr(member, "_hook", False)
        if not (is_skill or is_command or is_rules or is_ai or is_tool or is_mcp or is_hook):
            continue
        kind = "rules" if is_rules else "command" if is_command else "skill" if is_skill else ""
        invoke = "tool" if is_tool else "action" if is_ai else "none"
        deploy_name = (
            getattr(member, "_command_name", None)
            or getattr(member, "_skill_name", None)
            or name
        )
        rows.append(
            OperationWrite(
                kind=kind,
                deploy_name=deploy_name,
                operation=name,
                doc=(inspect.getdoc(member) or "").strip(),
                invoke=invoke,
                mcp=bool(is_mcp),
                hook=bool(is_hook),
                member=member,
            )
        )
    return rows
