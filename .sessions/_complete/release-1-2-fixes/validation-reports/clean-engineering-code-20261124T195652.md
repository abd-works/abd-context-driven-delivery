# Graph rule validation

**Generated:** 2026-11-24 20:09:26 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\clean-engineering-code-20261124T195652\graph.json`

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
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**Total graph violations:** 152
**Rules with graph hits:** 8
**Candidates for the judge to read:** 37. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it.
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

Rule text: [clean_engineering/clean_engineering.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L241)

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:251](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L251)

**Candidates for the judge to read:** 7

- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L499): Operation `call_seconds`: Operation 'ProjectToolsets.call_seconds' hands its parameter 'name' on unchanged to 2 other classes: ProjectToolsets.call_seconds, ProjectToolsets.enrolled, ProjectToolsets.resolve_call_name, AgentTool.is_called, names_alike. Read which object should hold the name, so the operations below it read it there.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L507): Operation `invoke`: Operation 'ProjectToolsets.invoke' hands its parameter 'mcp_name' on unchanged to 2 other classes: ProjectToolsets.invoke, ProjectToolsets.answer, ProjectToolsets.enrolled, ProjectToolsets.resolve_call_name, AgentTool.is_called, names_alike. Read which object should hold the mcp_name, so the operations below it read it there.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L727): Operation `answer_for_chat`: Operation 'McpHost.answer_for_chat' hands its parameter 'call' on unchanged to 4 other classes: McpHost.answer_for_chat, McpHost.answer, McpHost._answer_between_restarts, ProjectToolsets.answer, AgentInstructions.answer, AgentTool.log_session_invocation, AgentToolSet.session_for. Read which object should hold the call, so the operations below it read it there.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L782): Operation `_ping_tool`: Operation 'McpHost._ping_tool' hands its parameter 'tool' on unchanged to 3 other classes: McpHost._ping_tool, ProjectToolsets.enrolled, ProjectToolsets.resolve_call_name, AgentTool.is_called, names_alike. Read which object should hold the tool, so the operations below it read it there.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L787): Operation `_log_failure`: Operation 'McpHost._log_failure' hands its parameter 'failure' on unchanged to 3 other classes: McpHost._log_failure, Session.log_failure, ChatLog.failure, SessionLog.append_trace. Read which object should hold the failure, so the operations below it read it there.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L885): Operation `content_blocks`: Operation 'ChatProtocol.content_blocks' hands its parameter 'answer' on unchanged to 2 other classes: ChatProtocol.content_blocks, data_of, DataClass.data. Read which object should hold the answer, so the operations below it read it there.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L971): Operation `_answer_chat`: Operation 'ChatProtocol._answer_chat' hands its parameter 'name' on unchanged to 3 other classes: ChatProtocol._answer_chat, ChatProtocol._call_from_chat, ProjectToolsets.resolve_call_name, AgentTool.is_called, names_alike. Read which object should hold the name, so the operations below it read it there.

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:351](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L351)

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:352](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L352)

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:249](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L249)

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:354](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L354)

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:253](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L253)

### `refuse-unreadable-input`

Rule text: [clean_engineering/clean_engineering.md:254](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L254)

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:357](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L357)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:267](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L267)

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:268](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L268)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:362](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L362)

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:269](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L269)

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/fact_files.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\lern_domain_driven\fact_files.py#L227): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L80): Operation `check`: Operation 'check' nearly duplicates 'check' (cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py): 71% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L136): Operation `web_path_literals`: Operation 'web_path_literals' nearly duplicates 'web_path_literals' (cdd_guidance/patterns/lern_domain_driven/fact_files.py): 76% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L205): Operation `_in_import`: Operation '_in_import' nearly duplicates '_in_import' (cdd_guidance/patterns/lern_domain_driven/fact_files.py): 73% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L211): Operation `_in_comment`: Operation '_in_comment' nearly duplicates '_in_comment' (cdd_guidance/patterns/lern_domain_driven/fact_files.py): 75% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L283): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/reading/code_file.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\reading\code_file.py#L462): Operation `module_cause`: Operation 'module_cause' nearly duplicates 'module_value' (cdd_guidance/practices/clean_engineering/reading/code_file.py): 87% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_map.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_map.py#L308): Operation `__init__`: Operation '__init__' nearly duplicates '__init__' (cdd_guidance/practices/bdd/model/nodes.py): 71% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/process/process.py](C:\dev\abd-cdd-release-1-2-fixes\harness\process\process.py#L137): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/release/test_runs.py](C:\dev\abd-cdd-release-1-2-fixes\harness\release\test_runs.py#L456): Operation `_removed_once_writable`: Operation '_removed_once_writable' nearly duplicates '_writable_then_retried' (cdd_guidance/actions/validate/report_files.py): 72% of their code is the same. Give the shared logic one function. *(outside the paths this validate was given)*

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:364](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L364)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:367](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L367)

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:368](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L368)

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:257](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L257)

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:370](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L370)

### `limit-paths-through-a-function`

Rule text: [clean_engineering/clean_engineering.md:375](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L375)

### `keep-functions-readable`

Rule text: [clean_engineering/clean_engineering.md:376](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L376)

### `limit-function-lines`

Rule text: [clean_engineering/clean_engineering.md:377](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L377)

### `limit-class-complexity`

Rule text: [clean_engineering/clean_engineering.md:378](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L378)

### `limit-class-methods`

Rule text: [clean_engineering/clean_engineering.md:379](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L379)

### `keep-class-methods-sharing-data`

Rule text: [clean_engineering/clean_engineering.md:380](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L380)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L659): OoadClass `McpHost`: Class 'McpHost' has 3 groups of methods that share no data with one another (lack of cohesion), over the limit of 1. Each group uses none of the fields the others use, so it is a second class kept inside this one: move it out.

### `limit-class-coupling`

Rule text: [clean_engineering/clean_engineering.md:381](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L381)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L659): OoadClass `McpHost`: Class 'McpHost' has 15 classes it depends on (coupling between objects), over the limit of 14. Find the classes it only passes values between and let them talk to each other, or split the class by the collaborators each part needs.

### `limit-class-response`

Rule text: [clean_engineering/clean_engineering.md:382](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L382)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L659): OoadClass `McpHost`: Class 'McpHost' has 54 methods one call into it can set off (response for a class), over the limit of 50. Ask each collaborator for the one result the class needs instead of calling its steps one by one, or split the class by the calls each part makes.

### `limit-module-file-lines`

Rule text: [clean_engineering/clean_engineering.md:383](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L383)

### `keep-module-files-maintainable`

Rule text: [clean_engineering/clean_engineering.md:384](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L384)

### `limit-average-class-complexity`

Rule text: [clean_engineering/clean_engineering.md:385](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L385)

### `limit-copied-code-blocks`

Rule text: [clean_engineering/clean_engineering.md:386](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L386)

### `limit-modules-importing`

Rule text: [clean_engineering/clean_engineering.md:387](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L387)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:184](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L184)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:185](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L185)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:186](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L186)

### `declared-exception-raised-by-a-test`

Rule text: [tdd/tdd.md:187](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L187)

**Graph violations:** 29

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/source_code/statement_translation.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\source_code\statement_translation.py#L29): OoadClass `Untranslatable`: No test names the exception 'Untranslatable', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/recipe.py](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\recipe.py#L240): OoadClass `RecipeNotAFunction`: No test names the exception 'RecipeNotAFunction', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-release-1-2-fixes\harness\apps\app.py#L217): OoadClass `AppServerNotRestarted`: No test names the exception 'AppServerNotRestarted', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-release-1-2-fixes\harness\apps\app.py#L234): OoadClass `NpmNotFound`: No test names the exception 'NpmNotFound', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-release-1-2-fixes\harness\apps\app.py#L238): OoadClass `NpmTooSlow`: No test names the exception 'NpmTooSlow', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/app.py](C:\dev\abd-cdd-release-1-2-fixes\harness\apps\app.py#L278): OoadClass `PackageNotInstalled`: No test names the exception 'PackageNotInstalled', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/catalog_generator/catalog_generator.py](C:\dev\abd-cdd-release-1-2-fixes\harness\catalog_generator\catalog_generator.py#L459): OoadClass `CatalogNotGenerated`: No test names the exception 'CatalogNotGenerated', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/app-client.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\health\app-client.ts#L23): OoadClass `AppNotOpened`: No test names the exception 'AppNotOpened', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/shared/cdd-tool.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\shared\cdd-tool.ts#L11): OoadClass `CddToolFailed`: No test names the exception 'CddToolFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/agent_tools_probe.py](C:\dev\abd-cdd-release-1-2-fixes\harness\diagnostics\agent_tools_probe.py#L40): OoadClass `ProbeCallTimedOut`: No test names the exception 'ProbeCallTimedOut', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/drawio-viewer.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\drawio-viewer.ts#L11): OoadClass `DrawioViewerNotStarted`: No test names the exception 'DrawioViewerNotStarted', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/file-explorer.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\file-explorer.ts#L8): OoadClass `FileNotThere`: No test names the exception 'FileNotThere', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/graph-api.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\graph\graph-api.ts#L7): OoadClass `GraphCallFailure`: No test names the exception 'GraphCallFailure', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/action_catalogue.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\action_catalogue.py#L127): OoadClass `ActionsNotRegistered`: No test names the exception 'ActionsNotRegistered', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_formats.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_formats.py#L250): OoadClass `NoFormatReads`: No test names the exception 'NoFormatReads', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_formats.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_formats.py#L259): OoadClass `SourceFormatNotSet`: No test names the exception 'SourceFormatNotSet', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/installation/destination.py](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\destination.py#L94): OoadClass `SkippedTool`: No test names the exception 'SkippedTool', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/format.py](C:\dev\abd-cdd-release-1-2-fixes\harness\markdown\format.py#L133): OoadClass `ContentNotHeld`: No test names the exception 'ContentNotHeld', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/cdd_home.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\cdd_home.py#L30): OoadClass `PinFailed`: No test names the exception 'PinFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/tool_calls.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\tool_calls.py#L48): OoadClass `ToolCallStopped`: No test names the exception 'ToolCallStopped', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/process/process.py](C:\dev\abd-cdd-release-1-2-fixes\harness\process\process.py#L377): OoadClass `ProcessNotStopped`: No test names the exception 'ProcessNotStopped', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/process/starter_bound_job.py](C:\dev\abd-cdd-release-1-2-fixes\harness\process\starter_bound_job.py#L45): OoadClass `JobNotMade`: No test names the exception 'JobNotMade', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/backlog_folder.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\backlog_folder.py#L17): OoadClass `IdeaHeldError`: No test names the exception 'IdeaHeldError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\board.py#L99): OoadClass `CardNotInColumnError`: No test names the exception 'CardNotInColumnError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket_checkout.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket_checkout.py#L294): OoadClass `TicketWorktreeBlockedError`: No test names the exception 'TicketWorktreeBlockedError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket_checkout.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket_checkout.py#L305): OoadClass `EditsInTheWayOfMergeError`: No test names the exception 'EditsInTheWayOfMergeError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/files/file_comments.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\files\file_comments.py#L48): OoadClass `FileCommentNotFoundError`: No test names the exception 'FileCommentNotFoundError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_folder.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_folder.py#L24): OoadClass `SessionFolderHeldError`: No test names the exception 'SessionFolderHeldError', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L132): OoadClass `QueueCallFailed`: No test names the exception 'QueueCallFailed', so no test sees it raised: add a test that breaks its invariant and expects it. *(outside the paths this validate was given)*

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:188](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L188)

### `delete-unused-classes`

Rule text: [clean_engineering/clean_engineering.md:275](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L275)

**Graph violations:** 45

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `Box (harness/whiteboard)`: Class 'Box (harness/whiteboard)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `ClassCard (markdown/class_card.py)`: Class 'ClassCard (markdown/class_card.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `MeasuredBody (Protocol)`: Class 'MeasuredBody (Protocol)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `ModuleMeta (module_context_files.py)`: Class 'ModuleMeta (module_context_files.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1): OoadClass `SketchFence (markdown/class_card.py)`: Class 'SketchFence (markdown/class_card.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/.context/ddd-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\.context\ddd-model.md#L1): OoadClass `Clean Engineering conversion`: Class 'Clean Engineering conversion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/.context/ddd-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\.context\ddd-model.md#L195): OoadClass `BuildingBlock`: Class 'BuildingBlock': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L1): OoadClass `EpicColumns (diagram_story_map.py)`: Class 'EpicColumns (diagram_story_map.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L1): OoadClass `OpenedStoryMap / UnopenedStoryMap`: Class 'OpenedStoryMap / UnopenedStoryMap': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L331): OoadClass `Formats`: Class 'Formats': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/.context/ux-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\.context\ux-model.md#L34): OoadClass `NoJavascriptPractice`: Class 'NoJavascriptPractice': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/.context/ux-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\.context\ux-model.md#L285): OoadClass `Formats`: Class 'Formats': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `Deploy boundary (installation)`: Class 'Deploy boundary (installation)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `ExpandedRecipe (protocol)`: Class 'ExpandedRecipe (protocol)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat-ui/pane/hooks/health/app-client.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\chat-ui\pane\hooks\health\app-client.ts#L23): OoadClass `AppNotOpened`: Class 'AppNotOpened': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/chat/chat.py](C:\dev\abd-cdd-release-1-2-fixes\harness\chat\chat.py#L55): OoadClass `SentCommand`: Class 'SentCommand': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `A practice in the graph (PracticeReading)`: Class 'A practice in the graph (PracticeReading)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `Explorer answers`: Class 'Explorer answers': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `FilterRequest, FilterChoices, Filter (node_filter.py)`: Class 'FilterRequest, FilterChoices, Filter (node_filter.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `GraphBuild (graph_build.py)`: Class 'GraphBuild (graph_build.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `GraphPractices (graph_practices.py)`: Class 'GraphPractices (graph_practices.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `GraphReads (graph_reads.py)`: Class 'GraphReads (graph_reads.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `LoadScope (load_scope.py)`: Class 'LoadScope (load_scope.py)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `What a practice declares on its PracticeGuidance`: Class 'What a practice declares on its PracticeGuidance': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): OoadClass `graph.json`: Class 'graph.json': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L298): OoadClass `_EDGE_ORDER`: Class '_EDGE_ORDER': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L566): OoadClass `Nodes`: Class 'Nodes': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L579): OoadClass `Edges`: Class 'Edges': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L594): OoadClass `Rules`: Class 'Rules': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `RenderPlace (frozen)`: Class 'RenderPlace (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `RenderRequest (frozen)`: Class 'RenderRequest (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `Reshaped (frozen)`: Class 'Reshaped (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L1): OoadClass `Written (frozen)`: Class 'Written (frozen)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): OoadClass `Installed artifacts`: Class 'Installed artifacts': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\markdown\.context\markdown-collection-model.md#L1): OoadClass `Guidance (caller)`: Class 'Guidance (caller)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\markdown\.context\markdown-collection-model.md#L1): OoadClass `Language companion`: Class 'Language companion': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\markdown\.context\markdown-collection-model.md#L1): OoadClass `RulesCollection (caller)`: Class 'RulesCollection (caller)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L1112): OoadClass `MainStaysOpenError`: Class 'MainStaysOpenError': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_log\prompt_log.py#L64): OoadClass `PromptAttachment`: Class 'PromptAttachment': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/.context/prompt-notify-model.md](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_notify\.context\prompt-notify-model.md#L1): OoadClass `NoticeWatcher (ide_toast, JavaScript)`: Class 'NoticeWatcher (ide_toast, JavaScript)': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/.context/prompt-notify-model.md](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_notify\.context\prompt-notify-model.md#L7): OoadClass `Language`: Class 'Language': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L132): OoadClass `QueueCallFailed`: Class 'QueueCallFailed': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*

### `delete-unused-operations`

Rule text: [clean_engineering/clean_engineering.md:276](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L276)

**Graph violations:** 62

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/.context/actions-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\.context\actions-model.md#L87): Operation `made_for`: Operation 'made_for': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/.context/actions-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\.context\actions-model.md#L106): Operation `made_for`: Operation 'made_for': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/.context/patterns-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\.context\patterns-model.md#L47): Operation `test_setup_text`: Operation 'test_setup_text': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/measures/copied_blocks.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\measures\copied_blocks.py#L43): Property `said`: Property 'said': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L733): Operation `ClassHeading`: Operation 'ClassHeading': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1267): Operation `value_on`: Operation 'value_on': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1269): Operation `said_of`: Operation 'said_of': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/.context/ux-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\.context\ux-model.md#L13): Operation `Ux`: Operation 'Ux': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/.context/ux-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\.context\ux-model.md#L19): Operation `javascript_practice`: Operation 'javascript_practice': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/apps/.context/apps-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\apps\.context\apps-model.md#L23): Operation `registered`: Operation 'registered': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/git/git_facts.py](C:\dev\abd-cdd-release-1-2-fixes\harness\git\git_facts.py#L77): Property `checkout`: Property 'checkout': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/app/explorer/explorer-filter.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\explorer\explorer-filter.ts#L41): Property `offered`: Property 'offered': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/app/explorer/explorer-filter.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\explorer\explorer-filter.ts#L76): Operation `apply`: Operation 'apply': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_node_types.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\practice_node_types.py#L149): Operation `node_types`: Operation 'node_types': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_reading.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\practice_reading.py#L172): Operation `node_types`: Operation 'node_types': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\guidance-model.md#L344): Operation `keys`: Operation 'keys': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L162): Operation `SupplementWorkingSet`: Operation 'SupplementWorkingSet': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L669): Operation `SchemaRelationship`: Operation 'SchemaRelationship': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/format_trip.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\format_trip.py#L56): Property `passes`: Property 'passes': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/format_trip.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\format_trip.py#L119): Operation `of`: Operation 'of': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/format_trip.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\format_trip.py#L133): Operation `through_each`: Operation 'through_each': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/worked_session.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\worked_session.py#L71): Property `recorded`: Property 'recorded': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/guidance/worked_session.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\worked_session.py#L74): Operation `of`: Operation 'of': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-model.md#L32): Operation `disabled_on`: Operation 'disabled_on': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-model.md#L33): Operation `deploys`: Operation 'deploys': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L50): Operation `Hooks`: Operation 'Hooks': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L104): Operation `HooksManifest`: Operation 'HooksManifest': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L116): Operation `HookHandlersFile`: Operation 'HookHandlersFile': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L196): Operation `HookMessages`: Operation 'HookMessages': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/installation/.context/installation-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\installation\.context\installation-model.md#L574): Operation `Identity`: Operation 'Identity': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/claude_marketplace.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\claude_marketplace.py#L102): Property `version`: Property 'version': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/claude_marketplace.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\claude_marketplace.py#L111): Property `installed_name`: Property 'installed_name': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L682): Property `chat_protocol`: Property 'chat_protocol': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L687): Property `http_endpoints`: Property 'http_endpoints': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it.
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L1077): Operation `from_report`: Operation 'from_report': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L14): Operation `fillSplit`: Operation 'fillSplit': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L23): Property `closeHint`: Property 'closeHint': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L27): Operation `startClose`: Operation 'startClose': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L31): Operation `fillHandoff`: Operation 'fillHandoff': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L36): Operation `fillSetUpRoots`: Operation 'fillSetUpRoots': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-chat-prompts.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-chat-prompts.ts#L41): Operation `validateAgain`: Operation 'validateAgain': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-drops.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-drops.ts#L12): Operation `canDropOn`: Operation 'canDropOn': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-drops.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-drops.ts#L18): Operation `dropOn`: Operation 'dropOn': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-face.ts#L13): Property `origin`: Property 'origin': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-face.ts#L18): Property `stagePlace`: Property 'stagePlace': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-face.ts#L27): Property `runNextHint`: Property 'runNextHint': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-face.ts#L33): Property `nextNote`: Property 'nextNote': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-face.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-face.ts#L38): Property `lockNote`: Property 'lockNote': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-next-step.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-next-step.ts#L16): Property `canRun`: Property 'canRun': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/ticket-next-step.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\ticket-next-step.ts#L25): Operation `run`: Operation 'run': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\dev\abd-cdd-release-1-2-fixes\space\repo\repo.py#L604): Operation `serve`: Operation 'serve': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/.context/session-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\session\.context\session-model.md#L138): Operation `of_chat`: Operation 'of_chat': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/.context/session-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\session\.context\session-model.md#L333): Operation `line`: Operation 'line': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/.context/session-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\session\.context\session-model.md#L343): Operation `mark_loop`: Operation 'mark_loop': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/idea_file.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\idea_file.py#L21): Property `path`: Property 'path': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/practices/guidance_selection.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\practices\guidance_selection.py#L251): Operation `command`: Operation 'command': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_log.py#L125): Operation `names`: Operation 'names': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_log.py#L175): Operation `note`: Operation 'note': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_log.py#L369): Property `chat`: Property 'chat': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_log.py#L377): Operation `validation`: Operation 'validation': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [space/session/session_log.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_log.py#L397): Operation `guidance_action`: Operation 'guidance_action': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [tools/.context/tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\tools\.context\tools-model.md#L64): Operation `log_for`: Operation 'log_for': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of the `code_reach` ways its `.context/config.json` names reaches it. *(outside the paths this validate was given)*

### `keep-classes-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:238](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L238)

