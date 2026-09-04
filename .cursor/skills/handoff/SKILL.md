---
name: handoff
description: "Compact the current session into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided."
disable-model-invocation: true
---

Compact the current session into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: handoff.handoff:Handoff
action: handoff_session
```
.\tools.ps1 run -
