"""Step 1 discovery — talk to the stdio MCP host the way Cursor does."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _path in (_REPO_ROOT, _REPO_ROOT / "tools", _REPO_ROOT / "practices", _REPO_ROOT / "actions"):
    value = str(_path)
    if value not in sys.path:
        sys.path.insert(0, value)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_PYTHON = _REPO_ROOT / ".venv" / "Scripts" / "python.exe"
_HOSTING_DEMO = "harness.mcp.examples.hosting_demo.hosting_demo:HostingDemo"
_BDD = "practices.bdd.bdd:Bdd"


class HostDiscovery:
    """Probe a stdio MCP host the way Cursor does."""

    def _stdio_params(self, toolsets: str) -> StdioServerParameters:
        return StdioServerParameters(
            command=str(_PYTHON),
            args=["-m", "harness.mcp", "--toolsets", toolsets],
            cwd=str(_REPO_ROOT),
            env={
                **{key: value for key, value in __import__("os").environ.items()},
                "PYTHONPATH": ";".join(
                    [
                        str(_REPO_ROOT),
                        str(_REPO_ROOT / "tools"),
                        str(_REPO_ROOT / "practices"),
                        str(_REPO_ROOT / "actions"),
                    ]
                ),
            },
        )

    async def _print_catalog(self, session: ClientSession) -> None:
        tools = await session.list_tools()
        print("tools:", [tool.name for tool in tools.tools])
        prompts = await session.list_prompts()
        print("prompts:", [prompt.name for prompt in prompts.prompts])
        ping = await session.call_tool("cdd.ping", arguments={})
        print("ping:", ping.content)

    async def _exercise_hosting_demo(self, session: ClientSession) -> None:
        plan_work = await session.call_tool(
            "hosting-demo.plan_work",
            arguments={"concept": "widgets"},
        )
        print("plan_work:", plan_work.content)
        increment = await session.call_tool(
            "hosting-demo.increment",
            arguments={"step": 4},
        )
        print("increment:", increment.content)
        read_count = await session.call_tool("hosting-demo.read_count", arguments={})
        print("read_count:", read_count.content)
        increment_again = await session.call_tool(
            "hosting-demo.increment",
            arguments={"step": 1},
        )
        print("increment again:", increment_again.content)
        read_count_again = await session.call_tool(
            "hosting-demo.read_count",
            arguments={},
        )
        print("read_count again:", read_count_again.content)

    async def _exercise_bdd(self, session: ClientSession) -> None:
        transform = await session.call_tool(
            "bdd.transform",
            arguments={
                "source_format": "markdown",
                "target_format": "markdown",
                "content": "# hi",
            },
        )
        print("bdd.transform:", transform.content)

    async def probe(self, toolsets: str) -> None:
        params = self._stdio_params(toolsets)
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                await self._print_catalog(session)
                if _HOSTING_DEMO in toolsets:
                    await self._exercise_hosting_demo(session)
                if _BDD in toolsets:
                    await self._exercise_bdd(session)


def main() -> None:
    discovery = HostDiscovery()
    print("=== builtin only ===")
    asyncio.run(discovery.probe(""))
    print("=== hosting demo ===")
    asyncio.run(discovery.probe(_HOSTING_DEMO))
    print("=== bdd ===")
    asyncio.run(discovery.probe(_BDD))


if __name__ == "__main__":
    main()
