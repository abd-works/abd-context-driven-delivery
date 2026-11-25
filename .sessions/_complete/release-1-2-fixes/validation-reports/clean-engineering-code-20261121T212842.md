# Graph rule validation

**Generated:** 2026-11-21 21:30:13 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\clean-engineering-code-20261121T212842\graph.json`

## Summary

**Total graph violations:** 388
**Rules with graph hits:** 24
**AI rules in scope:** 48

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

**Graph violations:** 21

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L418): OoadClass `Relationship`: Class 'Relationship' copies the fields ['cardinality', 'description', 'kind', 'sequential_order', 'target'] of 'Relationship'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L732): OoadClass `CodeSpelling`: Class 'CodeSpelling' copies the fields ['base_constructor', 'base_receiver', 'camel_case', 'construct', 'receiver', 'statement_end'] of 'CodeSpelling'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L745): OoadClass `CodeLanguage`: Class 'CodeLanguage' copies the fields ['indent', 'line_comment', 'name', 'suffixes', 'unfinished'] of 'CodeLanguage'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L831): OoadClass `CallGraphEntry`: Class 'CallGraphEntry' copies the fields ['depth', 'kind', 'text'] of 'CallGraphEntry'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/call_links.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\call_links.py#L120): OoadClass `ClassLinks`: Class 'ClassLinks' copies the fields ['_graph', '_in_graph', '_reach'] of 'ClassNodes'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/diagram/geometry.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\diagram\geometry.py#L11): OoadClass `Geometry`: Class 'Geometry' copies the fields ['height', 'width', 'x', 'y'] of 'Geometry'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\markdown\markdown_class_model.py#L358): OoadClass `MarkdownModule`: Class 'MarkdownModule' holds '_card_name', a name copy of a 'Card'; hold the Card itself.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/script_imports.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\script_imports.py#L122): OoadClass `PythonImports`: Class 'PythonImports' copies the fields ['_package', '_qualified', '_text'] of 'ScriptImportClauses'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/.context/ddd-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\.context\ddd-model.md#L331): OoadClass `MarkdownBoundedContext`: Class 'MarkdownBoundedContext' copies the fields ['group_notes', 'module_notes', 'notes'] of 'MarkdownBoundedContext'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/modelled_areas.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\modelled_areas.py#L33): OoadClass `ExampleObservations`: Class 'ExampleObservations' copies the fields ['graph', 'stories', 'tree'] of 'StoryLinks'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `ExpansionResult                                                <!-- Md -->`: Class 'ExpansionResult                                                <!-- Md -->' copies the fields ['instructions', 'result', 'tools'] of 'ExpansionResult'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/failure-fixes.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\failure-fixes.ts#L33): OoadClass `FailureFixes`: Class 'FailureFixes' copies the fields ['api', 'chat', 'store'] of 'FilesNotices'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_formats.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_formats.py#L43): OoadClass `Reshaped`: Class 'Reshaped' copies the fields ['added', 'changed', 'kept'] of '_FileEdit'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_reading.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_reading.py#L57): OoadClass `PracticeReading`: Class 'PracticeReading' copies the fields ['anchor_types', 'class_node_type', 'class_types', 'graph', 'in_graph', 'member_types', 'node_types', 'reads_after', 'rule_types', 'source_ordered_types'] of 'PracticeReading'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\schema.py#L32): OoadClass `SchemaType`: Class 'SchemaType' copies the fields ['fields', 'key', 'rules'] of 'SchemaType'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_daemon.py](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_daemon.py#L93): OoadClass `HookDaemonIdentity`: Class 'HookDaemonIdentity' copies the fields ['pid', 'repo', 'stamp'] of 'HookDaemonAddress                                              <!-- Md -->'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_server.py#L188): OoadClass `HookMessages`: Class 'HookMessages' copies the fields ['additional_context', 'agent_message', 'followup_message', 'toast', 'user_message'] of 'HookResult                                                     <!-- Md -->'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L694): OoadClass `StageWork`: Class 'StageWork' copies the fields ['action_states', 'allowed_actions', 'commands', 'has_violations', 'stage', 'violation_count'] of 'FidelityProgress'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/session/file_comments.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\file_comments.py#L55): OoadClass `CommentSending`: Class 'CommentSending' copies the fields ['chat', 'message', 'sent_text'] of 'CommentRecord'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L141): OoadClass `AlignmentFailure`: Class 'AlignmentFailure' copies the fields ['_file', '_kind', '_message'] of 'AlignmentGap'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L167): OoadClass `AlignedFile`: Class 'AlignedFile' copies the fields ['_file', '_format', '_source'] of 'AlignmentGap'. Use one canonical model type.

### `hide-inner-details`

Rule text: [clean_engineering/clean_engineering.md:234](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L234)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/imported_classes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\imported_classes.py#L27): Operation `resolve`: Operation 'resolve' reaches into a collaborator's private state.

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:244](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L244)

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:327](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L327)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L174): Operation `renderComparePage`: Operation 'renderComparePage' is 29 statements (max 20).
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-graph.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-graph.ts#L97): Operation `read`: Operation 'read' is 22 statements (max 20).
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L130): Operation `_seed_project`: Operation '_seed_project' is 24 statements (max 20).

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:328](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L328)

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_file.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_file.py#L123): Operation `_scope_of`: Operation '_scope_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\drawio\drawio_bounded_context_map.py#L52): Operation `name_from_modules_title`: Operation 'name_from_modules_title' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/drawio/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\drawio\nodes.py#L312): Operation `_corner`: Operation '_corner' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L211): Operation `on_another_project`: Operation 'on_another_project' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L220): Operation `in_a_plain_folder`: Operation 'in_a_plain_folder' is a classmethod; prefer an instance operation.

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L242)

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L174): Operation `renderComparePage`: Operation 'renderComparePage' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L252): Operation `previousRunOf`: Operation 'previousRunOf' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L271): Operation `checkedRows`: Operation 'checkedRows' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L294): Operation `readRows`: Operation 'readRows' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L28): Operation `baselineOf`: Operation 'baselineOf' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L50): Operation `reviewOf`: Operation 'reviewOf' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L74): Operation `judgeStep`: Operation 'judgeStep' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [scripts/install.py](C:\dev\abd-cdd-release-1-2-fixes\scripts\install.py#L20): Operation `main`: Operation 'main' mixes I/O-style calls with domain calculation; split responsibilities.

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:330](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L330)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L194): Operation `_brace_end`: Operation '_brace_end' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/call_links.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\call_links.py#L109): Operation `_imports_of`: Operation '_imports_of' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/source_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\source_facts.py#L108): Operation `constructor_fields`: Operation 'constructor_fields' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_recording.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_recording.py#L253): Operation `_align`: Operation '_align' nests control flow 5 levels deep (max 3).

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:246](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L246)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L337): Operation `open_callout_on`: Operation 'open_callout_on' raises on an empty or missing value; return a quiet result instead.

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:332](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L332)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

**Graph violations:** 43

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1081): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1081): Parameter `y`: Parameter 'y' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1090): Parameter `dx`: Parameter 'dx' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1090): Parameter `dy`: Parameter 'dy' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1091): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1091): Parameter `y`: Parameter 'y' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/.context/drawio-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\drawio\.context\drawio-model.md#L47): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/modelled_areas.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\modelled_areas.py#L125): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/view/reshaped_view.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\view\reshaped_view.py#L169): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `fn`: Parameter 'fn' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L299): Parameter `by`: Parameter 'by' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L436): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L775): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L62): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L67): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L81): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L87): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L102): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L110): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L124): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L133): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L189): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/icon-button-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\icon-button-view.tsx#L87): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L284): Parameter `to`: Parameter 'to' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L292): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L441): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L460): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L643): Parameter `to`: Parameter 'to' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L667): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L83): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L136): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L147): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L170): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L191): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L260): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L276): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L297): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L311): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L340): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L362): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L208): Parameter `to`: Parameter 'to' does not reveal intent.

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:260](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L260)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:337](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L337)

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L163): Operation `blockGrey`: Operation 'blockGrey' uses the unnamed number 0.299.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L393): Operation `halfSize`: Operation 'halfSize' uses the unnamed number 255.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L426): Operation `placeOf`: Operation 'placeOf' uses the unnamed number 0.8.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-page-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-page-view.tsx#L303): Operation `WhiteboardFileView`: Operation 'WhiteboardFileView' uses the unnamed number 18.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L228): Operation `_wait_for`: Operation '_wait_for' uses the unnamed number 0.25.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L247): Operation `open`: Operation 'open' uses the unnamed number 1600.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L350): Operation `settled`: Operation 'settled' uses the unnamed number 0.1.

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:261](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L261)

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L62): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L79): Operation `check`: Operation 'check' nearly duplicates 'check' (cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py): 82% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L136): Operation `web_path_literals`: Operation 'web_path_literals' nearly duplicates 'web_path_literals' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 76% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L205): Operation `_in_import`: Operation '_in_import' nearly duplicates '_in_import' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 73% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L211): Operation `_in_comment`: Operation '_in_comment' nearly duplicates '_in_comment' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 75% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L283): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/class_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\class_facts.py#L278): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/class_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\class_facts.py#L325): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_exposure.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\module_exposure.py#L99): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/operation_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\operation_facts.py#L81): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/modelled_areas.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\modelled_areas.py#L98): Operation `_step_body`: Operation '_step_body' duplicates the body of '_step_body'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/typescript/typescript_story_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\typescript\typescript_story_model.py#L19): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/source-of-file.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\source-of-file.ts#L38): Operation `saidBy`: Operation 'saidBy' duplicates the body of 'saidBy'.

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:339](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L339)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:342](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L342)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L945): Operation `_lane_reply`: Operation '_lane_reply' catches every exception (a bare except, or except Exception that never re-raises).

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:343](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L343)

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L762): Operation `setMode`: Operation 'setMode' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-graph.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-graph.ts#L97): Operation `read`: Operation 'read' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-page.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-page.ts#L307): Operation `readBeside`: Operation 'readBeside' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-theme.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-theme.ts#L142): Operation `storedWrap`: Operation 'storedWrap' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L945): Operation `_lane_reply`: Operation '_lane_reply' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L144): Operation `changeQueue`: Operation 'changeQueue' swallows a caught failure or hands back a fallback in its place.

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:249](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L249)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L217): OoadClass `TicketEnding`: Class 'TicketEnding' has a descriptive comment; use invariants only.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L236): Operation `close`: Operation 'close' has a descriptive comment.

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:345](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L345)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:167](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L167)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:168](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L168)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:169](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L169)

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:170](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L170)

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

**Graph violations:** 21

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L418): OoadClass `Relationship`: Class 'Relationship' copies the fields ['cardinality', 'description', 'kind', 'sequential_order', 'target'] of 'Relationship'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L732): OoadClass `CodeSpelling`: Class 'CodeSpelling' copies the fields ['base_constructor', 'base_receiver', 'camel_case', 'construct', 'receiver', 'statement_end'] of 'CodeSpelling'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L745): OoadClass `CodeLanguage`: Class 'CodeLanguage' copies the fields ['indent', 'line_comment', 'name', 'suffixes', 'unfinished'] of 'CodeLanguage'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L831): OoadClass `CallGraphEntry`: Class 'CallGraphEntry' copies the fields ['depth', 'kind', 'text'] of 'CallGraphEntry'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/call_links.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\call_links.py#L120): OoadClass `ClassLinks`: Class 'ClassLinks' copies the fields ['_graph', '_in_graph', '_reach'] of 'ClassNodes'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/diagram/geometry.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\diagram\geometry.py#L11): OoadClass `Geometry`: Class 'Geometry' copies the fields ['height', 'width', 'x', 'y'] of 'Geometry'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\markdown\markdown_class_model.py#L358): OoadClass `MarkdownModule`: Class 'MarkdownModule' holds '_card_name', a name copy of a 'Card'; hold the Card itself.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/script_imports.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\script_imports.py#L122): OoadClass `PythonImports`: Class 'PythonImports' copies the fields ['_package', '_qualified', '_text'] of 'ScriptImportClauses'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/.context/ddd-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\.context\ddd-model.md#L331): OoadClass `MarkdownBoundedContext`: Class 'MarkdownBoundedContext' copies the fields ['group_notes', 'module_notes', 'notes'] of 'MarkdownBoundedContext'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/modelled_areas.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\modelled_areas.py#L33): OoadClass `ExampleObservations`: Class 'ExampleObservations' copies the fields ['graph', 'stories', 'tree'] of 'StoryLinks'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): OoadClass `ExpansionResult                                                <!-- Md -->`: Class 'ExpansionResult                                                <!-- Md -->' copies the fields ['instructions', 'result', 'tools'] of 'ExpansionResult'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/failure-fixes.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\failure-fixes.ts#L33): OoadClass `FailureFixes`: Class 'FailureFixes' copies the fields ['api', 'chat', 'store'] of 'FilesNotices'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_formats.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_formats.py#L43): OoadClass `Reshaped`: Class 'Reshaped' copies the fields ['added', 'changed', 'kept'] of '_FileEdit'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/guidance/practice_reading.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\practice_reading.py#L57): OoadClass `PracticeReading`: Class 'PracticeReading' copies the fields ['anchor_types', 'class_node_type', 'class_types', 'graph', 'in_graph', 'member_types', 'node_types', 'reads_after', 'rule_types', 'source_ordered_types'] of 'PracticeReading'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/guidance/schema.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\schema.py#L32): OoadClass `SchemaType`: Class 'SchemaType' copies the fields ['fields', 'key', 'rules'] of 'SchemaType'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_daemon.py](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_daemon.py#L93): OoadClass `HookDaemonIdentity`: Class 'HookDaemonIdentity' copies the fields ['pid', 'repo', 'stamp'] of 'HookDaemonAddress                                              <!-- Md -->'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [harness/hooks/hook_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\hook_server.py#L188): OoadClass `HookMessages`: Class 'HookMessages' copies the fields ['additional_context', 'agent_message', 'followup_message', 'toast', 'user_message'] of 'HookResult                                                     <!-- Md -->'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L694): OoadClass `StageWork`: Class 'StageWork' copies the fields ['action_states', 'allowed_actions', 'commands', 'has_violations', 'stage', 'violation_count'] of 'FidelityProgress'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/session/file_comments.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\file_comments.py#L55): OoadClass `CommentSending`: Class 'CommentSending' copies the fields ['chat', 'message', 'sent_text'] of 'CommentRecord'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L141): OoadClass `AlignmentFailure`: Class 'AlignmentFailure' copies the fields ['_file', '_kind', '_message'] of 'AlignmentGap'. Use one canonical model type.
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L167): OoadClass `AlignedFile`: Class 'AlignedFile' copies the fields ['_file', '_format', '_source'] of 'AlignmentGap'. Use one canonical model type.

### `hide-inner-details`

Rule text: [clean_engineering/clean_engineering.md:234](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L234)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/imported_classes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\imported_classes.py#L27): Operation `resolve`: Operation 'resolve' reaches into a collaborator's private state.

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:244](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L244)

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:327](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L327)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L174): Operation `renderComparePage`: Operation 'renderComparePage' is 29 statements (max 20).
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-graph.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-graph.ts#L97): Operation `read`: Operation 'read' is 22 statements (max 20).
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L130): Operation `_seed_project`: Operation '_seed_project' is 24 statements (max 20).

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:328](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L328)

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_file.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_file.py#L123): Operation `_scope_of`: Operation '_scope_of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/drawio/drawio_bounded_context_map.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\drawio\drawio_bounded_context_map.py#L52): Operation `name_from_modules_title`: Operation 'name_from_modules_title' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/drawio/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\drawio\nodes.py#L312): Operation `_corner`: Operation '_corner' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L211): Operation `on_another_project`: Operation 'on_another_project' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L220): Operation `in_a_plain_folder`: Operation 'in_a_plain_folder' is a classmethod; prefer an instance operation.

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L242)

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L174): Operation `renderComparePage`: Operation 'renderComparePage' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L252): Operation `previousRunOf`: Operation 'previousRunOf' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L271): Operation `checkedRows`: Operation 'checkedRows' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L294): Operation `readRows`: Operation 'readRows' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L28): Operation `baselineOf`: Operation 'baselineOf' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L50): Operation `reviewOf`: Operation 'reviewOf' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L74): Operation `judgeStep`: Operation 'judgeStep' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [scripts/install.py](C:\dev\abd-cdd-release-1-2-fixes\scripts\install.py#L20): Operation `main`: Operation 'main' mixes I/O-style calls with domain calculation; split responsibilities.

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:330](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L330)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L194): Operation `_brace_end`: Operation '_brace_end' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/call_links.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\call_links.py#L109): Operation `_imports_of`: Operation '_imports_of' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/source_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\source_facts.py#L108): Operation `constructor_fields`: Operation 'constructor_fields' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_recording.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_recording.py#L253): Operation `_align`: Operation '_align' nests control flow 5 levels deep (max 3).

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:246](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L246)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L337): Operation `open_callout_on`: Operation 'open_callout_on' raises on an empty or missing value; return a quiet result instead.

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:332](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L332)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

**Graph violations:** 43

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1081): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1081): Parameter `y`: Parameter 'y' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1090): Parameter `dx`: Parameter 'dx' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1090): Parameter `dy`: Parameter 'dy' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1091): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1091): Parameter `y`: Parameter 'y' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/.context/drawio-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\drawio\.context\drawio-model.md#L47): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/modelled_areas.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\modelled_areas.py#L125): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/view/reshaped_view.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\view\reshaped_view.py#L169): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `fn`: Parameter 'fn' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L299): Parameter `by`: Parameter 'by' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L436): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L775): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L62): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L67): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L81): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L87): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L102): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L110): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L124): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L133): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L189): Parameter `at`: Parameter 'at' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/icon-button-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\icon-button-view.tsx#L87): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L284): Parameter `to`: Parameter 'to' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L292): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L441): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L460): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L643): Parameter `to`: Parameter 'to' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L667): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L83): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L136): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L147): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L170): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L191): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L260): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L276): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L297): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L311): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L340): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L362): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L208): Parameter `to`: Parameter 'to' does not reveal intent.

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:260](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L260)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:337](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L337)

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L163): Operation `blockGrey`: Operation 'blockGrey' uses the unnamed number 0.299.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L393): Operation `halfSize`: Operation 'halfSize' uses the unnamed number 255.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L426): Operation `placeOf`: Operation 'placeOf' uses the unnamed number 0.8.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-page-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-page-view.tsx#L303): Operation `WhiteboardFileView`: Operation 'WhiteboardFileView' uses the unnamed number 18.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L228): Operation `_wait_for`: Operation '_wait_for' uses the unnamed number 0.25.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L247): Operation `open`: Operation 'open' uses the unnamed number 1600.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L350): Operation `settled`: Operation 'settled' uses the unnamed number 0.1.

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:261](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L261)

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L62): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/practices/ddd/rules/oss_tier_rules.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\practices\ddd\rules\oss_tier_rules.py#L79): Operation `check`: Operation 'check' nearly duplicates 'check' (cdd_guidance/patterns/lern_domain_driven/practices/ddd/rules/lern_tier_rules.py): 82% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L136): Operation `web_path_literals`: Operation 'web_path_literals' nearly duplicates 'web_path_literals' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 76% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L205): Operation `_in_import`: Operation '_in_import' nearly duplicates '_in_import' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 73% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L211): Operation `_in_comment`: Operation '_in_comment' nearly duplicates '_in_comment' (cdd_guidance/patterns/lern_domain_driven/tier_facts.py): 75% of their code is the same. Give the shared logic one function.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/tier_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\tier_facts.py#L283): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/class_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\class_facts.py#L278): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/class_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\class_facts.py#L325): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/module_exposure.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\module_exposure.py#L99): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/operation_facts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\operation_facts.py#L81): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/modelled_areas.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\modelled_areas.py#L98): Operation `_step_body`: Operation '_step_body' duplicates the body of '_step_body'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/typescript/typescript_story_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\typescript\typescript_story_model.py#L19): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/source-of-file.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\source-of-file.ts#L38): Operation `saidBy`: Operation 'saidBy' duplicates the body of 'saidBy'.

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:339](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L339)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:342](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L342)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L945): Operation `_lane_reply`: Operation '_lane_reply' catches every exception (a bare except, or except Exception that never re-raises).

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:343](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L343)

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L762): Operation `setMode`: Operation 'setMode' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-graph.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-graph.ts#L97): Operation `read`: Operation 'read' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-page.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-page.ts#L307): Operation `readBeside`: Operation 'readBeside' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-theme.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-theme.ts#L142): Operation `storedWrap`: Operation 'storedWrap' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L945): Operation `_lane_reply`: Operation '_lane_reply' swallows a caught failure or hands back a fallback in its place.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L144): Operation `changeQueue`: Operation 'changeQueue' swallows a caught failure or hands back a fallback in its place.

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:249](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L249)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L217): OoadClass `TicketEnding`: Class 'TicketEnding' has a descriptive comment; use invariants only.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L236): Operation `close`: Operation 'close' has a descriptive comment.

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:345](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L345)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:167](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L167)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:168](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L168)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:169](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L169)

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:170](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L170)

### `avoid-vague-parameter-names`

Rule text: [clean_engineering/clean_engineering.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L245)

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/mcp/server_lanes.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\server_lanes.py#L43): Operation `from_data`: Parameter 'data' in 'from_data' is vague.
- [X] **ERROR** **[graph rule]** - [harness/mcp/server_lanes.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\server_lanes.py#L43): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L295): Operation `attach`: Parameter 'data' in 'attach' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L295): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L324): Operation `_saved_attachment`: Parameter 'data' in '_saved_attachment' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L324): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.

### `deep-module`

Rule text: [clean_engineering/clean_engineering.md:135](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L135)

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/annotations](C:\dev\abd-cdd-release-1-2-fixes\harness\annotations#L1): Module `annotations`: Module 'annotations' exposes 18 of its 51 methods to other modules, more than the 17 that 35% allows; they are the public methods of its 5 public classes of 15: Annotation, Destination, NamesAnnotation, ClassRegistry, Name. Hide more behind fewer public methods.
- [X] **ERROR** **[graph rule]** - [harness/chat](C:\dev\abd-cdd-release-1-2-fixes\harness\chat#L1): Module `chat`: Module 'chat' exposes 27 of its 66 methods to other modules, more than the 23 that 35% allows; they are the public methods of its 5 public classes of 13: Chat, ChatCommand, ChatLinks, ChatMessage, Chats. Hide more behind fewer public methods.
- [X] **ERROR** **[graph rule]** - [harness/design_canvas](C:\dev\abd-cdd-release-1-2-fixes\harness\design_canvas#L1): Module `design_canvas`: Module 'design_canvas' exposes 24 of its 38 methods to other modules, more than the 13 that 35% allows; they are the public methods of its 4 public classes of 10: Artboard, DesignCanvas, Place, CanvasVersions. Hide more behind fewer public methods.
- [X] **ERROR** **[graph rule]** - [harness/guidance](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance#L1): Module `guidance`: Module 'guidance' exposes 185 of its 440 methods to other modules, more than the 154 that 35% allows; they are the public methods of its 20 public classes of 72: Action, DeclaredFile, DeclaredOutputs, FidelityGuidance, Guidance, GuidanceCollection, PracticeGuidance, SketchLens, PracticeSet, UnknownPractice, PracticeFormats, RenderRequest, Reshaped, PracticeReading, PracticeSupplement, Rule, RulesCollection, Schema, ApproachStage, StageScope. Hide more behind fewer public methods.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance_actions#L1): Module `guidance_actions`: Module 'guidance_actions' exposes 32 of its 84 methods to other modules, more than the 29 that 35% allows; they are the public methods of its 5 public classes of 15: ActionSession, ActionWorksInNoSession, GuidanceAction, GuidanceCommand, WorkList. Hide more behind fewer public methods.
- [X] **ERROR** **[graph rule]** - [harness/markdown](C:\dev\abd-cdd-release-1-2-fixes\harness\markdown#L1): Module `markdown`: Module 'markdown' exposes 50 of its 136 methods to other modules, more than the 47 that 35% allows; they are the public methods of its 6 public classes of 20: Format, FrontMatter, Markdown, MarkdownCollection, MarkdownScope, MarkdownText. Hide more behind fewer public methods.
- [X] **ERROR** **[graph rule]** - [harness/whiteboard](C:\dev\abd-cdd-release-1-2-fixes\harness\whiteboard#L1): Module `whiteboard`: Module 'whiteboard' exposes 36 of its 54 methods to other modules, more than the 18 that 35% allows; they are the public methods of its 6 public classes of 13: BoardElement, BoardLinks, Box, UnreadableBoard, Whiteboard, WhiteboardNode. Hide more behind fewer public methods.

### `keep-classes-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:231](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L231)

