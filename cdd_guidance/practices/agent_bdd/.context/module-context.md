# cdd_guidance/practices/agent_bdd
*Agent BDD* specs are mamba tests that drive a real agent and assert on what it actually did. `with agent(workspace, session_file) as run:` opens an *AgentBlock*: `run.instruct(prompt)` gives the agent a natural-language step and returns an *AgentResult*; `run.instruct_use_tool(prompt)` and `run.run_toolset(ToolsetRequest(...))` run a toolset request in-process, in the block's workspace, and return a parsed *RunResponse* to assert on; `run.ai_judge(output, rubric)` fails the spec when an AI judge finds the prose does not meet the rubric. The block runs either through the agent CLI or in the chat, chosen by the `in_chat` argument or, without it, by `AGENT_BDD_IN_CHAT`.

The spec helpers in `spec_helpers.py` — `repo_root_from`, `sessions_dir`, `expect_ok_action`, and `expect_instructions_contain`, which the template and the examples use — hold the path and assertion steps specs repeat; `run.generate_and_judge` holds the judging step. *AgentBdd* is the practice that writes these specs, layering the agent harness rules on BDD's test discipline (`agent-bdd.instructions`).

- **Purpose:** Test agent behaviour end to end against a real agent, so a spec fails when the agent would actually do the wrong thing.
- **Seam (terms):** AgentBdd, `agent`, AgentBlock, `instruct`, `instruct_use_tool`, `run_toolset`, ToolsetRequest, `ai_judge`, AgentResult, RunResponse, `agent-bdd.instructions`
- **Dependencies (one-way):** `cdd_guidance/practices/bdd` (*Bdd*, whose test discipline the practice builds on), `harness/guidance` (*PracticeGuidance*), `harness/agent_tools` (`@agent_toolset`, `@agent_instructions`).

The agent runner behind `agent(...)` (`agent.py`, `agent_bdd_common.py`, `conf.py` and the files beside them) is spec support, which the project's `.context/config.json` names as test code, so its imports are not the practice's dependencies: it reads `harness/installation` (*JsonFile*, and *RepositoryToolsets* for the toolsets a run may call) and `harness/agent_tools` (the toolset a request runs).

## Constraint

Take every step on the block `with agent(...) as run:` yields, so it acts on that spec's agent session and project. Load the agent's secrets and import paths when `agent(...)` opens, never on import, so the MCP host that imports the practice keeps its own environment. Never mock the harness or the agent's output. Import `agent` from `agent.py`, never the CLI or chat implementation directly. Use the spec helpers instead of copying request and assertion code into each spec.
