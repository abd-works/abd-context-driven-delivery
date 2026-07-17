# Focused examples

## Rule

Each package keeps examples that exercise **only that package's concept**. Specs and agentic tests import from the examples co-located with the package they test — not from a shared grab-bag folder.

| Package | Example location | Tests |
|---------|------------------|-------|
| `tools/` | `tools/examples/` — `@tool`, `@resource`, manifest, CLI (`Car`) plus repair fixtures | `tools/tools_spec.py`, `tools/tools_agent_spec.py` |
| `agents/` | `agents/examples/` — `@action` orchestration (`Car` with `travelTo`) plus repair fixtures | `agents/agents_spec.py`, `agents/agents_agent_spec.py` |
| `generator/` | `generator/examples/` — `@generator`, instruction inlining, repair fixtures | `generator/generator_spec.py`, `generator/generator_agent_spec.py` |
| `agent_bdd/` | reusable agent channels: `cursor_channel` (cursor-agent CLI), `agent_chat_bdd` (in-chat inbox); shared types in `agent_bdd_common`; BDD harness in `agent_cli_bdd` / `agent_chat_bdd`; secrets at `agent_bdd/conf/.secrets` | `agent_bdd/agent_bdd_spec.py` |
| `clean-code/` | `clean-code/examples/` — worked samples and scanner repair fixtures | `clean-code/clean_code_spec.py` |

Do not add `@action` examples under `tools/examples/`. Do not add generator dummy toolsets under `tools/examples/`.

## Examples

**Wrong:** `CarChronicle` lives in `tools/examples/` because "examples go in tools."

**Right:** `Car` with only `@tool` lives in `tools/examples/`; `Car` with `travelTo` lives in `agents/examples/`.
