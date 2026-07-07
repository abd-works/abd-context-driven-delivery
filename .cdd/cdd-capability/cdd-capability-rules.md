# Rules

Rules that every CDD capability must satisfy.

---

## config-in-cdd-config

All capability state and configuration lives in `.cdd-config.json`. No separate config or state files alongside it.

**Pass** — deploy record, settings, and any other capability state are keys inside `.cdd-config.json`:
```json
{
  "deploy": {
    "ide": "cursor",
    "target_root": "/path/to/workspace",
    "deployed_at_utc": "2026-01-01T00:00:00+00:00"
  }
}
```

**Fail** — any of: `.cdd-deploy.json`, `config.json`, `settings.json`, or any other file used to store capability state instead of a key in `.cdd-config.json`.

---

## surface-files-entry-point

Every capability folder must contain an agentic surface and an API surface, both named after the folder.

```
{capability}/
  {capability}.md    ← agentic surface; top-level ## sections are the commands
  {capability}.py    ← API surface; exports CapabilityCli with execute(argv)
  .cdd-config.json   ← presence identifies this as a CDD capability
```

The `.md` file must open with a one-sentence description (no filename heading).  
The `.py` file must expose a `CapabilityCli` class with an `execute(argv: list[str]) -> int` method and a `main()` entry point.

**Pass** — `enforce/enforce.md` and `enforce/enforce.py` exist in an `enforce/` folder that has `.cdd-config.json`.

**Fail** — surface files named `README.md`, `index.py`, or anything other than `{folder-name}.md` / `{folder-name}.py`.

---

## templates-use-parameterized-placeholders

All template files must use `{placeholder}` syntax for every value that must be filled in when creating a new capability from the template.

**Pass** — `{capability}.md` contains `{capability}`, `{one sentence description}`, `{Action 1}`.

**Fail** — placeholders written as `<capability>`, `<description>`, `TODO`, or left blank.
