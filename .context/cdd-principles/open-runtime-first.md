Maximise use of open standard runtime harness machinery — `SKILL.md`, `AGENTS.md`, `.cursor/rules/`, command files — before building custom tooling.

The runtime harness already provides skill discovery, agent routing, rule injection, and command dispatch. Capabilities should plug into these mechanisms rather than reimplement them.

**DO** — use harness primitives:
- `SKILL.md` for skill registration and command routing
- `.cursor/commands/{capability}-{command}.md` for IDE-invokable commands
- `.cursor/rules/` (or `AGENTS.md`) for persistent coding conventions injected into every session
- `extends:` / `overrides:` frontmatter and the `extend` capability to compose surfaces without custom wiring

**DON'T** — duplicate what the harness already does:
- Custom plugin registries that mirror skill discovery
- Bespoke command dispatch layers that replicate what command files already handle
- Embedding routing logic in code that belongs in `SKILL.md` sections
