# Graph rule validation

**Generated:** 2026-11-26 18:05:30 UTC
**Project:** abd-cdd-ui-fixes-as-i-use-it
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-ui-fixes-as-i-use-it\.sessions\ui-fixes-as-i-use-it\.context\checked-graphs\clean-engineering-code-20261126T175040\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `.context`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/align`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/diagnostics`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
- `harness/agent_tools`
- `harness/annotations`
- `harness/apps`
- `harness/catalog_generator`
- `harness/chat`
- `harness/chat-ui`
- `harness/design_canvas`
- `harness/diagnostics`
- `harness/drawio`
- `harness/e2e_review`
- `harness/files_app`
- `harness/git`
- `harness/graph`
- `harness/guidance`
- `harness/guidance_actions`
- `harness/hooks`
- `harness/installation`
- `harness/markdown`
- `harness/mcp`
- `harness/process`
- `harness/release`
- `harness/whiteboard`
- `scripts`
- `scripts/names_exist`
- `scripts/unit_guard`
- `space`
- `space/.context`
- `space/kanban`
- `space/repo`
- `space/session`
- `story_tests`
- `story_tests/author-story-maps`
- `story_tests/build-design-canvas-screens`
- `story_tests/connect-sessions-across-channels-and-apps`
- `story_tests/deliver-work-with-context-guidance`
- `story_tests/draw-practice-models-on-claude-whiteboard`
- `story_tests/explore-stories-in-story-ui`
- `story_tests/map-work-into-knowledge-graph`
- `story_tests/move-work-forward-from-chat-bar`
- `story_tests/move-work-forward-on-session-board`
- `story_tests/queue-prompts-for-later`
- `story_tests/register-and-install-toolsets`
- `story_tests/review-end-to-end-screens`
- `story_tests/review-generated-work-in-file-viewer`
- `tools`
- `tools/.context`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**Total graph violations:** 167
**Rules with graph hits:** 5
**Candidates for the judge to read:** 4. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it.
**Accepted violations left out:** 5. A person accepted them as they are, in `.context/violations-accepted.json`; do not report them again.
**AI rules in scope:** 39

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6). A hit marked `**CANDIDATE**` comes from a rule that requires a judge: its check only lists places to read, so read each and fail the rule only where the reading finds it broken.

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

### `hide-inner-details`

Rule text: [clean_engineering/clean_engineering.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L243)

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:253](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L253)

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:353](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L353)

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:354](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L354)

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:251](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L251)

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:356](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L356)

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:255](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L255)

### `refuse-unreadable-input`

Rule text: [clean_engineering/clean_engineering.md:256](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L256)

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:359](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L359)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:269](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L269)

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:270](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L270)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:364](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L364)

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:271](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L271)

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/fact_files.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\lern_domain_driven\fact_files.py#L227): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L80): Operation `check`: Operation 'check' nearly duplicates 'check' (cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py): 71% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L136): Operation `web_path_literals`: Operation 'web_path_literals' nearly duplicates 'web_path_literals' (cdd_guidance/patterns/lern_domain_driven/fact_files.py): 76% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L205): Operation `_in_import`: Operation '_in_import' nearly duplicates '_in_import' (cdd_guidance/patterns/lern_domain_driven/fact_files.py): 73% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L211): Operation `_in_comment`: Operation '_in_comment' nearly duplicates '_in_comment' (cdd_guidance/patterns/lern_domain_driven/fact_files.py): 75% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L283): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/reading/code_file.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\reading\code_file.py#L462): Operation `module_cause`: Operation 'module_cause' nearly duplicates 'module_value' (cdd_guidance/practices/clean_engineering/reading/code_file.py): 87% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_map.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\stories\model\story_map.py#L308): Operation `__init__`: Operation '__init__' nearly duplicates '__init__' (cdd_guidance/practices/bdd/model/nodes.py): 71% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/mounted_view/canvas-runtime.js](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\mounted_view\canvas-runtime.js#L111): Operation `CanvasMount`: Operation 'CanvasMount' nearly duplicates 'canvasMount' (cdd_guidance/practices/ux/model/claude_design/mounted_view/canvas-runtime.js): 80% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/mounted_view/react/jsx-runtime.js](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\mounted_view\react\jsx-runtime.js#L5): Operation `element`: Operation 'element' duplicates the body of 'element'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/process/process.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\process\process.py#L137): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/release/test_runs.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\release\test_runs.py#L456): Operation `_removed_once_writable`: Operation '_removed_once_writable' nearly duplicates '_writable_then_retried' (cdd_guidance/actions/validate/report_files.py): 72% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:366](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L366)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:369](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L369)

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:370](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L370)

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:372](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L372)

