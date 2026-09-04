worksession-chat — list chat transcript paths attached to a work session.

Reads the append-only annotated tag ``chat/session/{name}``. Omit ``name`` to
use the current work session (or this session). Pass the kebab session name or
``session/...`` branch when looking up a closed session from another chat.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: workspace.workspace:WorkSession
tool: worksession_chat
```
.\tools.ps1 run -
