# Module: agent_bdd

**Purpose:** Drive real-agent BDD specs through a shared `agent(...)` harness that routes to CLI or in-chat execution, then assert on parsed `RunResponse` fields and AI-judged prose.

**Seam:** `agent`, `instruct`, `instruct_use_tool`, `ai_judge`; `spec_helpers` for shared YAML/prompt/assert helpers; generator `AgentBdd` for scaffolding agent specs that compose vanilla `Bdd`.

**Constraint:** Specs must call the free harness functions only inside `with agent(...)`. Never mock the harness or agent output. Do not import CLI/chat backends directly from specs — use the package seam. Prefer `spec_helpers` (`run_toolset`, `expect_ok_action`, …) over copying prompt/assert boilerplate.

## Public API

- `agent(workspace, session_file, *, in_chat=None)`
- `instruct(prompt, *, timeout_seconds=300) -> AgentResult`
- `instruct_use_tool(prompt, *, timeout_seconds=300) -> RunResponse`
- `ai_judge(output, rubric, *, timeout_seconds=180)`
- `AgentResult`, `RunResponse`, `JudgeResult`, `AgentSession`
- `AgentSpecManifest`, `AgentSpecRunbook`, `read_manifest`, `build_runbook`
- Spec helpers: `repo_root_from`, `sessions_dir`, `dump_run_yaml`, `tools_run_prompt`, `run_toolset`, `read_workspace`, `follow_instructions`, `manifest_command_from_header`, `run_manifest_from_header`, `expect_ok_action`, `expect_ok_tool`, `expect_tools_include`, `expect_tools_exclude`, `expect_instructions_contain`, `expect_instructions_contain_any`, `tools_run_captures`, `combined_capture_text`, `expect_capture_mentions`
- `AgentBdd` generator actions: `generate_output`, `validate`, `satisfy`, `repair`

**Dependencies:** `Bdd` / `BaseContextTool` (generator); cursor-agent CLI or in-chat inbox (harness backends); fenced YAML CLI envelope parsing.

**Mechanism:** Thread-local free functions delegate into the active harness block. Specs stay end-to-end — never mock the harness.