**Graph violations:** 19

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L304): OoadClass `SourceText`: Class 'SourceText' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L435): OoadClass `ModuleContext`: Class 'ModuleContext' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/.context/drawio-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\drawio\.context\drawio-model.md#L140): OoadClass `DrawioScanner`: Class 'DrawioScanner' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\markdown\nodes.py#L141): OoadClass `MarkdownAggregate`: Class 'MarkdownAggregate' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/ux_map.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\ux_map.py#L32): OoadClass `UxMap`: Class 'UxMap' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-graph.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-graph.ts#L59): OoadClass `FilesGraph`: Class 'FilesGraph' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L341): OoadClass `Filter`: Class 'Filter' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L991): OoadClass `_HeldNodes`: Class '_HeldNodes' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L1514): OoadClass `Graph`: Class 'Graph' exposes 18 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L187): OoadClass `PracticeFormats`: Class 'PracticeFormats' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L535): OoadClass `FidelityGuidance`: Class 'FidelityGuidance' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/mcp/cdd_home.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\cdd_home.py#L81): OoadClass `CddHome`: Class 'CddHome' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L330): OoadClass `Ticket`: Class 'Ticket' exposes 23 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L739): OoadClass `BacklogItem`: Class 'BacklogItem' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/app/src/kanban/ticket/files-panel-client.ts](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\app\src\kanban\ticket\files-panel-client.ts#L45): OoadClass `FilesPanelClient`: Class 'FilesPanelClient' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L898): OoadClass `FidelityProgress`: Class 'FidelityProgress' exposes 12 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/practice_session_output.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L41): OoadClass `PracticeSessionOutput`: Class 'PracticeSessionOutput' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session_files.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_files.py#L31): OoadClass `SessionFiles`: Class 'SessionFiles' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L120): OoadClass `PromptQueue`: Class 'PromptQueue' exposes 17 public operations (budget ~9). Split responsibilities.

