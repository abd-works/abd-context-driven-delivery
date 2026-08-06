# Session: manifest-gate

## Start

- **date:** 2026-08-04
- **path:** primitives/tools/hooks
- **goal:** Guarantee every governed asset reliably receives its governing context tool's manifest guidance before an edit - deliver it once per chat and reuse it, fail loud (not silent) when a manifest can't load, and let normal/verbose modes surface manifest activity - replacing the current deny-until-cleared gate.
- **fidelities:** acceptance_tests
- **contexts:** manifest-gate-stories-sketch

## Progress

- **2026-08-04 - unit-testable stories, GREEN.** Wrote `*_story.py` + `*_test_helper.domain.py`
  under `keep-generated-assets-guided-by-their-context-tools/{sub-epic}/{story}/` for the two
  stories that are pure-function behavior (no live agent needed):
  - `treat-a-missing-manifest-as-exceptional/recover-from-a-manifest-that-wont-load/`
  - `report-manifest-lifecycle-events/see-the-manifest-run-as-it-happens/`
  CE-wired directly (already well-understood change, done in the same pass rather than a
  separate RED-then-GREEN cycle): `manifest_gate.run_manifests` now retries a failing manifest
  command up to 2 times before reporting it as a failure instead of silently swallowing
  `TimeoutExpired`/`OSError`; a total failure raises an all-caps `user_message` via
  `_manifest_failure_notification`; `context_tools/base/manifest_gate_conf.py` (temporary home)
  reads `normal`/`verbose` mode from `context_tools/base/.context/conf/manifest_gate.json`;
  verbose mode narrates hook-fired / executing / loaded in the hook's `user_message`; normal mode
  gets one confirmation from both the hook and from `cli.py`'s `_manifest_main` directly (so a
  bare `python -m tools manifest ...` call with no hook involved still confirms).
  Updated `manifest_gate_spec.py`'s existing `run_manifests` mocks to the new 2-tuple return
  shape (output, failures) - no behavior change there, just the new signature. All 21
  pre-existing examples plus the 7 new acceptance tests pass:
  `mamba primitives/tools/hooks/manifest_gate_spec.py` and
  `pytest primitives/tools/hooks/keep-generated-assets-guided-by-their-context-tools -o "python_files=*_test_helper.*.py" --import-mode=importlib`.
