# cdd_guidance/practices/agent_bdd

*AgentBdd* is the practice for specs that drive a real agent and judge what it did. It composes vanilla BDD: its generate output is the session's own *Bdd*'s instructions and generate output.

- **Purpose:** Test agent behaviour end to end against a real agent, so a spec fails when the agent would actually do the wrong thing.
- **Seam (terms):** AgentBdd
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/installation, cdd_guidance/practices/bdd

## AgentBdd : PracticeGuidance

The agent BDD practice: mamba specs that drive a real agent.

+ AgentBdd(format: str = 'python')
------
+ bdd: Bdd
	// the session's own BDD practice, read from the session's graph
----
+ generate_output(): str
---<<reads instructions and generate output of>>--> Bdd