**Candidates for the judge to read:** 2

- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L368): OoadClass `ProjectToolsets`: Class 'ProjectToolsets' exposes 11 public operations (budget ~9). Split responsibilities.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L659): OoadClass `McpHost`: Class 'McpHost' exposes 11 public operations (budget ~9). Split responsibilities.

### `make-module-only-operations-private`

Rule text: [clean_engineering/clean_engineering.md:278](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L278)

**Candidates for the judge to read:** 10

- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/claude_plugins.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\claude_plugins.py#L64): Operation `install`: Operation 'install': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L705): Operation `tools_listed_for`: Operation 'tools_listed_for': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L716): Operation `call_sent`: Operation 'call_sent': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L722): Operation `tool_request`: Operation 'tool_request': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L727): Operation `answer_for_chat`: Operation 'answer_for_chat': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L747): Operation `answer`: Operation 'answer': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L792): Operation `serve`: Operation 'serve': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L796): Operation `restart`: Operation 'restart': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L814): Operation `diagnose`: Operation 'diagnose': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L826): Operation `from_repo`: Operation 'from_repo': public on a class its module shows other modules, but only code inside the module calls it. Make it private to the module, or say which other module should call it.

### `prefer-class-operations`

Rule text: [clean_engineering/clean_engineering.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L243)

