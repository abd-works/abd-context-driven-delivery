# Graph rule validation

**Generated:** 2026-11-17 01:47:47 UTC
**Project:** harness
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\file-manager\.context\checked-graphs\stories-acceptance-tests-20261117T014730\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `../story_tests`
- `agent_tools`
- `annotations`
- `catalog_generator`
- `chat`
- `chat-ui`
- `chat-ui/pane`
- `design_canvas`
- `diagnostics`
- `diagnostics/examples`
- `files_app`
- `files_app/app`
- `git`
- `graph`
- `graph/app`
- `guidance`
- `guidance_actions`
- `hooks`
- `installation`
- `markdown`
- `mcp`
- `mcp/examples`
- `mcp/scripts`
- `process`
- `process/examples`
- `whiteboard`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 33

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `examples-declare-seed-vs-interaction`

Rule text: [stories/stories.md:230](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L230)

### `shared-example-fixtures`

Rule text: [stories/stories.md:231](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L231)

### `seed-state-at-its-real-owner`

Rule text: [stories/stories.md:232](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L232)

### `separate-test-controls-from-production-contracts`

Rule text: [stories/stories.md:233](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L233)

### `system-stubs-domain-real`

Rule text: [stories/stories.md:234](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L234)

### `assert-domain-behavior-not-seeded-state`

Rule text: [stories/stories.md:235](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L235)

### `infrastructure-in-lifecycle-hooks`

Rule text: [stories/stories.md:236](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L236)

### `inline-simple-gwt-bodies`

Rule text: [stories/stories.md:237](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L237)

### `domain-operations-inline-in-steps`

Rule text: [stories/stories.md:238](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L238)

### `code-steps-invoke-code`

Rule text: [stories/stories.md:239](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L239)

### `extract-assertion-helper`

Rule text: [stories/stories.md:240](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L240)

### `suffix-names-the-tier`

Rule text: [tdd/tdd.md:112](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L112)

### `unit-tier-fakes-every-boundary`

Rule text: [tdd/tdd.md:113](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L113)

### `heavy-tier-holds-a-real-resource`

Rule text: [tdd/tdd.md:114](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L114)

### `e2e-tier-drives-browser-or-agent`

Rule text: [tdd/tdd.md:115](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L115)

### `slow-example-moves-not-the-file`

Rule text: [tdd/tdd.md:116](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L116)

### `no-skipped-or-empty-test`

Rule text: [tdd/tdd.md:117](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L117)

### `unit-example-within-100-ms`

Rule text: [tdd/tdd.md:120](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L120)

### `unit-file-within-2-seconds`

Rule text: [tdd/tdd.md:121](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L121)

### `unit-tier-within-25-seconds`

Rule text: [tdd/tdd.md:122](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L122)

### `specs-run-in-parallel`

Rule text: [tdd/tdd.md:123](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L123)

### `heavy-spec-owns-its-resources`

Rule text: [tdd/tdd.md:124](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L124)

### `expensive-fixture-built-once`

Rule text: [tdd/tdd.md:125](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L125)

### `no-wait-in-unit-test`

Rule text: [tdd/tdd.md:126](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L126)

### `budget-never-raised`

Rule text: [tdd/tdd.md:127](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L127)

### `stubbed-boundary-has-heavy-coverage`

Rule text: [tdd/tdd.md:130](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L130)

### `heavy-example-has-a-stubbed-twin`

Rule text: [tdd/tdd.md:131](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L131)

### `heavy-run-within-the-hour`

Rule text: [tdd/tdd.md:134](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L134)

### `e2e-run-within-the-day`

Rule text: [tdd/tdd.md:135](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L135)

### `release-follows-a-green-e2e`

Rule text: [tdd/tdd.md:136](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L136)
