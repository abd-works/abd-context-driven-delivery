"""MCP runtime — one repo implementation; enroll from deploy-recorded ops."""
from __future__ import annotations

import inspect
from typing import Any

from primitives.harness.deployment import McpDeployment, McpOp
from primitives.harness.operation_writes import operation_writes
from primitives.harness.toolset_loader import ToolsetLoader


class McpTool:
    """One MCP tool enrolled from a deploy-recorded ``McpOp``."""

    def __init__(self, op: McpOp) -> None:
        self.mcp_name = op.mcp_name
        self._op = op
        self.callable = getattr(op.host, op.operation)
        function = getattr(self.callable, "__func__", self.callable)
        self.description = (inspect.getdoc(function) or "").strip()

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        if callable(self.callable):
            return self.callable(**dict(arguments or {}))
        return self.callable


class McpPrompt:
    """One MCP prompt enrolled from a deploy-recorded ``McpOp``."""

    def __init__(self, op: McpOp) -> None:
        self.mcp_name = op.mcp_name
        self._op = op
        self.callable = getattr(op.host, op.operation)
        function = getattr(self.callable, "__func__", self.callable)
        self.prompt_text = (inspect.getdoc(function) or "").strip()

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        host = self._op.host
        name = self._op.operation
        if name == "guidance" and hasattr(host, "instructions"):
            return host.instructions
        member = self.callable
        if callable(member):
            try:
                result = member(**dict(arguments or {}))
            except TypeError:
                result = None
            if result is not None:
                return result
            return self.prompt_text or getattr(host, "instructions", "")
        if hasattr(host, "instructions"):
            return host.instructions
        return member


class McpServer:
    """Load toolset refs and enroll only ``@mcp`` ops from the deploy walk."""

    def __init__(self, *, toolset_loader: ToolsetLoader | None = None) -> None:
        self._toolset_loader = toolset_loader or ToolsetLoader.instance()
        self.mcp_deployments: list[McpDeployment] = []
        self._tools: dict[str, McpTool] = {}
        self._prompts: dict[str, McpPrompt] = {}
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    @property
    def tools(self) -> dict[str, McpTool]:
        return self._tools

    @property
    def prompts(self) -> dict[str, McpPrompt]:
        return self._prompts

    def enroll(self, op: McpOp) -> None:
        if op.kind == "tool":
            self._tools[op.mcp_name] = McpTool(op)
        else:
            self._prompts[op.mcp_name] = McpPrompt(op)

    def bind_from(self, deployment: McpDeployment) -> None:
        """Enroll ops recorded during ``Harness.write_deploy`` — no class rescan."""
        deployment.bind(self)
        if deployment not in self.mcp_deployments:
            self.mcp_deployments.append(deployment)

    def start(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, object] | None = None,
    ) -> None:
        """Load each toolset ref and enroll its ``@mcp`` ops via the same walk deploy uses."""
        context = dict(constructor_context or {})
        self.mcp_deployments = []
        self._tools.clear()
        self._prompts.clear()
        for ref in toolset_refs:
            host = self._toolset_loader.load(ref)(**context)
            deployment = McpDeployment("Cursor", ".", ref)
            for row in operation_writes(host):
                deployment.record_operation(host, row)
            deployment.bind(self)
            self.mcp_deployments.append(deployment)
        self._started = True

    def invoke_tool(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._tools[mcp_name].invoke(arguments)

    def invoke_prompt(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._prompts[mcp_name].invoke(arguments)


__all__ = ["McpPrompt", "McpServer", "McpTool"]
