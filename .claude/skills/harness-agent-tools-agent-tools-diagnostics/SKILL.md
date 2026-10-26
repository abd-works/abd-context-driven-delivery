---
name: harness-agent-tools-agent-tools-diagnostics
description: >-
  Probe space, harness, and tools MCP tools through the live host; append results under ``agent_tools`` in ``diagnostics.json``.
  
  guidance: optional slugs when a harness tool needs ``guidance`` probe arguments. Practices, patterns, builders, and ``harness.guidance`` / ``harness.guidance_actions`` base toolsets are out of scope — use ``/guidance-diagnostics`` for those.
  
  All probes use the live CDD MCP host already loaded in Cursor. Diagnostics do not run git clean/switch on the repo (avoids lock hangs). Light invoke uses ``_cdd-diagnostic-probe`` args where needed; only ``repo.push_commit`` and ``repo.close_*`` are skipped. Heavy session/graph uses ``cdd-diagnostic``. Progress on stderr: ``[agent-tools] phase tool: detail``. Slash or MCP ``agent-tools-diagnostics.agent_tools_diagnostics``. Read ``.cursor/diagnostics.json`` → ``agent_tools``.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Probe space, harness, and tools MCP tools through the live host; append results under ``agent_tools`` in ``diagnostics.json``.

guidance: optional slugs when a harness tool needs ``guidance`` probe arguments. Practices, patterns, builders, and ``harness.guidance`` / ``harness.guidance_actions`` base toolsets are out of scope — use ``/guidance-diagnostics`` for those.

All probes use the live CDD MCP host already loaded in Cursor. Diagnostics do not run git clean/switch on the repo (avoids lock hangs). Light invoke uses ``_cdd-diagnostic-probe`` args where needed; only ``repo.push_commit`` and ``repo.close_*`` are skipped. Heavy session/graph uses ``cdd-diagnostic``. Progress on stderr: ``[agent-tools] phase tool: detail``. Slash or MCP ``agent-tools-diagnostics.agent_tools_diagnostics``. Read ``.cursor/diagnostics.json`` → ``agent_tools``.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `agent-tools-diagnostics.agent_tools_diagnostics(guidance: 'list[str] | None' = None)`
