"""Deployment walk on Deployment; leaf writes on Markdown / MCP / Hook subtypes."""
from __future__ import annotations

import inspect
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from primitives.harness.operation_writes import OperationWrite, operation_writes


def _slugify(name: str) -> str:
    stepped = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    stepped = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", stepped)
    stepped = re.sub(r"[_.:/\\\s]+", "-", stepped)
    return re.sub(r"-+", "-", stepped).strip("-").lower()


def host_slug(host: Any) -> str:
    raw = (
        getattr(host, "domain_slug", None)
        or getattr(host, "toolset_name", None)
        or getattr(type(host), "domain_slug", None)
    )
    if raw:
        return str(raw).replace("_", "-")
    return _slugify(type(host).__name__)


def toolset_ref_for_type(cls: type) -> str:
    """Stable ``module:Class`` ref for MCP registration and run requests."""
    return f"{cls.__module__}:{cls.__name__}"


def toolset_ref(host: Any) -> str:
    """``module:Class`` ref for mcp.json ``--toolsets`` — not a display slug."""
    return toolset_ref_for_type(type(host))


def member_is_mcp(member: Any) -> bool:
    return bool(getattr(member, "_mcp", False))


def render_mcp_invoke(toolset_ref: str, member: Any) -> str:
    name = getattr(member, "__name__", str(member))
    slug = toolset_ref.split(":")[-1]
    if "." in toolset_ref and ":" not in toolset_ref:
        slug = toolset_ref
    else:
        slug = slug.replace("_", "-")
    try:
        signature = inspect.signature(member)
        params = inspect.Signature(
            [
                p
                for n, p in signature.parameters.items()
                if n != "self"
            ]
        )
        suffix = str(params)
    except (TypeError, ValueError):
        suffix = "()"
    return f"Use MCP tool: `{slug}.{name}{suffix}`"


def _cli_fence(toolset_ref: str, operation: str, invoke: str) -> str:
    kind = "tool" if invoke == "tool" else "action"
    return (
        "```\n"
        f"toolset: {toolset_ref}\n"
        f"{kind}: {operation}\n"
        "```\n"
        ".\\tools.ps1 run -\n"
    )


@dataclass
class McpOp:
    mcp_name: str
    kind: str
    host: Any
    operation: str
    member: Any


class MarkdownDeployment:
    def __init__(self, ide: str, path: Path | str) -> None:
        self.ide = ide
        self.path = Path(path)

    def mark(self, member: Any) -> Any:
        return member

    def relative_path(self, mark: str, guidance: Any, member: Any) -> Path:
        name = (
            getattr(member, "_command_name", None)
            or getattr(member, "_skill_name", None)
            or getattr(member, "__name__", "member")
        )
        slug = host_slug(guidance)
        from primitives.agent_tools.agent_tools import AgentToolSet
        from primitives.guidance.guidance import FidelityGuidance

        fidelity_name = getattr(guidance, "name", None)
        is_fidelity = isinstance(guidance, FidelityGuidance)
        if mark == "skill":
            folder = name if isinstance(guidance, AgentToolSet) else slug
            return Path("skills") / str(folder) / "SKILL.md"
        if mark == "command":
            if self.ide == "VS Code":
                base = Path("prompts")
            else:
                base = Path("commands")
            if is_fidelity and fidelity_name:
                return base / f"{slug}-{fidelity_name}.md"
            return base / f"{name}.md"
        if mark == "rules":
            return Path("rules") / f"{name}.mdc"
        return Path(str(name))

    def render(self, mark: str, section: str, member: Any, host: Any | None = None) -> str:
        if member_is_mcp(member):
            context = ""
            if host is not None:
                context = getattr(host, "context", "") or ""
                if callable(context):
                    context = ""
            slug = host_slug(host) if host is not None else "toolset"
            tail = render_mcp_invoke(slug, member)
            parts = [str(context).strip(), tail]
            return "\n\n".join(p for p in parts if p) + "\n"
        invoke = "tool" if getattr(member, "_is_agent_tool", False) else "action"
        ref = host_slug(host) if host is not None else "toolset"
        op = getattr(member, "__name__", "operation")
        return f"{section.rstrip()}\n\n{_cli_fence(ref, op, invoke)}"

    def deployGuidance(self, guidance: Any) -> None:
        return None

    def deployFidelityGuidance(self, fidelity: Any) -> None:
        return None

    def deployAgentInstructions(self, host: Any, operation: OperationWrite) -> None:
        if not operation.kind:
            return
        member = operation.member
        body_source = _instruction_body(host, operation)
        text = self.render(operation.kind, body_source, member, host)
        rel = self.relative_path(operation.kind, host, member)
        dest = self.path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")

    def deployAgentTool(self, host: Any, operation: OperationWrite) -> None:
        if operation.kind not in {"skill", "command"}:
            return
        self.deployAgentInstructions(host, operation)

    def write_rules(self, host: Any) -> None:
        rules = getattr(host, "rules", None)
        member = _rules_member(type(host))
        if rules is None or member is None:
            return
        if not getattr(member, "_rules", False):
            return
        entries = getattr(rules, "entries", None) or {}
        for slug, rule in entries.items():
            if hasattr(rule, "entries"):
                continue
            body = getattr(rule, "body", str(rule))
            text = self.render("rules", body, member, host)
            dest = self.path / "rules" / f"{slug}.mdc"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")


def _rules_member(cls: type) -> Any:
    prop = getattr(cls, "rules", None)
    return getattr(prop, "fget", prop)


