---
fidelity: [behavior]
artifact: [bdd]
format: py
---

**Sources / context:** `utilities/mcp-server/.context/mcp-server-spec.md`; `utilities/mcp-server/.context/clean-engineering-model.md`

Behavior fidelity lives in `utilities/mcp-server/mcp_server_spec.py` (Python/Mamba channel).

Increment 1: toolset operations annotated as AI tools or instructions, registered and invoked by MCP; dotted naming; direct callable invocation; no YAML/CLI path.

Hierarchy anchors on **toolset operation** → annotation → MCP registration/invocation — not server startup plumbing.
