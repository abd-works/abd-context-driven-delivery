Keep every aspect of a capability — agentic surface, API surface, tests, rules, config — together in one folder. Organise around concepts, not layers.

All concerns of a capability belong in the capability folder itself. Do not split a capability across layers or generic shared folders.

| Concern | Lives in |
|---|---|
| Agentic surface | `{capability}/{capability}.md` |
| API surface | `{capability}/{capability}.py` |
| Rules | `{capability}/rules/{rule-name}/` |
| Tests | `{capability}/test_*.py` |
| Config | `{capability}/.cdd-config.json` |

**DO** — co-locate everything that belongs to a concept:

```
enforce/
  enforce.md
  enforce.py
  rules/
    vehicle-has-means/
      vehicle-has-means-rule.md
      vehicle-has-means-scanner.py
      examples/pass/
      examples/fail/
  validate-artifact-rules-test.py
```

**DON'T** — split by technical layer across the repo:

```
rules/vehicle-has-means.md       ← wrong: rules folder at repo root
scanners/vehicle-has-means.py    ← wrong: scanners folder at repo root
tests/vehicle-has-means-test.py  ← wrong: tests folder at repo root
```
