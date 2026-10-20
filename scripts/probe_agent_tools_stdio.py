"""Timed stdio exercise of agent-tools-diagnostics (dev / CI)."""
from __future__ import annotations

import asyncio
import os
import sys
import time
from datetime import timedelta
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def _run(toolsets: str, call_timeout: float) -> tuple[float, str]:
    py = _REPO / ".venv" / "Scripts" / "python.exe"
    diag = _REPO.parent / "cdd-diagnostic"
    server_env = {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "PYTHONPYCACHEPREFIX": str(_REPO / ".pycache"),
        "CDD_REPO": str(_REPO),
        "CDD_PROJECT": str(_REPO),
        "CDD_PROBE_QUIET": "0",
    }
    if diag.is_dir():
        server_env["CDD_DIAGNOSTIC_REPO"] = str(diag)
        server_env["PYTHONPATH"] = os.pathsep.join(
            [str(diag / "src"), server_env.get("PYTHONPATH", "")]
        ).strip(os.pathsep)
    params = StdioServerParameters(
        command=str(py),
        args=["-u", "-m", "harness.mcp", "--toolsets", toolsets],
        cwd=str(_REPO),
        env=server_env,
    )
    async with stdio_client(params, errlog=sys.stderr) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=timedelta(seconds=int(call_timeout) + 30),
        ) as session:
            t_init = time.perf_counter()
            await session.initialize()
            print(f"initialized in {time.perf_counter() - t_init:.1f}s", flush=True)
            print(
                "calling agent-tools-diagnostics — [agent-tools] lines below are live server stderr",
                flush=True,
            )
            started = time.perf_counter()
            call = asyncio.create_task(
                session.call_tool(
                    "agent-tools-diagnostics.agent_tools_diagnostics",
                    arguments={},
                )
            )
            while not call.done():
                await asyncio.sleep(2.0)
                if not call.done():
                    print(
                        f"  … still running ({time.perf_counter() - started:.0f}s)",
                        flush=True,
                    )
            result = await call
            elapsed = time.perf_counter() - started
            return elapsed, result.content[0].text


def main() -> int:
    from harness.installation.installer import Installer

    Installer(repo=_REPO).ensure_import_path()
    refs = ",".join(Installer(repo=_REPO).collect_toolsets())
    budget = float(os.environ.get("CDD_PROBE_BUDGET_SECONDS", "45"))
    print(
        f"toolsets={len(refs.split(','))} budget={budget}s "
        "(live trace: [agent-tools] phase tool: detail — do not set CDD_PROBE_QUIET=1)",
        flush=True,
    )
    try:
        elapsed, text = asyncio.run(_run(refs, budget))
    except Exception as error:
        print(f"FAIL {type(error).__name__}: {error}", flush=True)
        return 1
    print(f"elapsed={elapsed:.2f}s", flush=True)
    print(text[:2500], flush=True)
    return 0 if elapsed <= budget else 1


if __name__ == "__main__":
    raise SystemExit(main())