- **2026-08-04 - "Edit A Governed Asset" (the agent-verified story), GREEN, live.** Rewrote
  `manifest_gate.py` end to end: dropped the deny-until-cleared mechanism entirely -
  `handle_pre_tool_use`'s `permission: deny` path, `.manifest_gate_clearance.json` (deleted),
  `is_cleared`/`clear_path`/`mark_pending_invoke`, `handle_after_shell`, and the invoke-edit
  self-execution/parsing machinery (`find_invoke_edit`, `parse_invoke_directive`,
  `build_invoke_edit_request`). `preToolUse`/`postToolUse`/`beforeReadFile` now share one
  `_deliver_guidance` helper: run every `@toolset-manifest` line's command, deliver the full
  output, always `permission: allow`. Removed the now-dead `afterShellExecution` hook
  registration from both `.cursor/hooks.json` files and from
  `primitives/tools/hooks/manifest-gate.json`. Rewrote `manifest_gate_spec.py`'s
  `handle_pre_tool_use`/`handle_post_tool_use` examples to match (allow-always, no clearance);
  dropped the `handle_after_shell` and `parse_invoke_directive`/`find_invoke_edit` example
  groups (functions no longer exist). `mamba manifest_gate_spec.py`: 17/17 green.

  Retired the four old agent specs (`hooks_direct_edit_agent_spec.py`,
  `hooks_satisfy_then_edit_agent_spec.py`, `hooks_adhoc_subagent_edit_agent_spec.py`,
  `hooks_sub_agent_annotation_edit_agent_spec.py`) - they asserted the retired deny-until-cleared
  behavior, separately per caller. Caller identity no longer matters, so one first-touch spec and
  one repeat-touch spec replace all four, plus a new recursive-governance spec:
  - `hooks_first_touch_delivers_guidance_agent_spec.py` - read then edit the GatedWidget fixture;
    guidance delivered on the read, edit proceeds directly (no deny).
  - `hooks_repeat_touch_reuses_guidance_agent_spec.py` - edit the same fixture twice in the same
    chat session; both edits proceed directly, nothing accumulates.
  - `hooks_recursive_governance_agent_spec.py` - read `context_tools/bdd/bdd.py` (a context
    tool's own source, itself a governed asset); guidance delivered the same as any other asset.

  All three ran for real via `mamba` against the authenticated `cursor-agent` CLI harness
  (`_cli_agent`, real nested sessions - not mocked, not in-chat inbox) and passed live:
  `mamba primitives/tools/hooks/hooks_first_touch_delivers_guidance_agent_spec.py`,
  `hooks_repeat_touch_reuses_guidance_agent_spec.py`, `hooks_recursive_governance_agent_spec.py`.
  Nested cursor-agent calls run 60-150s+ each; timeouts on the `instruct()` calls are set to
  120-240s accordingly. Assertions check literal `RESULT: EDIT SUCCEEDED`/`MANIFEST GATE`
  markers the instructed sub-agent states, not a `permission: allow` string - Cursor's own edit
  tool result doesn't echo `permission` back verbatim on a silent allow, only on a deny.

  All three increments from the sketch are now done and verified:
  `mamba manifest_gate_spec.py` (17), `pytest .../keep-generated-assets-guided-by-their-context-tools`
  (7), and the three live agent specs above (3). Total 27 examples green.

- **2026-08-05 - "a governing tool's own source is itself a governed asset" split into two
  testable scenarios.** That scenario's `then` was not testable as written - "the same
  guidance-delivery behavior applies, recursively, all the way down to the base primitives"
  is a design principle, not an observable outcome, and it had a second claim ("and no context
  tool is exempt...") tacked on with `and` rather than its own `given/when/then`. Split into:
  - "a governing tool's own source is itself a governed asset" - mid-level example
    (context_tools/bdd/bdd.py) - `then` now says concretely what the gate does: delivers that
    file's own governing toolset's guidance, same as any other generated asset.
  - "the recursion has no floor - base primitives are governed too" - new scenario, base-level
    example (primitives/assets/assets.py, confirmed live to be BDD-governed) - `then` is the
    former "and no context tool is exempt" claim, now its own testable predicate at a distinct
    layer rather than an addendum to the first scenario.

  Added `hooks_base_primitive_governance_agent_spec.py` (companion to the existing
  `hooks_recursive_governance_agent_spec.py`, which now covers only the mid-level scenario) -
  reads `primitives/assets/assets.py` and asserts `MANIFEST GATE` guidance is delivered. Ran live
  against the authenticated `cursor-agent` CLI harness: passed
  (`mamba primitives/tools/hooks/hooks_base_primitive_governance_agent_spec.py`, 100s). Unit spec
  still 17/17 green (no production-code change this round, sketch + spec-file work only).

- **2026-08-05 - `/stories validate` pass after the sketch splits above.** `Stories.validate`
  (context: fidelity acceptance_tests, path primitives/tools/hooks, session manifest-gate)
  returned its critical-judge instructions and pointed at `scan`; the `scan` tool call itself
  hung (4+ min, zero output) and was killed. Did the validation by hand instead - walked every
  current sketch scenario against its generated artifact:
  - Edit A Governed Asset's 4 scenario-groups (first touch+edit, repeat touch, mid-level tool
    source, base-primitive source) each already have a matching `hooks_*_agent_spec.py` with a
    docstring naming the scenario - pass.
  - See The Manifest Run As It Happens's 2 normal-mode scenarios and 1 verbose-mode scenario
    (3 narrated events) all match `see_the_manifest_run_as_it_happens_story.py`'s 5 test
    functions - pass, already fixed in the prior entry.
  - Recover From A Manifest That Won't Load - untouched by this session's sketch edits, still
    matches `recover_from_a_manifest_that_wont_load_story.py` - pass.
  No further test or production-code changes needed. `mamba manifest_gate_spec.py` (17) and
  `pytest .../keep-generated-assets-guided-by-their-context-tools` (7) both still green.