### `limit-operation-parameters`

Rule text: [clean_engineering/clean_engineering.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L243)

**Graph violations:** 90

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\render.py#L69): Operation `_render_files`: Operation '_render_files' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\render.py#L86): Operation `_saved_by_declared_paths`: Operation '_saved_by_declared_paths' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\render.py#L109): Operation `_saved_code`: Operation '_saved_code' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_code.py#L87): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_code.py#L99): Operation `__init__`: Operation '__init__' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/reshaped_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\reshaped_code.py#L67): Operation `__init__`: Operation '__init__' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/reshaped_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\reshaped_code.py#L123): Operation `_python_member`: Operation '_python_member' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/desktop_walk/desktop_walk.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\desktop_walk\desktop_walk.py#L55): Operation `__init__`: Operation '__init__' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/desktop_walk/desktop_walk.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\desktop_walk\desktop_walk.py#L177): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L140): Operation `_tier_facts`: Operation '_tier_facts' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/oss_portal_domain_driven/graph_overlay.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\oss_portal_domain_driven\graph_overlay.py#L195): Operation `_file_node`: Operation '_file_node' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_reshape.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\spec_reshape.py#L36): Operation `__init__`: Operation '__init__' takes 6 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_reshape.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\spec_reshape.py#L62): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_reshape.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\spec_reshape.py#L161): Operation `_written_in`: Operation '_written_in' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L422): Operation `Relationship`: Operation 'Relationship' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L660): Operation `ClassHeading`: Operation 'ClassHeading' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L736): Operation `CodeSpelling`: Operation 'CodeSpelling' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L749): Operation `CodeLanguage`: Operation 'CodeLanguage' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1081): Operation `Geometry`: Operation 'Geometry' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1097): Operation `DiagramArrow`: Operation 'DiagramArrow' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L1129): Operation `ArrowRouter`: Operation 'ArrowRouter' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/diagram/diagram_node.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\diagram\diagram_node.py#L90): Operation `take_arrow`: Operation 'take_arrow' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/whiteboard/whiteboard_class_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\whiteboard\whiteboard_class_model.py#L514): Operation `_arrow_element`: Operation '_arrow_element' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/operation_checks.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\rules\operation_checks.py#L359): Operation `_near_copy_message`: Operation '_near_copy_message' takes 4 parameters (maximum 3, excluding self). A packed tuple or *args counts each value it carries.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\graph_reading.py#L512): Operation `_link_sides`: Operation '_link_sides' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\graph_reading.py#L551): Operation `add`: Operation 'add' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\graph_reading.py#L629): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\graph_reading.py#L703): Operation `_read_block`: Operation '_read_block' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\graph_reading.py#L745): Operation `_read_mapping`: Operation '_read_mapping' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\nodes.py#L290): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L146): Operation `Increment`: Operation 'Increment' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\code_story_model.py#L498): Operation `_write_epic`: Operation '_write_epic' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/code_story_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\code_story_model.py#L646): Operation `_take_stories`: Operation '_take_stories' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/scenario_parts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\markdown\scenario_parts.py#L28): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/markdown/scenario_parts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\markdown\scenario_parts.py#L152): Operation `heading`: Operation 'heading' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/python/shared_story_file.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\python\shared_story_file.py#L41): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/story_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\story_model.py#L155): Operation `_load_child_band`: Operation '_load_child_band' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L212): Operation `AgentInstructions`: Operation 'AgentInstructions' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/app.py](C:\dev\abd-cdd-release-1-2-fixes\harness\diagnostics\app.py#L144): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L134): Operation `add_walked_step`: Operation 'add_walked_step' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L200): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L327): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L371): Operation `_start_in_background`: Operation '_start_in_background' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L411): Operation `renderShot`: Operation 'renderShot' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L436): Operation `check`: Operation 'check' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L56): Operation `recordVerdict`: Operation 'recordVerdict' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/review.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\review.ts#L74): Operation `judgeStep`: Operation 'judgeStep' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/failure-fixes.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\failure-fixes.ts#L44): Operation `show`: Operation 'show' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/file-source-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\file-source-view.tsx#L36): Operation `useMembersFolded`: Operation 'useMembersFolded' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/source-of-file.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\source-of-file.ts#L79): Operation `lineUsing`: Operation 'lineUsing' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L18): Operation `constructor`: Operation 'constructor' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\SourceView.tsx#L143): Operation `useSourceCallouts`: Operation 'useSourceCallouts' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\SourceView.tsx#L157): Operation `useLineMarks`: Operation 'useLineMarks' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L95): Operation `calloutsIn`: Operation 'calloutsIn' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L102): Operation `calloutsOn`: Operation 'calloutsOn' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/source-callouts.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\source-callouts.ts#L144): Operation `calloutsBlock`: Operation 'calloutsBlock' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/source-callouts.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\source-callouts.ts#L156): Operation `calloutSection`: Operation 'calloutSection' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/source-callouts.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\source-callouts.ts#L234): Operation `calloutRow`: Operation 'calloutRow' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L236): Operation `align_to_declaration`: Operation 'align_to_declaration' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L55): Operation `render`: Operation 'render' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L833): Operation `render_files`: Operation 'render_files' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/guidance/guidance.py](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\guidance.py#L840): Operation `files_to_render`: Operation 'files_to_render' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Operation `HookDaemonAddress`: Operation 'HookDaemonAddress' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Operation `HookResult`: Operation 'HookResult' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L60): Operation `HookInstallation`: Operation 'HookInstallation' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_server.py#L695): Operation `_call_sent`: Operation '_call_sent' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/mcp/server_lanes.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\server_lanes.py#L32): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/mcp/server_lanes.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\server_lanes.py#L55): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L624): Operation `FidelityProgress`: Operation 'FidelityProgress' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L806): Operation `Help`: Operation 'Help' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L852): Operation `Report`: Operation 'Report' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\ticket.py#L1130): Operation `_shown_as`: Operation '_shown_as' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L72): Operation `__init__`: Operation '__init__' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L171): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L414): Operation `_read`: Operation '_read' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L426): Operation `_compared`: Operation '_compared' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/format_alignment.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\format_alignment.py#L443): Operation `_lacks`: Operation '_lacks' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/practice_session_output.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\practice_session_output.py#L559): Operation `_declared_files`: Operation '_declared_files' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session_file.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\session_file.py#L247): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/violation_history.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\violation_history.py#L301): Operation `_matching`: Operation '_matching' takes 4 parameters (maximum 3, excluding self). A packed tuple or *args counts each value it carries.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/icon-button-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\icon-button-view.tsx#L37): Operation `TipView`: Operation 'TipView' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L643): Operation `moveStep`: Operation 'moveStep' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L147): Operation `CardsView`: Operation 'CardsView' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L191): Operation `CardView`: Operation 'CardView' takes 6 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L260): Operation `CardButtonsView`: Operation 'CardButtonsView' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L297): Operation `AgentQueueView`: Operation 'AgentQueueView' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L311): Operation `AgentRobotView`: Operation 'AgentRobotView' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\queue-view.tsx#L362): Operation `StepView`: Operation 'StepView' takes 6 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L108): Operation `__init__`: Operation '__init__' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/prompt_queue.py](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\prompt_queue.py#L324): Operation `_saved_attachment`: Operation '_saved_attachment' takes 5 parameters (maximum 3, excluding self).

