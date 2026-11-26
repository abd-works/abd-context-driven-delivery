---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Invoke Guidance Through Slash Commands

Story map: [Invoke Guidance Through Slash Commands](../../../.context/story-map.md#e-invoke-guidance-through-slash-commands). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the cdd server today (`harness/mcp/tool_calls.py`, commit b609c986e) and is tested by `harness/mcp/tool_calls_spec.py`, which each scenario names. They were written after the dev lane's server, on 2026-11-23, answered a render whose caller had been told it was still running with "still running" on every later ask, and never with its result or its failure. No story test file runs them: the spec drives the cdd server's calls directly.

### Domain terms

- ++still running++ — the cdd server's answer to a call that is still running at its time limit (10 seconds, or ten minutes for an operation marked `@long_call`): a sentence telling the agent to call the tool again with the same arguments, and the same as data (`structuredContent` `{"still_running": {"tool", "seconds", "message"}}`). The run keeps going.
- ++identical call++ — a call to the same tool, on the same project, with the same arguments, from the same chat.

> In steps: ++example++ names an example in a table below.

## Examples

### calls

| call | tool | arguments | its run |
| --- | --- | --- | --- |
| ++slow validate++ | validate.validate | the story map's paths | writes its report after the time limit, answering written |
| ++failing validate++ | validate.validate | the story map's paths | fails after the time limit with ValueError: graph is corrupt |

## Story: Call CDD Tool Through MCP

#### Scenario: Answer a call told it is still running with its result when it is asked again

> Test: unit: harness/mcp/tool_calls_spec.py 'with a call that outlives its time limit' ('should hand the result to the same call made again', 'should not start the work again') and 'with a call that outlived its time limit, asked for again long after it ended'.

*Given* the agent called ++slow validate++ and was told it is ++still running++
*And* its run has since ended, an hour before the agent asks again
*When* the agent makes the ++identical call++ to ++slow validate++
*Then* the agent is answered written, the result of the run it was told about
*And* the work is not started again

#### Scenario: Answer a failed call's failure, never still running, when it is asked again

> Test: unit: harness/mcp/tool_calls_spec.py 'with a call that failed after its caller was told it is still running'.

*Given* the agent called ++failing validate++ and was told it is ++still running++
*And* its run has since failed with ValueError: graph is corrupt
*When* the agent makes the ++identical call++ to ++failing validate++
*Then* the agent is told the call failed with ValueError: graph is corrupt
*But* the agent is not told it is still running
