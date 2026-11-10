"""Time each workspace MCP ping/invoke on a full in-process host."""
from __future__ import annotations

import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    from harness.agent_tools.agent_tools_probe import (
        _invoke_skip_reason,
        _probe_mcp_invoke_host,
        _probe_mcp_ping_host,
        published_agent_tools_mcp,
    )
    from harness.guidance.guidance import ActionProbeSession
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import McpHost

    installer = Installer(repo=_REPO)
    installer.ensure_import_path()
    refs = tuple(installer.collect_toolsets())
    print(f"standing host ({len(refs)} toolsets)", flush=True)
    started = time.perf_counter()
    host = McpHost.from_refs(refs, repo=str(_REPO), project=str(_REPO))
    print(f"host ready {time.perf_counter() - started:.1f}s", flush=True)
    host._bind_as_serving()
    names = published_agent_tools_mcp(installer)
    print(f"published {len(names)}", flush=True)
    session = ActionProbeSession(installer)
    try:
        for name in names:
            t1 = time.perf_counter()
            _probe_mcp_ping_host(host, name)
            dt = time.perf_counter() - t1
            slow = " SLOW" if dt > 2 else ""
            print(f"ping {name}: {dt:.2f}s{slow}", flush=True)
        for name in names:
            skip = _invoke_skip_reason(name)
            if skip:
                print(f"invoke skip {name}: {skip}", flush=True)
                continue
            t1 = time.perf_counter()
            item = _probe_mcp_invoke_host(host, name, [], session, installer)
            dt = time.perf_counter() - t1
            extra = item.get("failure") or item.get("skipped") or ""
            print(f"invoke {name}: {dt:.2f}s {item.get('color')} {extra}"[:140], flush=True)
    finally:
        session.cleanup()
        host._unbind_as_serving()
    print("done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