### `missing-module-context`

Rule text: a graph rule, written in no practice document

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L1): OoadClass `_module`: Module folder 'review-generated-work-in-file-viewer' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L182): OoadClass `FilesStack`: Module folder 'review-generated-work-in-file-viewer' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

### `one-way-deps`

Rule text: [clean_engineering/clean_engineering.md:147](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L147)

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model#L1): Package `model`: Circular import: 'model' imports 'markdown', which imports back into 'model' through a cycle of 2 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/markdown](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\markdown#L1): Package `markdown`: Circular import: 'markdown' imports 'model', which imports back into 'markdown' through a cycle of 2 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model#L1): Package `model`: Circular import: 'model' imports 'markdown', which imports back into 'model' through a cycle of 2 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ddd/model/markdown](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ddd\model\markdown#L1): Package `markdown`: Circular import: 'markdown' imports 'model', which imports back into 'markdown' through a cycle of 2 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model#L1): Package `model`: Circular import: 'model' imports 'drawio', which imports back into 'model' through a cycle of 4 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model#L1): Package `model`: Circular import: 'model' imports 'html', which imports back into 'model' through a cycle of 4 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/drawio](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\drawio#L1): Package `drawio`: Circular import: 'drawio' imports 'model', which imports back into 'drawio' through a cycle of 4 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/html](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\html#L1): Package `html`: Circular import: 'html' imports 'model', which imports back into 'html' through a cycle of 4 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/html](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\html#L1): Package `html`: Circular import: 'html' imports 'json', which imports back into 'html' through a cycle of 4 modules; dependencies must flow one way.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/json](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\json#L1): Package `json`: Circular import: 'json' imports 'model', which imports back into 'json' through a cycle of 4 modules; dependencies must flow one way.

