"""MCP runtime — enroll from McpDeployment.bind, not a second annotation scan."""
from __future__ import annotations

from typing import Any


class McpTool:
    def __init__(self, op: Any) -> None:
        self.mcp_name = op.mcp_name
        self._op = op

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        member = getattr(self._op.host, self._op.operation)
        if callable(member):
            return member(**dict(arguments or {}))
        return member


class McpPrompt:
    def __init__(self, op: Any) -> None:
        self.mcp_name = op.mcp_name
        self._op = op

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        import inspect

        host = self._op.host
        name = self._op.operation
        if name == "guidance" and hasattr(host, "instructions"):
            return host.instructions
        member = getattr(host, name, None)
        if callable(member):
            try:
                result = member(**dict(arguments or {}))
            except TypeError:
                result = None
            if result is not None:
                return result
            return (inspect.getdoc(member) or "").strip() or getattr(host, "instructions", "")
        if hasattr(host, "instructions"):
            return host.instructions
        return member


class McpServer:
    def __init__(self) -> None:
        self.mcp_deployments: list[Any] = []
        self.tools: dict[str, McpTool] = {}
        self.prompts: dict[str, McpPrompt] = {}

    def enroll(self, op: Any) -> None:
        if op.kind == "tool":
            self.tools[op.mcp_name] = McpTool(op)
        else:
            self.prompts[op.mcp_name] = McpPrompt(op)

    def start(self, toolset_refs: tuple[str, ...] = ()) -> None:
        from primitives.harness.deployment import McpDeployment
        from primitives.harness.registry import Registry

        self.mcp_deployments = []
        for ref in toolset_refs:
            deployment = McpDeployment("Cursor", ".", ref)
            for host in Registry.load():
                from primitives.harness.operation_writes import operation_writes

                for row in operation_writes(host):
                    if row.mcp:
                        if row.invoke == "tool":
                            deployment.deployAgentTool(host, row)
                        else:
                            deployment.deployAgentInstructions(host, row)
            deployment.bind(self)
            self.mcp_deployments.append(deployment)

    def bind_from(self, deployment: Any) -> None:
        deployment.bind(self)
        if deployment not in self.mcp_deployments:
            self.mcp_deployments.append(deployment)

    def invoke_tool(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self.tools[mcp_name].invoke(arguments)

    def invoke_prompt(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self.prompts[mcp_name].invoke(arguments)
