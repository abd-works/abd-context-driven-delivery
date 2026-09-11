---
name: model
description: "Set the preferred IDE/CLI model for this work session (slash ``/model``)."
disable-model-invocation: true
---

Set the preferred IDE/CLI model for this work session (slash ``/model``).

        Persist under ``.sessions/{session}/model``. When no session is open,
        use the root-repo ``sessions/default`` folder. CliAgent and SubAgent read this
        value when present. Never set disable-model-invocation.

Step 1 - Resolve the model id. If {model} is already given, use it. If not, call list_session_models, then AskQuestion constrained to that list (plus Other) so the user picks one.

Step 2 - Call set_session_model with the chosen model (and session/workspace when known).

Use MCP tool: `workspace.model(model: 'str' = '', session: 'str' = '', workspace: 'str' = '') -> 'str'`
