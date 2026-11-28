# sparky-07: pattern hooks never run in a project with no guidelines list, though it uses those patterns everywhere else

**Title** - The hook server decides whether a pattern's hook runs from the project's own `guidelines` list alone, so in a project with no list (which uses CDD's list for its tools, install, overlays and graph) every pattern hook is off, including one for a pattern installed into that very project.

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. `ProjectGuidelines` docstring and CDR 0005: "A project with no list uses those CDD's own config lists, and with neither list every guideline"; "Every reader that lists, applies, chooses, or installs patterns asks the project's guidelines rather than the process's registry."

**Module and class** - `harness/hooks/hook_server.py` `HookHandler._pattern_enabled` calls `ContextConfig(root).uses_guideline(pattern)`, which is false whenever `guidelines()` is `None`; it does not ask `PROJECT_GUIDELINES.of(root).uses(pattern)`.

**Severity** - wrong result.

**Steps**
1. Sandbox env as in sparky-06.
2. `work/beta/.context/config.json` = `{"guidelines_folder": "guidelines"}` (no list); `guidelines/lern_domain_driven/lern_domain_driven.py` defines `class LernDomainDriven(Pattern)` with `@hook("postToolUse") def mark_edit(...)` returning `{"additional_context": "HOOK-OF-beta"}`.
3. Install into `work/beta/.cursor` as in sparky-06: the install publishes `cdd_claude_mod`, `cdd_web_domain_access` and beta's own `lern_domain_driven`, and `hook-handlers.json` lists `mark_edit`.
4. In one process: `PROJECT_GUIDELINES.of(beta).own_classes` (so the package imports, see sparky-06), `PROJECT_GUIDELINES.of(beta).uses("lern_domain_driven")`, then `HookServer.from_handlers(beta/.cursor/hook-handlers.json, repo=<build>).dispatch(HookPayload({"hook_event_name": "postToolUse", "workspace_roots": [beta], "tool_name": "Write", "tool_input": {"file_path": beta + r"\src\x.py"}}))`.
5. Control: alpha, which lists its pattern, answers `HOOK-OF-alpha` the same way.

**Expected** - `uses` is `True` and the hook answers `additional_context: HOOK-OF-beta`, as for alpha.

**Actual** - `uses("lern_domain_driven")` is `True`, but the dispatch answers `{'permission': 'allow'}`: the handler is never enabled. The same holds for any shipped pattern that gains a hook, in every project without a list.

**Tier that should catch it** - unit (`harness/hooks/hook_spec.py`: a pattern toolset with a hook, a project with no list, CDD's list naming the pattern). The hook specs cover a project that lists or leaves out the pattern, not one with no list.
