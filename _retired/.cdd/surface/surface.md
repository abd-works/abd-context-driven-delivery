Minimal CDD surface — paired `{surface}.md` and `{surface}.py`.

## Generate

Create `{surface}.md` and `{surface}.py` for a new surface. No template — boilerplate only.

**Alignment rule (always):**

- `{Surface}` class (PascalCase of folder name) mirrors the agentic surface — implement `deploy()` and `clean()` matching §Deploy and §Clean.
- `{Surface}Cli` routes `python -m …` only; no `*Deployer` classes.
- CLI **only** for actions with documented `python -m …` blocks (Deploy, Clean). Generate and Satisfy are agent-only — no CLI, no public satisfy/generate API.

After generate, run:

```
python surface/check_alignment.py <surface-folder>
```

## Satisfy

Check that `{surface}.md` and `{surface}.py` exist, names match, and surface identity is consistent. Rejects extension frontmatter — plain surfaces are closed.

**Alignment rule (always):**

- Main class `{Surface}` implements `deploy()` and `clean()` — not a separate `{Surface}Deployer`.
- `{Surface}Cli` subcommands match `{surface}.md` code blocks exactly.
- Agent-only sections (Generate, Satisfy) must not appear in `.py` CLI.

Always run:

```
python surface/check_alignment.py <surface-folder>
python -m pytest surface/test_surface.py
```

## Deploy

Discover all surfaces under the repo root and deploy each to the IDE area. Copies source to `.cdd/` and emits a SKILL.md pointer to the full `{surface}.md`. Surfaces on the `extend` chain get section wiring from `extend`.

```
python -m surface deploy <cursor|vscode> <target-root>
```

## Clean

Remove deployed artefacts for all discovered surfaces (uses each surface's deploy record when target is omitted).

```
python -m surface clean
```
