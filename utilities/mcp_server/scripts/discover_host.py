"""Step 1 discovery — talk to the stdio MCP host the way Cursor does."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _path in (_REPO_ROOT, _REPO_ROOT / "utilities", _REPO_ROOT / "primitives", _REPO_ROOT / "context_tools"):
    value = str(_path)
    if value not in sys.path:
        sys.path.insert(0, value)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_PYTHON = _REPO_ROOT / ".venv" / "Scripts" / "python.exe"
_HOSTING_DEMO = "mcp_server.examples.hosting_demo.hosting_demo:HostingDemo"
_BDD = "context_tools.bdd.bdd:Bdd"


async def _probe(toolsets: str) -> None:
    params = StdioServerParameters(
        command=str(_PYTHON),
        args=[
            "-m",
            "mcp_server",
            "--toolsets",
            toolsets,
        ],
        cwd=str(_REPO_ROOT),
        env={
            **{key: value for key, value in __import__("os").environ.items()},
            "PYTHONPATH": ";".join(
                [
                    str(_REPO_ROOT),
                    str(_REPO_ROOT / "utilities"),
                    str(_REPO_ROOT / "primitives"),
                    str(_REPO_ROOT / "context_tools"),
                ]
            ),
        },
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [tool.name for tool in tools.tools])
            prompts = await session.list_prompts()
            print("prompts:", [prompt.name for prompt in prompts.prompts])
            ping = await session.call_tool("cdd.ping", arguments={})
            print("ping:", ping.content)
            if _HOSTING_DEMO in toolsets:
                plan_work = await session.call_tool(
                    "hosting_demo.plan_work",
                    arguments={"concept": "widgets"},
                )
                print("plan_work:", plan_work.content)
            if _BDD in toolsets:
                transform = await session.call_tool(
                    "bdd.transform",
                    arguments={
                        "source_format": "markdown",
                        "target_format": "markdown",
                        "content": "# hi",
                    },
                )
                print("bdd.transform:", transform.content)
            if toolsets and _HOSTING_DEMO in toolsets:
                increment = await session.call_tool(
                    "hosting_demo.increment",
                    arguments={"step": 4},
                )
                print("increment:", increment.content)
                read_count = await session.call_tool(
                    "hosting_demo.read_count",
                    arguments={},
                )
                print("read_count:", read_count.content)
                increment_again = await session.call_tool(
                    "hosting_demo.increment",
                    arguments={"step": 1},
                )
                print("increment again:", increment_again.content)
                read_count_again = await session.call_tool(
                    "hosting_demo.read_count",
                    arguments={},
                )
                print("read_count again:", read_count_again.content)


def main() -> None:
    print("=== builtin only ===")
    asyncio.run(_probe(""))
    print("=== hosting demo ===")
    asyncio.run(_probe(_HOSTING_DEMO))
    print("=== bdd ===")
    asyncio.run(_probe(_BDD))


if __name__ == "__main__":
    main()
