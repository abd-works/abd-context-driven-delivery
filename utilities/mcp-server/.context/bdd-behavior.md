---
fidelity: [behavior]
artifact: [bdd]
format: py
---

**Sources / context:** `utilities/mcp-server/.context/mcp-server-spec.md`; `utilities/mcp-server/.context/clean-engineering-model.md`

Behavior fidelity lives in `utilities/mcp-server/mcp_server_spec.py` (Python/Mamba).

## Sketch (usage order)

```
a toolset operation
  that is annotated for direct AI invocation
    that has been registered for MCP discovery
      it should appear to the host under a dotted name combining the toolset and operation
      it should advertise invocable parameters to the host
    that has been invoked through MCP
      it should return the operation result to the host

  that is annotated as agent guidance
    that has been registered for MCP discovery
      it should expose its guidance text to the host
      it should list each AI tool name that the guidance orchestrates
    that has been invoked through MCP
      it should complete its orchestration and return a result to the host
      with an explicit AI tool reference in its orchestration
        it should run that AI tool as part of the invocation
        it should allow that AI tool's result to shape the returned output
      with an ordinary code call in its orchestration
        it should run that call without treating it as an AI tool invocation

  that is exposed through MCP
    it should use a dotted name with the toolset slug and operation name
    it should not replace dots with underscores in its exposed name

a toolset
  that is hosting operations through MCP
    that receives a second invocation on the same loaded instance
      it should preserve instance state from the first invocation

a toolset operation
  that is exposed through MCP
    it should use a dotted name with the toolset slug and operation name
    it should not replace dots with underscores in its exposed name
```

Hierarchy anchors on **toolset operation** → annotation kind → MCP discovery/invocation. No server-startup or implementation-type subjects.