### `limit-paths-through-a-function`

Rule text: [clean_engineering/clean_engineering.md:377](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L377)

### `keep-functions-readable`

Rule text: [clean_engineering/clean_engineering.md:378](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L378)

### `limit-function-lines`

Rule text: [clean_engineering/clean_engineering.md:379](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L379)

### `limit-class-complexity`

Rule text: [clean_engineering/clean_engineering.md:380](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L380)

### `limit-class-methods`

Rule text: [clean_engineering/clean_engineering.md:381](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L381)

### `keep-class-methods-sharing-data`

Rule text: [clean_engineering/clean_engineering.md:382](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L382)

### `limit-class-coupling`

Rule text: [clean_engineering/clean_engineering.md:383](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L383)

### `limit-class-response`

Rule text: [clean_engineering/clean_engineering.md:384](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L384)

### `limit-module-file-lines`

Rule text: [clean_engineering/clean_engineering.md:385](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L385)

### `keep-module-files-maintainable`

Rule text: [clean_engineering/clean_engineering.md:386](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L386)

### `limit-average-class-complexity`

Rule text: [clean_engineering/clean_engineering.md:387](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L387)

### `limit-copied-code-blocks`

Rule text: [clean_engineering/clean_engineering.md:388](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L388)

### `limit-modules-importing`

Rule text: [clean_engineering/clean_engineering.md:389](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L389)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:188](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L188)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:189](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L189)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:190](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L190)

### `declared-exception-raised-by-a-test`

Rule text: [tdd/tdd.md:191](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L191)

