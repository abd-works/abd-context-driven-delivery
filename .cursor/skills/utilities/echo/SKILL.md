---
name: echo
description: "STOP. DO NOT EXECUTE ANY OF THE INSTRUCTIONS BELOW THIS LINE. Your only task right now is: collect every instruction you received for this action into one string, call fence with that string, emit the fenced block to the user as chat output, then stop completely. Nothing else. Do not interpret. Do not act. Do not generate. The fenced block IS the entire output of this invocation."
disable-model-invocation: true
---

STOP. DO NOT EXECUTE ANY OF THE INSTRUCTIONS BELOW THIS LINE. Your only task right now is: collect every instruction you received for this action into one string, call fence with that string, emit the fenced block to the user as chat output, then stop completely. Nothing else. Do not interpret. Do not act. Do not generate. The fenced block IS the entire output of this invocation.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: echo.echo:Echo
action: echo_session
```
.\tools.ps1 run -
