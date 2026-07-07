---
rule: config-in-cdd-config
kind: shape
fidelity: [engineering]
artifact: .cdd-config.json
scanner: config-in-cdd-config-scanner.py
---

# Rule: Config in CDD Config

All capability state and configuration must live as keys inside `.cdd-config.json`. No separate state files (`.cdd-deploy.json`, `config.json`, `settings.json`, etc.) may exist alongside it.

## DO

- Store deploy record under the `deploy` key in `.cdd-config.json`
- Store any other capability state as a named key in `.cdd-config.json`

## DON'T

- Create `.cdd-deploy.json` or any other file to store state that belongs in `.cdd-config.json`
- Leave `.cdd-config.json` empty while state files exist alongside it
