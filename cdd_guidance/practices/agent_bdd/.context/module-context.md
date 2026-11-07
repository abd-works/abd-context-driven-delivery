# cdd_guidance/practices/agent_bdd
*Agent BDD* specs are mamba tests that drive a real agent and assert on what it actually did. Inside `with agent(workspace, session_file):`, `instruct(prompt)` gives the agent a natural-language step and returns an *AgentResult*; `instruct_use_tool(prompt)` runs a toolset request in-process and returns a parsed *RunResponse* to assert on; `ai_judge(output, rubric)` fails the spec when an AI judge finds the prose does not meet the rubric. The same block runs either through the agent CLI or in the chat, chosen by `AGENT_BDD_IN_CHAT` or the spec's manifest.

The spec helpers — such as `run_toolset`, `expect_ok_action`, `expect_tools_include`, `expect_instructions_contain`, and `generate_and_judge` — hold the request, assertion, and judging steps specs repeat. *AgentBdd* is the practice that writes these specs, layering the agent harness rules on BDD's test discipline (`agent-bdd.instructions`).

- **Purpose:** Test agent behaviour end to end against a real agent, so a spec fails when the agent would actually do the wrong thing.
- **Seam (terms):** AgentBdd, `agent`, `instruct`, `instruct_use_tool`, `ai_judge`, AgentResult, RunResponse, `agent-bdd.instructions`
- **Dependencies (one-way):** `cdd_guidance/practices/bdd` (*Bdd*), `cdd_guidance/actions` (*Generate*), `harness/guidance` (*PracticeGuidance*), `harness/agent_tools`, `harness/installation`, `harness/mcp` (spec server)

## Constraint

Call `instruct`, `instruct_use_tool`, and `ai_judge` only inside `with agent(...)`; outside it they raise `RuntimeError`. Never mock the harness or the agent's output. Import the harness from `agent_bdd`, never the CLI or chat implementation directly. Use the spec helpers instead of copying request and assertion code into each spec.