**Graph violations:** 35

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/source_code/statement_translation.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\source_code\statement_translation.py#L29): OoadClass `Untranslatable`: No test names the exception 'Untranslatable', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/canvas_explorer.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\canvas_explorer.py#L18): OoadClass `ExplorerTreeUnreadable`: No test names the exception 'ExplorerTreeUnreadable', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/mounted_view.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\mounted_view.py#L40): OoadClass `MountedViewsNotBuilt`: No test names the exception 'MountedViewsNotBuilt', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/project_story_canvas.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\project_story_canvas.py#L66): OoadClass `StoryMapNotFound`: No test names the exception 'StoryMapNotFound', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/screen_files.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\screen_files.py#L43): OoadClass `ContainerCssFailed`: No test names the exception 'ContainerCssFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/screen_walk.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\screen_walk.py#L47): OoadClass `ScreenWalkUnavailable`: No test names the exception 'ScreenWalkUnavailable', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/recipe.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\agent_tools\recipe.py#L240): OoadClass `RecipeNotAFunction`: No test names the exception 'RecipeNotAFunction', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\apps\app.py#L217): OoadClass `AppServerNotRestarted`: No test names the exception 'AppServerNotRestarted', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\apps\app.py#L234): OoadClass `NpmNotFound`: No test names the exception 'NpmNotFound', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\apps\app.py#L238): OoadClass `NpmTooSlow`: No test names the exception 'NpmTooSlow', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\apps\app.py#L278): OoadClass `PackageNotInstalled`: No test names the exception 'PackageNotInstalled', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\catalog_generator\catalog_generator.py#L459): OoadClass `CatalogNotGenerated`: No test names the exception 'CatalogNotGenerated', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/app-client.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\chat-ui\pane\hooks\health\app-client.ts#L23): OoadClass `AppNotOpened`: No test names the exception 'AppNotOpened', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/shared/cdd-tool.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\chat-ui\pane\hooks\shared\cdd-tool.ts#L11): OoadClass `CddToolFailed`: No test names the exception 'CddToolFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\diagnostics\agent_tools_probe.py#L40): OoadClass `ProbeCallTimedOut`: No test names the exception 'ProbeCallTimedOut', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/drawio-viewer.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\files_app\app\drawio-viewer.ts#L11): OoadClass `DrawioViewerNotStarted`: No test names the exception 'DrawioViewerNotStarted', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/file-explorer.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\files_app\app\file-explorer.ts#L8): OoadClass `FileNotThere`: No test names the exception 'FileNotThere', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/graph-api.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\app\graph\graph-api.ts#L7): OoadClass `GraphCallFailure`: No test names the exception 'GraphCallFailure', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\action_catalogue.py#L127): OoadClass `ActionsNotRegistered`: No test names the exception 'ActionsNotRegistered', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_formats.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\practice_formats.py#L250): OoadClass `NoFormatReads`: No test names the exception 'NoFormatReads', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_formats.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\practice_formats.py#L259): OoadClass `SourceFormatNotSet`: No test names the exception 'SourceFormatNotSet', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\installation\destination.py#L94): OoadClass `SkippedTool`: No test names the exception 'SkippedTool', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/format.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\markdown\format.py#L133): OoadClass `ContentNotHeld`: No test names the exception 'ContentNotHeld', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/cdd_home.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\mcp\cdd_home.py#L30): OoadClass `PinFailed`: No test names the exception 'PinFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\mcp\mcp_server.py#L67): OoadClass `McpStandupFailed`: No test names the exception 'McpStandupFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/tool_calls.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\mcp\tool_calls.py#L48): OoadClass `ToolCallStopped`: No test names the exception 'ToolCallStopped', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/process/process.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\process\process.py#L377): OoadClass `ProcessNotStopped`: No test names the exception 'ProcessNotStopped', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/process/starter_bound_job.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\process\starter_bound_job.py#L45): OoadClass `JobNotMade`: No test names the exception 'JobNotMade', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/backlog_folder.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\backlog_folder.py#L17): OoadClass `IdeaHeldError`: No test names the exception 'IdeaHeldError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\board.py#L99): OoadClass `CardNotInColumnError`: No test names the exception 'CardNotInColumnError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket_checkout.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\ticket_checkout.py#L294): OoadClass `TicketWorktreeBlockedError`: No test names the exception 'TicketWorktreeBlockedError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket_checkout.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\ticket_checkout.py#L305): OoadClass `EditsInTheWayOfMergeError`: No test names the exception 'EditsInTheWayOfMergeError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/files/file_comments.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\files\file_comments.py#L48): OoadClass `FileCommentNotFoundError`: No test names the exception 'FileCommentNotFoundError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_folder.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\session_folder.py#L24): OoadClass `SessionFolderHeldError`: No test names the exception 'SessionFolderHeldError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\prompt_queue\hooks\queue\prompt-queue.ts#L140): OoadClass `QueueCallFailed`: No test names the exception 'QueueCallFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:192](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L192)

### `check-use-the-graph-cannot-see`

Rule text: [clean_engineering/clean_engineering.md:279](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L279)

**Candidates for the judge to read:** 3

