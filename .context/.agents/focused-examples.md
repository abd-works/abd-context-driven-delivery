# Focused examples

## Rule

Each package keeps examples that exercise **only that package's concept**. Specs and agentic tests import from the examples co-located with the package they test — not from a shared grab-bag folder.

| Package | Example location | Tests |
|---------|------------------|-------|
| `primitives/tools/` | `primitives/tools/examples/` — `@tool`, `@resource`, manifest, CLI (`Car`) plus repair fixtures | `primitives/tools/tools_spec.py`, `tools_agent_spec.py` |
| `primitives/actions/` | `primitives/actions/examples/` — `@action` orchestration (`Car` with `travelTo`, chaining) plus repair fixtures | `primitives/actions/actions_spec.py`, `actions_agent_spec.py` |
| `context_tools/` | `context_tools/base/examples/` — `@context`, instruction inlining, repair fixtures | `context_tools/base/context_spec.py`, `context_tools/base/context_agent_spec.py` |
| `context_tools/agent_bdd/` | reusable agent channels: `cursor_channel` (cursor-agent CLI), `agent_chat_bdd` (in-chat inbox); shared types in `agent_bdd_common`; BDD harness in `agent_cli_bdd` / `agent_chat_bdd`; secrets at `context_tools/agent_bdd/conf/.secrets` | `context_tools/agent_bdd/agent_bdd_spec.py` |
| `context_tools/clean_engineering/` | `context_tools/clean_engineering/examples/` and `evals/engineering/` — worked samples and scanner repair fixtures | `context_tools/clean_engineering/clean_engineering_spec.py`, `scanners/scanners_spec.py` |

Do not add `@action` examples under `primitives/tools/examples/`. Do not add concept dummy toolsets under `primitives/tools/examples/`.

## Examples

**Wrong:** `CarChronicle` lives in `tools/examples/` because "examples go in tools."

**Right:** `Car` with only `@tool` lives in `primitives/tools/examples/`; `Car` with `travelTo` lives in `primitives/actions/examples/`.
