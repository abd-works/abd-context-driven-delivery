# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/mcp_server/mcp_server.py."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, context, description, it

from mcp_server import (
    McpInstructionCatalog,
    McpNameFormatter,
    McpServer,
    McpToolCatalog,
    ToolsetLoader,
)


def _demo_ref() -> str:
    return "mcp_server.examples.hosting_demo.hosting_demo:HostingDemo"


def _build_server() -> McpServer:
    formatter = McpNameFormatter()
    loader = ToolsetLoader(name_formatter=formatter)
    return McpServer(
        tool_catalog=McpToolCatalog(),
        instruction_catalog=McpInstructionCatalog(),
        loader=loader,
        name_formatter=formatter,
    )


with description("a toolset operation"):
    with context("that is annotated for direct AI invocation"):
        with before.each:
            self.server = _build_server()
            self.server.start((_demo_ref(),))

        with context("that has been registered for MCP discovery"):
            with it("should appear to the host under a dotted name combining the toolset and operation"):
                expect(self.server.list_tools()).to(contain("hosting_demo.increment"))

            with it("should advertise invocable parameters to the host"):
                params = self.server.invocable_parameters_for("hosting_demo.increment")
                expect("step" in params).to(equal(True))

            with it("should report the server as started"):
                expect(self.server.started).to(equal(True))

        with context("that has been invoked through MCP"):
            with it("should return the operation result to the host"):
                result = self.server.invoke_tool("hosting_demo.increment", {"step": 3})
                expect(result).to(equal(3))

    with context("that is annotated as agent guidance"):
        with before.each:
            self.server = _build_server()
            self.server.start((_demo_ref(),))

        with context("that has been registered for MCP discovery"):
            with it("should expose its guidance text to the host"):
                binding = self.server.instruction_for("hosting_demo.plan_work")
                expect(binding.prompt_text).to(contain("Think about the concept"))

            with it("should list each AI tool name that the guidance orchestrates"):
                binding = self.server.instruction_for("hosting_demo.plan_work")
                expect(binding.referenced_tool_names).to(equal(("increment",)))

            with it("should expose registered guidance names to the host"):
                expect(self.server.list_instructions()).to(contain("hosting_demo.plan_work"))

        with context("that has been invoked through MCP"):
            with it("should complete its orchestration and return a result to the host"):
                result = self.server.invoke_instruction(
                    "hosting_demo.plan_work", {"concept": "widgets"}
                )
                expect(result["concept"]).to(equal("widgets"))

            with context("with an explicit AI tool reference in its orchestration"):
                with it("should run that AI tool as part of the invocation"):
                    self.server.invoke_instruction(
                        "hosting_demo.plan_work", {"concept": "widgets"}
                    )
                    expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(2))

                with it("should allow that AI tool's result to shape the returned output"):
                    result = self.server.invoke_instruction(
                        "hosting_demo.plan_work", {"concept": "widgets"}
                    )
                    expect(result["count"]).to(equal(2))

            with context("with an ordinary code call in its orchestration"):
                with it("should run that call without treating it as an AI tool invocation"):
                    result = self.server.invoke_instruction("hosting_demo.orchestrate_with_plain", {})
                    expect(result["plain"]).to(equal("plain-result"))
                    expect(result["count"]).to(equal(1))

    with context("that is exposed through MCP"):
        with it("should use a dotted name with the toolset slug and operation name"):
            name = McpNameFormatter().format("hosting_demo", "increment")
            expect(name).to(equal("hosting_demo.increment"))

        with it("should not replace dots with underscores in its exposed name"):
            name = McpNameFormatter().format("bdd", "find_examples")
            expect(name).to(equal("bdd.find_examples"))
            expect(name == "bdd_find_examples").to(equal(False))


with description("a toolset"):
    with context("that is hosting operations through MCP"):
        with before.each:
            self.server = _build_server()
            self.server.start((_demo_ref(),))

        with context("that receives a second invocation on the same loaded instance"):
            with it("should preserve instance state from the first invocation"):
                self.server.invoke_tool("hosting_demo.increment", {"step": 4})
                expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(4))
                self.server.invoke_tool("hosting_demo.increment", {"step": 1})
                expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(5))