def _instruction_body(host: Any, operation: OperationWrite) -> str:
    name = operation.operation
    if name == "guidance" and hasattr(host, "instructions"):
        return str(host.instructions)
    member = getattr(host, name, None)
    if callable(member) and not getattr(operation.member, "_is_agent_instructions", False):
        try:
            return str(member())
        except TypeError:
            pass
    if operation.doc:
        return operation.doc
    if hasattr(host, "instructions"):
        return str(host.instructions)
    return ""


class McpDeployment:
    def __init__(self, ide: str, path: Path | str, toolset_ref: str = "") -> None:
        self.ide = ide
        self.path = Path(path)
        self.toolset_ref = toolset_ref
        self.mcp_operations: list[McpOp] = []
        self._bound = False

    def deployGuidance(self, guidance: Any) -> None:
        return None

    def deployFidelityGuidance(self, fidelity: Any) -> None:
        return None

    def record_operation(self, host: Any, operation: OperationWrite) -> None:
        """Record one ``@mcp`` op from the deploy walk — does not write ``mcp.json``."""
        if not operation.mcp:
            return
        slug = host_slug(host)
        kind = "tool" if operation.invoke == "tool" else "prompt"
        self.mcp_operations.append(
            McpOp(
                mcp_name=f"{slug}.{operation.operation}",
                kind=kind,
                host=host,
                operation=operation.operation,
                member=operation.member,
            )
        )

    def deployAgentInstructions(self, host: Any, operation: OperationWrite) -> None:
        self.record_operation(host, operation)
        if operation.mcp:
            self._write_manifest()

    def deployAgentTool(self, host: Any, operation: OperationWrite) -> None:
        self.record_operation(host, operation)
        if operation.mcp:
            self._write_manifest()

    def _write_manifest(self) -> None:
        refs = sorted({toolset_ref(op.host) for op in self.mcp_operations})
        payload = {
            "mcpServers": {
                "cdd": {
                    "command": "python",
                    "args": [
                        "-m",
                        "mcp_server",
                        "--toolsets",
                        ",".join(refs),
                    ],
                }
            }
        }
        dest = self.path / "mcp.json"
        dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def bind(self, server: Any) -> None:
        self._bound = True
        for op in self.mcp_operations:
            server.enroll(op)


class HookDeployment:
    def __init__(self, ide: str, path: Path | str) -> None:
        self.ide = ide
        self.path = Path(path)
        self._events: list[dict[str, str]] = []

    def deployGuidance(self, guidance: Any) -> None:
        return None

    def deployFidelityGuidance(self, fidelity: Any) -> None:
        return None

    def deployAgentInstructions(self, toolset: Any, operation: OperationWrite) -> None:
        from primitives.agent_tools.agent_tools import AgentToolSet

        if not isinstance(toolset, AgentToolSet):
            return
        if not operation.hook:
            return
        event = getattr(operation.member, "_hook_name", None) or "stop"
        dest = self.path / "skills" / f"hook-{operation.operation}" / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(operation.doc or operation.operation, encoding="utf-8")
        self._events.append({"event": str(event), "command": operation.operation})
        self._write()

    def _write(self) -> None:
        if not self._events:
            return
        dest = self.path / "hooks.json"
        dest.write_text(json.dumps({"hooks": self._events}, indent=2) + "\n", encoding="utf-8")


class Deployment:
    def __init__(self, ide: str, path: Path | str) -> None:
        self.ide = ide
        self.path = Path(path)
        self.markdown = MarkdownDeployment(ide, self.path)
        self.mcp = McpDeployment(ide, self.path)
        self.hooks = HookDeployment(ide, self.path)

    def deploy(self, host: Any) -> None:
        from primitives.guidance.guidance import Guidance, PracticeGuidance
        from primitives.agent_tools.agent_tools import AgentToolSet

        if isinstance(host, PracticeGuidance):
            self.deployPracticeGuidance(host)
        elif isinstance(host, AgentToolSet):
            self.deployAgentToolSet(host)
        elif isinstance(host, Guidance):
            self.deployGuidance(host)

    def deployPracticeGuidance(self, practice_guidance: Any) -> None:
        self.deployGuidance(practice_guidance)
        fidelities = getattr(practice_guidance, "fidelities", None)
        entries = getattr(fidelities, "entries", {}) if fidelities is not None else {}
        for fidelity in entries.values():
            self.deployFidelityGuidance(fidelity)

    def deployGuidance(self, guidance: Any) -> None:
        for row in operation_writes(guidance):
            if row.invoke == "action" or row.operation == "guidance":
                self.deployAgentInstructions(guidance, row)
        self.markdown.write_rules(guidance)

    def deployFidelityGuidance(self, fidelity: Any) -> None:
        for row in operation_writes(fidelity):
            if row.invoke == "action" or row.operation == "guidance":
                self.deployAgentInstructions(fidelity, row)
        self.markdown.write_rules(fidelity)

    def deployAgentToolSet(self, host: Any) -> None:
        for row in operation_writes(host):
            if row.invoke == "action":
                self.deployAgentInstructions(host, row)
            elif row.invoke == "tool":
                self.deployAgentTool(host, row)

    def deployAgentInstructions(self, host: Any, operation: OperationWrite) -> None:
        self.markdown.deployAgentInstructions(host, operation)
        self.mcp.deployAgentInstructions(host, operation)
        self.hooks.deployAgentInstructions(host, operation)

    def deployAgentTool(self, host: Any, operation: OperationWrite) -> None:
        self.markdown.deployAgentTool(host, operation)
        self.mcp.deployAgentTool(host, operation)