**Candidates for the judge to read:** 1

- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L845): OoadClass `McpHost`: Module function '_listed_tool' (line 845) is only used from 'McpHost'. Move it onto 'McpHost' as a method.

### `put-logic-on-the-owning-resource`

Rule text: [clean_engineering/clean_engineering.md:240](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L240)

**Candidates for the judge to read:** 17

- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L100): OoadClass `CddEntry`: Class 'CddEntry' looks up a 'IdeLayout' by name (in write, _write_claude_plugin, _write_dev_lane_entry, _drop_cdd_entry, _server_manifest, is_user_level, path, _project_root, _layout). Read whether 'CddEntry' should hold the IdeLayout it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L100): OoadClass `CddEntry`: Class 'CddEntry' builds a 'JsonFile' on each call (in _ide_config), from strings or dicts. Read whether 'CddEntry' should own it: a part it builds once and keeps (composition), or a JsonFile handed to it and held (association).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L100): OoadClass `CddEntry`: Class 'CddEntry' looks up a 'JsonFile' by name (in write, _write_dev_lane_entry, _allow_cdd_tools, _drop_cdd_entry, _has_cdd_entry, _merged_with_other_servers, _ide_config). Read whether 'CddEntry' should hold the JsonFile it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L269): OoadClass `McpChannelServer`: Class 'McpChannelServer' builds a 'SkippedTools' on each call (in stand_up), from strings or dicts. Read whether 'McpChannelServer' should own it: a part it builds once and keeps (composition), or a SkippedTools handed to it and held (association).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L269): OoadClass `McpChannelServer`: Class 'McpChannelServer' looks up a 'McpHost' by name (in stand_up). Read whether 'McpChannelServer' should hold the McpHost it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L319): OoadClass `McpInstallation`: Class 'McpInstallation' looks up a 'ServerLanes' by name (in __init__, create, lanes, daemon). Read whether 'McpInstallation' should hold the ServerLanes it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L368): OoadClass `ProjectToolsets`: Class 'ProjectToolsets' looks up a 'AgentTool' by name (in enroll, call_seconds, answer, _tools, _prompts). Read whether 'ProjectToolsets' should hold the AgentTool it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L368): OoadClass `ProjectToolsets`: Class 'ProjectToolsets' looks up a 'AgentToolSet' by name (in enroll, start, _enroll_with_children, _enroll_toolset). Read whether 'ProjectToolsets' should hold the AgentToolSet it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L368): OoadClass `ProjectToolsets`: Class 'ProjectToolsets' looks up a 'ToolsetReference' by name (in start, restarted, of_repo, of_refs, _toolsets). Read whether 'ProjectToolsets' should hold the ToolsetReference it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L368): OoadClass `ProjectToolsets`: Class 'ProjectToolsets' builds a 'ToolRequest' on each call (in invoke), from strings or dicts. Read whether 'ProjectToolsets' should own it: a part it builds once and keeps (composition), or a ToolRequest handed to it and held (association).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L572): OoadClass `ChatRequest`: Class 'ChatRequest' looks up a 'ClaudeChatProcess' by name (in _folder_the_chat_works_in, process, chat). Read whether 'ChatRequest' should hold the ClaudeChatProcess it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L572): OoadClass `ChatRequest`: Class 'ChatRequest' looks up a 'ChatPointer' by name (in _folder_of_chat, chat). Read whether 'ChatRequest' should hold the ChatPointer it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L659): OoadClass `McpHost`: Class 'McpHost' looks up a 'ProjectToolsets' by name (in __init__, _server_for, tools_listed_for, dispatch, _answer_between_restarts, _ping_tool, restart, diagnose, from_repo, from_refs, _checkout_toolsets, _servers). Read whether 'McpHost' should hold the ProjectToolsets it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L864): OoadClass `ChatProtocol`: Class 'ChatProtocol' looks up a 'AgentTool' by name (in _register_prompt_handlers). Read whether 'ChatProtocol' should hold the AgentTool it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L864): OoadClass `ChatProtocol`: Class 'ChatProtocol' looks up a 'ToolCall' by name (in _answer_chat, _answer_off_loop). Read whether 'ChatProtocol' should hold the ToolCall it means, handed to it (association), or own it as a part it builds once and keeps (composition).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L1039): OoadClass `HttpEndpoints`: Class 'HttpEndpoints' builds a 'LaneReply' on each call (in _answer_lane_call), from strings or dicts. Read whether 'HttpEndpoints' should own it: a part it builds once and keeps (composition), or a LaneReply handed to it and held (association).
- [?] **CANDIDATE** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L1039): OoadClass `HttpEndpoints`: Class 'HttpEndpoints' looks up a 'LaneReply' by name (in _answer_lane_call). Read whether 'HttpEndpoints' should hold the LaneReply it means, handed to it (association), or own it as a part it builds once and keeps (composition).

### `seam-names-current-code`

Rule text: [clean_engineering/clean_engineering.md:144](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L144)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions#L1): Module `actions`: Module 'actions' imports 'harness/design_canvas', which its card does not name among its dependencies. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/agent_bdd](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\agent_bdd#L1): Module `agent_bdd`: Module 'agent_bdd' card names the dependency 'harness/installation', which its code does not import. *(outside the paths this validate was given)*
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd#L1): Module `bdd`: Module 'bdd' imports 'harness/markdown', which its card does not name among its dependencies. *(outside the paths this validate was given)*