### `prefer-class-operations`

Rule text: [clean_engineering/clean_engineering.md:236](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L236)

**Graph violations:** 18

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_code.py#L76): OoadClass `RenderedCode`: Module function '_says_where_name_ends' (line 76) is only used from 'RenderedCode'. Move it onto 'RenderedCode' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/patterns/lern_domain_driven/graph_overlay.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\patterns\lern_domain_driven\graph_overlay.py#L246): OoadClass `_LernReading`: Module function '_record_screen_stories' (line 246) is only used from '_LernReading'. Move it onto '_LernReading' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/call_links.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\call_links.py#L48): OoadClass `ClassesInReach`: Module function '_language_of' (line 48) is only used from 'ClassesInReach'. Move it onto 'ClassesInReach' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/code_class_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\code_class_model.py#L44): OoadClass `CodeCleanEngineeringModel`: Module function '_without_note' (line 44) is only used from 'CodeCleanEngineeringModel'. Move it onto 'CodeCleanEngineeringModel' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/diagram/diagram_node.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\diagram\diagram_node.py#L62): OoadClass `DiagramClass`: Module function '_names_in' (line 62) is only used from 'DiagramClass'. Move it onto 'DiagramClass' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/drawio/drawio_class_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\drawio\drawio_class_model.py#L550): OoadClass `_ClassDiagramReader`: Module function '_folded_classes' (line 550) is only used from '_ClassDiagramReader'. Move it onto '_ClassDiagramReader' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\rules\practice_wide_rules.py#L165): OoadClass `OneWayDeps`: Module function '_folders' (line 165) is only used from 'OneWayDeps'. Move it onto 'OneWayDeps' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/drawio/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\drawio\nodes.py#L314): OoadClass `_KeptPlaces`: Module function '_drawn_geometries' (line 314) is only used from '_KeptPlaces'. Move it onto '_KeptPlaces' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/story_link.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\story_link.py#L204): OoadClass `StoryTargets`: Module function '_ancestor' (line 204) is only used from 'StoryTargets'. Move it onto 'StoryTargets' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/story_link.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\story_link.py#L211): OoadClass `StoryTargets`: Module function '_parent' (line 211) is only used from 'StoryTargets'. Move it onto 'StoryTargets' as a method.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/ux_map.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\ux_map.py#L279): OoadClass `UxMap`: Module function '_name_of' (line 279) is only used from 'UxMap'. Move it onto 'UxMap' as a method.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/e2e_review.py](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\e2e_review.py#L367): OoadClass `E2eReview`: Module function '_stamp' (line 367) is only used from 'E2eReview'. Move it onto 'E2eReview' as a method.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L57): OoadClass `PracticeLoading`: Module function '_under_any' (line 57) is only used from 'PracticeLoading'. Move it onto 'PracticeLoading' as a method.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\graph.py#L62): OoadClass `Source`: Module function '_decorated_end' (line 62) is only used from 'Source'. Move it onto 'Source' as a method.
- [X] **ERROR** **[graph rule]** - [space/session/proposed_roots.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\proposed_roots.py#L131): OoadClass `ProposedRoots`: Module function '_fixed_head' (line 131) is only used from 'ProposedRoots'. Move it onto 'ProposedRoots' as a method.
- [X] **ERROR** **[graph rule]** - [space/session/proposed_roots.py](C:\dev\abd-cdd-release-1-2-fixes\space\session\proposed_roots.py#L137): OoadClass `ProposedRoots`: Module function '_squashed' (line 137) is only used from 'ProposedRoots'. Move it onto 'ProposedRoots' as a method.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L115): OoadClass `FilesStack`: Module function '_free_port' (line 115) is only used from 'FilesStack'. Move it onto 'FilesStack' as a method.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L125): OoadClass `FilesStack`: Module function '_write' (line 125) is only used from 'FilesStack'. Move it onto 'FilesStack' as a method.

### `shape-classes-around-resources`

Rule text: [clean_engineering/clean_engineering.md:232](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L232)

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/app/story-map/story-map-client.ts](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\app\story-map\story-map-client.ts#L23): OoadClass `StoryMapClient`: Class 'StoryMapClient' acts on the data bag 'Edit', which holds the state but no behavior; put the behavior on the resource that owns the data.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/brace_story.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\brace_story.py#L114): OoadClass `BraceStoryWriting`: Class 'BraceStoryWriting' acts on the data bag 'StoryFilePlace', which holds the state but no behavior; put the behavior on the resource that owns the data.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\graph_reading.py#L55): OoadClass `StoriesReading`: Class 'StoriesReading' acts on the data bag 'ScriptStoryModel', which holds the state but no behavior; put the behavior on the resource that owns the data.

### `state-change-returns-record-or-named-failure`

Rule text: [clean_engineering/clean_engineering.md:247](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L247)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-fold-keys.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-fold-keys.ts#L52): Operation `read`: Operation 'read' mutates state but does not return the record or a named failure.

### `use-explicit-dependencies`

Rule text: [clean_engineering/clean_engineering.md:237](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L237)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [cdd_guidance/desktop_walk/desktop_walk.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\desktop_walk\desktop_walk.py#L173): OoadClass `DesktopWalk`: Class 'DesktopWalk' constructs 'NewRepository' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\graph_reading.py#L108): OoadClass `ObservationLinks`: Class 'ObservationLinks' constructs 'ImportedClasses' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/story-demo/mount-generated-mockup.js](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\story-demo\mount-generated-mockup.js#L527): OoadClass `GeneratedMockup`: Class 'GeneratedMockup' constructs 'ExplorerPanel' inside its constructor.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L182): OoadClass `FilesStack`: Class 'FilesStack' constructs 'SpecServer' inside its constructor.

### `use-typed-signatures`

Rule text: [clean_engineering/clean_engineering.md:140](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L140)

**Graph violations:** 113

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/kept_document.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\kept_document.py#L87): Parameter `drawn`: Parameter 'drawn' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/kept_document.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\kept_document.py#L87): Parameter `held`: Parameter 'held' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/render.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\render.py#L105): Parameter `result`: Parameter 'result' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_code.py#L115): Parameter `rendered`: Parameter 'rendered' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_code.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_code.py#L147): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/render/rendered_file.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\actions\render\rendered_file.py#L135): Parameter `rendered`: Parameter 'rendered' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_reshape.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\spec_reshape.py#L110): Parameter `calls`: Parameter 'calls' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/spec_reshape.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\spec_reshape.py#L113): Parameter `call`: Parameter 'call' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L687): Parameter `record`: Parameter 'record' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L695): Parameter `record`: Parameter 'record' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L707): Parameter `record`: Parameter 'record' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L713): Parameter `record`: Parameter 'record' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\.context\ooad-model.md#L719): Parameter `record`: Parameter 'record' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/code_class_model.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\code_class_model.py#L268): Parameter `member`: Parameter 'member' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/clean_engineering/model/operation_counts.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\clean_engineering\model\operation_counts.py#L35): Parameter `shape`: Parameter 'shape' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L69): Parameter `practice`: Parameter 'practice' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L405): Parameter `path`: Parameter 'path' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L449): Parameter `content`: Parameter 'content' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L532): Parameter `block`: Parameter 'block' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L544): Parameter `children`: Parameter 'children' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L560): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L560): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/model/.context/story-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\model\.context\story-model.md#L573): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/stories/stories_formats.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\stories\stories_formats.py#L55): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/.context/ux-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\.context\ux-model.md#L158): Parameter `name`: Parameter 'name' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/.context/ux-model.md](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\.context\ux-model.md#L158): Parameter `sequential_order`: Parameter 'sequential_order' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `arguments`: Parameter 'arguments' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `arguments`: Parameter 'arguments' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `collection`: Parameter 'collection' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `context`: Parameter 'context' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `instance`: Parameter 'instance' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `instance`: Parameter 'instance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `member`: Parameter 'member' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `name`: Parameter 'name' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `operation`: Parameter 'operation' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `return_type`: Parameter 'return_type' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L1): Parameter `roots`: Parameter 'roots' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/agent_tools/.context/agent-tools-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\agent_tools\.context\agent-tools-model.md#L212): Parameter `arguments`: Parameter 'arguments' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/diagnostics/desktop_walk_question.py](C:\dev\abd-cdd-release-1-2-fixes\harness\diagnostics\desktop_walk_question.py#L102): Parameter `asked`: Parameter 'asked' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L232): Parameter `under`: Parameter 'under' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L411): Parameter `caption`: Parameter 'caption' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L411): Parameter `from`: Parameter 'from' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L436): Parameter `title`: Parameter 'title' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L517): Parameter `withImages`: Parameter 'withImages' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L762): Parameter `mode`: Parameter 'mode' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L762): Parameter `persist`: Parameter 'persist' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L772): Parameter `open`: Parameter 'open' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/e2e_review/report/report.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\e2e_review\report\report.ts#L775): Parameter `id`: Parameter 'id' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/drawio-viewer.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\drawio-viewer.ts#L50): Parameter `project`: Parameter 'project' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/failure-fixes.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\failure-fixes.ts#L44): Parameter `isOnProblemLine`: Parameter 'isOnProblemLine' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-paths.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-paths.ts#L25): Parameter `project`: Parameter 'project' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-paths.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-paths.ts#L35): Parameter `port`: Parameter 'port' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/files-paths.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\files-paths.ts#L35): Parameter `project`: Parameter 'project' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/files_app/app/files/whiteboard-canvas.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\files_app\app\files\whiteboard-canvas.ts#L18): Parameter `problem`: Parameter 'problem' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): Parameter `call`: Parameter 'call' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): Parameter `force`: Parameter 'force' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L1): Parameter `overlays`: Parameter 'overlays' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L70): Parameter `message`: Parameter 'message' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L236): Parameter `seen`: Parameter 'seen' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L236): Parameter `stack`: Parameter 'stack' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L236): Parameter `via`: Parameter 'via' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L256): Parameter `child`: Parameter 'child' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L256): Parameter `kind`: Parameter 'kind' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L280): Parameter `kind`: Parameter 'kind' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L330): Parameter `name`: Parameter 'name' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L330): Parameter `root`: Parameter 'root' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L355): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L414): Parameter `node_type`: Parameter 'node_type' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L436): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L477): Parameter `violation`: Parameter 'violation' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L506): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/.context/graph-populate-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\.context\graph-populate-model.md#L506): Parameter `location`: Parameter 'location' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L88): Parameter `owner`: Parameter 'owner' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\app\source\call-expansion.ts#L95): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/pattern_overlays.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\pattern_overlays.py#L58): Parameter `node`: Parameter 'node' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\dev\abd-cdd-release-1-2-fixes\harness\graph\schema_rules.py#L70): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L15): Parameter `format`: Parameter 'format' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L42): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L55): Parameter `fidelity`: Parameter 'fidelity' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L55): Parameter `format`: Parameter 'format' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L146): Parameter `format`: Parameter 'format' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L187): Parameter `content`: Parameter 'content' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L187): Parameter `model`: Parameter 'model' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L187): Parameter `paths`: Parameter 'paths' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L187): Parameter `target`: Parameter 'target' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L256): Parameter `name`: Parameter 'name' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L256): Parameter `stage`: Parameter 'stage' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L358): Parameter `entries`: Parameter 'entries' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L358): Parameter `parent`: Parameter 'parent' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L358): Parameter `parent`: Parameter 'parent' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L379): Parameter `always_apply`: Parameter 'always_apply' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance/.context/practice-guidance-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\guidance\.context\practice-guidance-model.md#L379): Parameter `globs`: Parameter 'globs' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `additional_context`: Parameter 'additional_context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `agent_message`: Parameter 'agent_message' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `followup_message`: Parameter 'followup_message' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `hooks`: Parameter 'hooks' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `item`: Parameter 'item' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `toast`: Parameter 'toast' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `toolset`: Parameter 'toolset' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/hooks/.context/hooks-runtime-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\hooks\.context\hooks-runtime-model.md#L1): Parameter `user_message`: Parameter 'user_message' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/markdown/.context/markdown-collection-model.md](C:\dev\abd-cdd-release-1-2-fixes\harness\markdown\.context\markdown-collection-model.md#L19): Parameter `parent`: Parameter 'parent' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_address.py](C:\dev\abd-cdd-release-1-2-fixes\harness\mcp\mcp_address.py#L78): Parameter `lane_call`: Parameter 'lane_call' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [space/kanban/.context/kanban-model.md](C:\dev\abd-cdd-release-1-2-fixes\space\kanban\.context\kanban-model.md#L223): Parameter `values`: Parameter 'values' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L187): Parameter `seed`: Parameter 'seed' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L350): Parameter `is_settled`: Parameter 'is_settled' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/files_app_browser.py](C:\dev\abd-cdd-release-1-2-fixes\story_tests\review-generated-work-in-file-viewer\files_app_browser.py#L350): Parameter `read`: Parameter 'read' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/.context/prompt-notify-model.md](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_notify\.context\prompt-notify-model.md#L1): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/.context/prompt-notify-model.md](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_notify\.context\prompt-notify-model.md#L1): Parameter `raw`: Parameter 'raw' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/icon-button-view.tsx](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\icon-button-view.tsx#L49): Parameter `detail`: Parameter 'detail' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-release-1-2-fixes\tools\prompt_queue\hooks\queue\prompt-queue.ts#L407): Parameter `sentId`: Parameter 'sentId' is missing a type annotation.
