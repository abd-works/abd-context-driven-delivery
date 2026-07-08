# When and how to add deterministic code to a capability

## The problem

A capability defines agent behavior in `{capability}.md`. As actions grow complex, the agent reaches for ad-hoc scripts — one-off files, vibe-coded helpers, throwaway automation. These drift from the capability, aren't reviewed, and don't evolve with the surface.

The `.py` file exists to **head that off**: per capability, identify what must be deterministic and write it into `{Capability}` using structure — not random one-offs.

---

## When to add code (not prose)

Add a method to `{Capability}` when the action is:

| Signal | Example |
|--------|---------|
| **Repeatable mechanical steps** | Parse a folder, copy files, rename placeholders |
| **Must produce identical output** | Deploy emits same SKILL.md structure every time |
| **Validation / gate** | Check `.cdd-config.json` exists; fail with exit code 1 |
| **Filesystem or subprocess** | Discover capabilities under a root; run CLI |
| **Already happened once as a script** | Agent wrote `fix-thing.py` — that belongs in the capability |

Keep it in prose only when the action is:

| Signal | Example |
|--------|---------|
| **Judgment / taste** | Write a rule definition; critique an artifact |
| **One-off creative** | Generate initial draft from template |
| **Reads context and decides** | Fix violations — agent reads report and edits |

When unsure: start prose-only. Promote to `.py` when the same mechanical step appears twice or when output must be exact.

---

## Structure (not one-offs)

```
{capability}.md          → what the agent should do (## sections, parameters)
{capability}.py
  {Capability}           → deterministic logic; one method per promoted action
  {Capability}Cli        → thin shim; routes CLI args to {Capability}; inherits deploy/clean from base
```

Rules:

1. **One method per deterministic action** — named to match the `##` slug (`identify` → `identify()`).
2. **No scripts/ folder for capability-owned logic** — if it's part of this capability, it lives in `{Capability}`. Scripts folder is for optional bundled helpers the agent invokes ad-hoc (Agent Skills pattern), not core behavior.
3. **`.md` points at `.py`** — deterministic actions say `python -m {capability} <command>` in the `##` body; prose actions say `read in full →`.
4. **CLI is the contract** — if it's in `{Capability}`, it's callable via `{Capability}Cli`.

---

## How to evolve when needs change

### Prose → code (complexity grew)

1. Agent or human notices repeated mechanical work or inconsistent output.
2. Implement method on `{Capability}`; wire `{Capability}Cli._dispatch` and `_build_parser`.
3. Update `## {Action}` body: replace vague steps with the CLI command.
4. Delete any ad-hoc script the agent created; do not leave orphans.

### Code → prose (never needed determinism)

1. Remove method and CLI subcommand.
2. Restore instructional prose in `## {Action}`.
3. Rare — usually means the action was misclassified.

### New action

1. Add `## {Action}` to `.md` first (parameters, one sentence).
2. If deterministic signals apply, add method + CLI in same change — not later.
3. If extending a parent, override in `.md` only (`overrides:` in frontmatter); inherit parent's `.py` methods via deploy unless the override requires new implementation.

### Inherited actions

- Non-overridden: parent's `.py` methods serve you via base CLI — no empty stubs in child.
- Listed in `overrides:`: child `{Capability}` implements override; child's `##` section documents it.

---

## Anti-patterns

- Agent creates `scripts/helper.py` for work that is a core capability action → move into `{Capability}`.
- Empty `raise NotImplementedError` left in template after shipping → implement or remove the `##` section.
- `.md` describes steps that duplicate what `.py` already does → `.md` should only say run the CLI.
- Deterministic logic in deploy/clean copied into every capability → belongs in base `capability.py`, extended not duplicated.
