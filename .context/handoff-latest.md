## Next session focus

partition_guidance templatization complete — all domain partition.md files cleaned,
partition_guidance.md owns the hard-fail with `{{self.domain_slug}}`.

## Resume in three lines

- Stage: refactor complete — all `partition.md` files standardized, fidelity model finalized (3×3), template/sketch folders flattened, spec files merged.
- Last work accepted: `partition_guidance.md` now holds the templatized hard-fail line; domain `partition.md` files stripped of their literal hard-fail headers; `partition_guidance()` in `partition_pipeline.py` combines base hard-fail + domain content at expand time; `{{self.domain_slug}}` substitution resolves at action expansion.
- Exact next action: run the full spec suite across all modified context tools to confirm no regressions remain beyond pre-existing `car_chronicle` and `actions_spec`/`tools_spec` module failures.

## Generator state

- Active toolset: none (refactoring session, no generator active)
- context_index_path: `.context/context-index.md`
- Current tool roots: stories = `./tests/*`

## Grilling / skills state

- No grill-answers active
- Suggested skills for next agent: none required; straight spec run + any backlog items

## CDD progress

- No cdd-sketch active

## Artifacts to read

- `.context/context-index.md`
- `utilities/partition_pipeline/partition_guidance.md` — base hard-fail template (2 lines)
- `utilities/partition_pipeline/partition_pipeline.py` — `partition_guidance()` method (combined expand)
- `context_tools/*/partition.md` — all five domain files (hard-fail removed, content starts at `Multi-pass:`)

## Key decisions made this session

| Area | Decision |
|------|----------|
| Fidelity model | 3 stages per tool: DISCOVERY / SPEC / ENGINEER (EXPLORE removed everywhere) |
| Stories fidelities | `story_map` → `scenarios` → `acceptance_tests`; generate/iterate/transform call `ce()` when at `acceptance_tests` |
| BDD fidelities | `modules` (delegates to CE) → `behavior` → `development` |
| DDD fidelities | `bounded_context` → `building_blocks` → `code` |
| UX fidelities | `ia` → `mockup` → `code` |
| CE fidelities | `modules` → `model` → `code` |
| CDD stages | `discovery` → `spec` → `engineer` (no `explore`) |
| Template folders | `bdd/templates/`, `ddd/templates/`, `agent_bdd/templates/` (flattened from `formats/`) |
| Sketch templates | All in `{tool}/templates/{tool}-sketch.md`; sketch utility searches `templates/*-sketch.*` |
| `base_context_tool_fidelity_spec.py` | Merged into `base_context_tool_spec.py` and deleted |
| `PartitionPipeline`/`Repair` inheritance | Removed from BaseContextTool MI; methods injected via explicit class-attr binding |
| `_session` property | Removed (dead code); `repair.py` updated to use `self.workspace()` |
| `diagnose.md` files | Deleted (orphaned, content duplicated in class docstrings) |
| Hard-fail templatization | `partition_guidance.md` owns `{{self.domain_slug}}.md` template; domain files no longer repeat it |

## Open questions / risks

- Pre-existing test failures: `car_chronicle` module missing (`ModuleNotFoundError`), `actions_spec`, `tools_spec` — all pre-existing, not introduced this session.
- `partition_pipeline_spec.py` `_DEFAULT_PARTITION_SNIPPET` updated to `"Hard fail"` to match new base content.
- The multi-pass lines in domain `partition.md` files retain domain-specific column names (e.g. "Epic / Mid-epic" for Stories) — these are intentionally not templatized.