- [?] **CANDIDATE** **[graph rule]** - [tools/drawio_viewer/drawio_viewer.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\drawio_viewer\drawio_viewer.py#L152): Operation `do_GET`: Operation 'do_GET': no use the graph can see, but 2 calls in the files that could reach it are made on values no type says, and one may reach it. Read them, and delete it with its specs if none reaches it.
- [?] **CANDIDATE** **[graph rule]** - [tools/drawio_viewer/drawio_viewer.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\drawio_viewer\drawio_viewer.py#L160): Operation `do_POST`: Operation 'do_POST': no use the graph can see, but 2 calls in the files that could reach it are made on values no type says, and one may reach it. Read them, and delete it with its specs if none reaches it.
- [?] **CANDIDATE** **[graph rule]** - [tools/drawio_viewer/drawio_viewer.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\drawio_viewer\drawio_viewer.py#L179): Operation `log_message`: Operation 'log_message': no use the graph can see, but 2 calls in the files that could reach it are made on values no type says, and one may reach it. Read them, and delete it with its specs if none reaches it.

### `delete-unused-classes`

Rule text: [clean_engineering/clean_engineering.md:277](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L277)

**Graph violations:** 46

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `Box (harness/whiteboard)`: Class 'Box (harness/whiteboard)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `ClassCard (markdown/class_card.py)`: Class 'ClassCard (markdown/class_card.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `MeasuredBody (Protocol)`: Class 'MeasuredBody (Protocol)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `ModuleMeta (module_context_files.py)`: Class 'ModuleMeta (module_context_files.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `SketchFence (markdown/class_card.py)`: Class 'SketchFence (markdown/class_card.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/.context/ddd-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ddd\model\.context\ddd-model.md#L1): OoadClass `Clean Engineering conversion`: Class 'Clean Engineering conversion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/.context/ddd-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ddd\model\.context\ddd-model.md#L195): OoadClass `BuildingBlock`: Class 'BuildingBlock': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\stories\model\.context\story-model.md#L1): OoadClass `EpicColumns (diagram_story_map.py)`: Class 'EpicColumns (diagram_story_map.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\stories\model\.context\story-model.md#L1): OoadClass `OpenedStoryMap / UnopenedStoryMap`: Class 'OpenedStoryMap / UnopenedStoryMap': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\stories\model\.context\story-model.md#L331): OoadClass `Formats`: Class 'Formats': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/.context/ux-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\.context\ux-model.md#L34): OoadClass `NoJavascriptPractice`: Class 'NoJavascriptPractice': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/.context/ux-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\.context\ux-model.md#L285): OoadClass `Formats`: Class 'Formats': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/screen_walk.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\screen_walk.py#L47): OoadClass `ScreenWalkUnavailable`: Class 'ScreenWalkUnavailable': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `Deploy boundary (installation)`: Class 'Deploy boundary (installation)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `ExpandedRecipe (protocol)`: Class 'ExpandedRecipe (protocol)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/app-client.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\chat-ui\pane\hooks\health\app-client.ts#L23): OoadClass `AppNotOpened`: Class 'AppNotOpened': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat/chat.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\chat\chat.py#L55): OoadClass `SentCommand`: Class 'SentCommand': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `A practice in the graph (PracticeReading)`: Class 'A practice in the graph (PracticeReading)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `Explorer answers`: Class 'Explorer answers': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `FilterRequest, FilterChoices, Filter (node_filter.py)`: Class 'FilterRequest, FilterChoices, Filter (node_filter.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `GraphBuild (graph_build.py)`: Class 'GraphBuild (graph_build.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `GraphPractices (graph_practices.py)`: Class 'GraphPractices (graph_practices.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `GraphReads (graph_reads.py)`: Class 'GraphReads (graph_reads.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `LoadScope (load_scope.py)`: Class 'LoadScope (load_scope.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `What a practice declares on its PracticeGuidance`: Class 'What a practice declares on its PracticeGuidance': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L1): OoadClass `graph.json`: Class 'graph.json': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L298): OoadClass `_EDGE_ORDER`: Class '_EDGE_ORDER': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L566): OoadClass `Nodes`: Class 'Nodes': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L579): OoadClass `Edges`: Class 'Edges': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\.context\graph-populate-model.md#L594): OoadClass `Rules`: Class 'Rules': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `RenderPlace (frozen)`: Class 'RenderPlace (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `RenderRequest (frozen)`: Class 'RenderRequest (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `Reshaped (frozen)`: Class 'Reshaped (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `Written (frozen)`: Class 'Written (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-runtime-model.md#L1): OoadClass `Installed artifacts`: Class 'Installed artifacts': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-runtime-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\markdown\.context\markdown-collection-model.md#L1): OoadClass `Guidance (caller)`: Class 'Guidance (caller)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\markdown\.context\markdown-collection-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\markdown\.context\markdown-collection-model.md#L1): OoadClass `RulesCollection (caller)`: Class 'RulesCollection (caller)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\.context\kanban-model.md#L1144): OoadClass `MainStaysOpenError`: Class 'MainStaysOpenError': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\prompt_log\prompt_log.py#L64): OoadClass `PromptAttachment`: Class 'PromptAttachment': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/.context/prompt-notify-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\prompt_notify\.context\prompt-notify-model.md#L1): OoadClass `NoticeWatcher (ide_toast, JavaScript)`: Class 'NoticeWatcher (ide_toast, JavaScript)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/.context/prompt-notify-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\prompt_notify\.context\prompt-notify-model.md#L7): OoadClass `Language`: Class 'Language': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\prompt_queue\hooks\queue\prompt-queue.ts#L140): OoadClass `QueueCallFailed`: Class 'QueueCallFailed': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*

### `delete-unused-operations`

Rule text: [clean_engineering/clean_engineering.md:278](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L278)

**Graph violations:** 70

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/.context/actions-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\actions\.context\actions-model.md#L87): Operation `made_for`: Operation 'made_for': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/.context/actions-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\actions\.context\actions-model.md#L106): Operation `made_for`: Operation 'made_for': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/.context/patterns-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\.context\patterns-model.md#L47): Operation `test_setup_text`: Operation 'test_setup_text': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/lern_domain_driven.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\lern_domain_driven\lern_domain_driven.py#L28): Operation `canvas_fixtures`: Operation 'canvas_fixtures': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/practices/stories/model/claude_design/story_runtime.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\patterns\lern_domain_driven\practices\stories\model\claude_design\story_runtime.py#L53): Operation `check`: Operation 'check': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/measures/copied_blocks.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\measures\copied_blocks.py#L43): Property `said`: Property 'said': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L733): Operation `ClassHeading`: Operation 'ClassHeading': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1267): Operation `value_on`: Operation 'value_on': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1269): Operation `said_of`: Operation 'said_of': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/.context/ux-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\.context\ux-model.md#L13): Operation `Ux`: Operation 'Ux': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/.context/ux-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\.context\ux-model.md#L19): Operation `javascript_practice`: Operation 'javascript_practice': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/mounted_view.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\mounted_view.py#L123): Operation `copy_files`: Operation 'copy_files': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/mounted_view.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\mounted_view.py#L127): Operation `sources`: Operation 'sources': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/mounted_view/canvas-runtime.js](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\mounted_view\canvas-runtime.js#L108): Operation `canvasMount`: Operation 'canvasMount': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/project_story_canvas.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\project_story_canvas.py#L76): Operation `build`: Operation 'build': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/project_story_canvas.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\project_story_canvas.py#L129): Operation `print_summary`: Operation 'print_summary': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/prototype_states.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\prototype_states.py#L62): Operation `story_screens`: Operation 'story_screens': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/claude_design/screen_walk.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\claude_design\screen_walk.py#L245): Operation `walk`: Operation 'walk': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/shown_places.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\ux\model\shown_places.py#L70): Operation `shown_on`: Operation 'shown_on': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/.context/apps-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\apps\.context\apps-model.md#L23): Operation `registered`: Operation 'registered': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/design_canvas/versions.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\design_canvas\versions.py#L106): Property `accepted_misses`: Property 'accepted_misses': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/git/git_facts.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\git\git_facts.py#L77): Property `checkout`: Property 'checkout': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/app/explorer/explorer-filter.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\app\explorer\explorer-filter.ts#L41): Property `offered`: Property 'offered': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/app/explorer/explorer-filter.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\app\explorer\explorer-filter.ts#L76): Operation `apply`: Operation 'apply': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_node_types.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\practice_node_types.py#L149): Operation `node_types`: Operation 'node_types': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_reading.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\graph\practice_reading.py#L172): Operation `node_types`: Operation 'node_types': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\guidance-model.md#L344): Operation `keys`: Operation 'keys': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L162): Operation `SupplementWorkingSet`: Operation 'SupplementWorkingSet': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\.context\practice-guidance-model.md#L669): Operation `SchemaRelationship`: Operation 'SchemaRelationship': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/format_trip.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\format_trip.py#L56): Property `passes`: Property 'passes': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/format_trip.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\format_trip.py#L119): Operation `of`: Operation 'of': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/format_trip.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\format_trip.py#L133): Operation `through_each`: Operation 'through_each': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/worked_session.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\worked_session.py#L71): Property `recorded`: Property 'recorded': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/worked_session.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\guidance\worked_session.py#L74): Operation `of`: Operation 'of': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-model.md#L32): Operation `disabled_on`: Operation 'disabled_on': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-model.md#L33): Operation `deploys`: Operation 'deploys': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-runtime-model.md#L50): Operation `Hooks`: Operation 'Hooks': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-runtime-model.md#L104): Operation `HooksManifest`: Operation 'HooksManifest': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-runtime-model.md#L116): Operation `HookHandlersFile`: Operation 'HookHandlersFile': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\hooks\.context\hooks-runtime-model.md#L196): Operation `HookMessages`: Operation 'HookMessages': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/installation/.context/installation-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\installation\.context\installation-model.md#L574): Operation `Identity`: Operation 'Identity': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/claude_marketplace.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\mcp\claude_marketplace.py#L102): Property `version`: Property 'version': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/claude_marketplace.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\mcp\claude_marketplace.py#L111): Property `installed_name`: Property 'installed_name': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\.context\kanban-model.md#L1109): Operation `from_report`: Operation 'from_report': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L14): Operation `fillSplit`: Operation 'fillSplit': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L23): Property `closeHint`: Property 'closeHint': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L27): Operation `startClose`: Operation 'startClose': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L31): Operation `fillHandoff`: Operation 'fillHandoff': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L36): Operation `fillSetUpRoots`: Operation 'fillSetUpRoots': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L41): Operation `validateAgain`: Operation 'validateAgain': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-drops.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-drops.ts#L18): Operation `dropOn`: Operation 'dropOn': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-face.ts#L13): Property `origin`: Property 'origin': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-face.ts#L18): Property `stagePlace`: Property 'stagePlace': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-face.ts#L27): Property `runNextHint`: Property 'runNextHint': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-face.ts#L33): Property `nextNote`: Property 'nextNote': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-face.ts#L38): Property `lockNote`: Property 'lockNote': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-next-step.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-next-step.ts#L16): Property `canRun`: Property 'canRun': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-next-step.ts](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\kanban\app\src\kanban\ticket\ticket-next-step.ts#L25): Operation `run`: Operation 'run': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\repo\repo.py#L638): Operation `serve`: Operation 'serve': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/.context/session-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\.context\session-model.md#L138): Operation `of_chat`: Operation 'of_chat': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/.context/session-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\.context\session-model.md#L333): Operation `line`: Operation 'line': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/.context/session-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\.context\session-model.md#L343): Operation `mark_loop`: Operation 'mark_loop': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/idea_file.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\idea_file.py#L21): Property `path`: Property 'path': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/practices/guidance_selection.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\practices\guidance_selection.py#L251): Operation `command`: Operation 'command': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\session_log.py#L125): Operation `names`: Operation 'names': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\session_log.py#L175): Operation `note`: Operation 'note': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\session_log.py#L369): Property `chat`: Property 'chat': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\session_log.py#L377): Operation `validation`: Operation 'validation': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\space\session\session_log.py#L397): Operation `guidance_action`: Operation 'guidance_action': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/.context/tools-model.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\.context\tools-model.md#L64): Operation `log_for`: Operation 'log_for': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*

### `put-logic-on-the-owning-resource`

Rule text: [clean_engineering/clean_engineering.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L242)

**Candidates for the judge to read:** 1

- [?] **CANDIDATE** **[graph rule]** - [tools/drawio_viewer/drawio_viewer.py](C:\dev\abd-cdd-ui-fixes-as-i-use-it\tools\drawio_viewer\drawio_viewer.py#L145): OoadClass `DrawioViewerHandler`: Class 'DrawioViewerHandler' looks up a 'DiagramLinks' by name (in _open_editor, _links_of). Read whether 'DrawioViewerHandler' should hold the DiagramLinks it means, handed to it (association), or own it as a part it builds once and keeps (composition).

### `seam-names-current-code`

Rule text: [clean_engineering/clean_engineering.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L146)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\actions#L1): Module `actions`: Module 'actions' imports 'harness/design_canvas', which its card does not name among its dependencies. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/agent_bdd](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\agent_bdd#L1): Module `agent_bdd`: Module 'agent_bdd' card names the dependency 'harness/installation', which its code does not import. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd](C:\dev\abd-cdd-ui-fixes-as-i-use-it\cdd_guidance\practices\bdd#L1): Module `bdd`: Module 'bdd' imports 'harness/markdown', which its card does not name among its dependencies. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/whiteboard](C:\dev\abd-cdd-ui-fixes-as-i-use-it\harness\whiteboard#L1): Module `whiteboard`: Module 'whiteboard' card names the dependency 'harness/installation', which its code does not import. *(outside the paths this validate was given)*
