# Graph rule validation

**Generated:** 2026-11-16 23:29:22 UTC
**Project:** harness
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\file-manager\.context\checked-graphs\clean-engineering-code-20261116T232901\graph.json`

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

**Total graph violations:** 3
**Rules with graph hits:** 2
**AI rules in scope:** 24

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

### `hide-inner-details`

Rule text: [clean_engineering/clean_engineering.md:233](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L233)

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L243)

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:325](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L325)

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:326](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L326)

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L241)

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:328](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L328)

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L245)

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:330](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L330)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:258](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L258)

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:335](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L335)

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:260](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L260)

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:337](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L337)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:340](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L340)

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:341](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L341)

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:248](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L248)

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:343](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L343)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:144](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L144)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L145)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L146)

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:147](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L147)

### `keep-classes-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:230](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L230)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [graph/graph.py](C:\dev\abd-cdd-file-manager\harness\graph\graph.py#L934): OoadClass `_HeldNodes`: Class '_HeldNodes' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [graph/graph.py](C:\dev\abd-cdd-file-manager\harness\graph\graph.py#L1445): OoadClass `Graph`: Class 'Graph' exposes 18 public operations (budget ~9). Split responsibilities.

### `prefer-class-operations`

Rule text: [clean_engineering/clean_engineering.md:235](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L235)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [graph/graph.py](C:\dev\abd-cdd-file-manager\harness\graph\graph.py#L57): OoadClass `Source`: Module function '_decorated_end' (line 57) is only used from 'Source'. Move it onto 'Source' as a method.

## Judgment — `harness/graph/graph.py`

The change (bea33125b) adds two private operations to `Filter`: `_listed_or_below_listed` and `_source_listed`, called from `Filter.matches`. No rule fails on them: each is one job, under 20 statements, flat control flow, and both branches (own file listed; an ancestor's file listed) are taken by the Switch Files App To Graph View story ("A story listed only by its story map holds its scenarios" and "The Changed button keeps only the nodes of changed files").

The three graph hits are on code this change did not touch and stand as before (not fixed in this pass): `keep-classes-single-responsibility` on `Graph` (graph.py:1445) and `_HeldNodes` (graph.py:934), `prefer-class-operations` on `_decorated_end` (graph.py:57).
