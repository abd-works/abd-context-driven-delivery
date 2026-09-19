Set the preferred IDE/CLI model for this work session (slash ``/model``).

Persist under ``.sessions/{session}/model``. When no session is open,
use the root-repo ``sessions/default`` folder. CliAgent and SubAgent read this
value when present. Never set disable-model-invocation.

Use MCP tool: `workspace.model(model: 'str' = '', session: 'str' = '', workspace: 'str' = '')`
