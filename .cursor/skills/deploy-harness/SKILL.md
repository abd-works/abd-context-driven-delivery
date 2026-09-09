---
name: deploy-harness
description: "With no IDE given, AskQuestion: Which IDE? Cursor | VS Code | Kilo. With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring. With no deploy path given, call suggested_deploy_path, then AskQuestion: deploy to that suggested path (recommended) / enter another path. With no code_language given, AskQuestion: Python (recommended) | TypeScript. Set context.type to the chosen IDE. Pass the chosen language as arguments.code_language to write_deploy."
disable-model-invocation: true
---

With no IDE given, AskQuestion: Which IDE? Cursor | VS Code | Kilo. With no name filter given, AskQuestion: all toolsets (recommended) / enter a substring. With no deploy path given, call suggested_deploy_path, then AskQuestion: deploy to that suggested path (recommended) / enter another path. With no code_language given, AskQuestion: Python (recommended) | TypeScript. Set context.type to the chosen IDE. Pass the chosen language as arguments.code_language to write_deploy.

Required context params with no value: type. AskQuestion to collect each missing value before running.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: harness.harness:Harness
context:
  type: 
tool: write_deploy
```
.\tools.ps1 run -
