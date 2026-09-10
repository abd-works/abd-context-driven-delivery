# Step 0 — MCP stdio host discovery

Manual verification per `context_tools/clean_engineering/rules/testing-approach.md`. Real stdio subprocess — same path Cursor uses.

**Re-verified:** 2026-09-09

## Transport and library

| Choice | Decision |
|---|---|
| Transport | **stdio** — Cursor spawns one long-lived child process |
| Python SDK | **`mcp==1.30.0`** (official modelcontextprotocol/python-sdk) |
| Install note | On Windows ARM64, install with `pip install mcp==1.30.0 --no-deps` then runtime deps — `cryptography` has no wheel and needs MSVC |

## Entry point

```
.venv\Scripts\python.exe -m mcp_server --toolsets echo.echo:Echo
```

`MCP_TOOLSET_REFS` env var is an alternative to `--toolsets` (comma-separated).

## Built-in health check

| Step | Observed |
|---|---|
| `tools/list` with no toolsets | `["cdd.ping"]` |
| `tools/call` `cdd.ping` | `"pong"` |

## HostingDemo fixture

| Step | Observed |
|---|---|
| `tools/list` | `cdd.ping`, `hosting_demo.increment`, `hosting_demo.read_count` |
| `tools/call` increment `step=4` | `"4"` |
| `tools/call` read_count | `"4"` |
| second increment `step=1` then read_count | `"5"` — **state retained in one process** |

### Failure found and fixed

- `step` annotated as `int` under `from __future__ import annotations` was serialized as JSON Schema `string` — MCP validation rejected integer arguments. Fixed with `get_type_hints()` in `mcp_host._input_schema`.
- `list`, `dict`, `Sequence`, `Mapping`, and `X | None` still fell through to JSON Schema `string` after that int fix. `tools: list` advertised as a string, so the host sent `"list"` and Python walked characters. Fixed by mapping resolved hints to `array` / `object` / `boolean` / `anyOf` in `mcp_host._annotation_schema`. Locked in `mcp_host_spec.py` and ParameterTypes stdio tests.

## Real toolset: Echo

| Step | Observed |
|---|---|
| `tools/list` | `cdd.ping`, `echo.fence` |
| `tools/call` `echo.fence` `body=hello mcp` | fenced body with `hello mcp` verbatim |

## HostingDemo orchestration

| Step | Observed |
|---|---|
| `prompts/list` | `hosting_demo.plan_work`, `guidance_only`, `orchestrate_with_plain` |
| `tools/list` | includes `@instruction` names (dual-registered for host invocation) |
| `tools/call` `hosting_demo.plan_work` `concept=widgets` | `{"concept":"widgets","count":2}` — `tool(self.increment, step=2)` ran |
| `tools/call` `read_count` after plan_work | `"2"` |

## Bdd context tool

| Step | Observed |
|---|---|
| `tools/list` | `bdd.transform`, `bdd.render`, `bdd.load_template`, … |
| `tools/call` `bdd.transform` markdown→markdown | `{"format":"markdown","content":"# hi\n"}` |

## Signatures locked in `mcp_server_host_spec.py`

- built-in `cdd.ping` listed and returns `pong`
- HostingDemo tools and prompts listed over stdio
- state retained across multiple `tools/call` in one process
- `plan_work` orchestration via `tools/call`
- Echo `echo.fence` callable over stdio
- Bdd `transform` callable over stdio
- ParameterTypes schema over `tools/list` (`list` → array, `dict` → object, `bool` → boolean) and typed `tools/call` round-trips

## Cursor config

`.cursor/mcp.json` points at the venv Python, `python -m mcp_server`, and sets `PYTHONPATH` for `utilities` / `primitives` / `context_tools`.
