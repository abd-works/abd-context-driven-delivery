# Grill Answers

### Driver of iterate
The iterate action owns the run. Context tools are arguments passed into it (slash-tool slash-action), not kits that BaseContextTool must compose so it can call the utility. Sources: `practices/base/.context/module-context.md` (lifecycle `iterate` + kit provider `iterator()`), `actions/.context/module-context.md` (host-action kits compose with a context tool already in scope), `practices/base/base_context_tool.py` (`iterate` opens workspace, records decisions, calls `iterator.iterate_session()`, then `generate()`).

### First slice — one operation
Add one extra operation on Iterator that takes a collection of context tools. Move the original host `iterate` step that runs `generate()` onto that operation. Do not invert generate/validate/eval or relocate eval in this tick. Sources: `actions/iterate/.context/module-context.md` (`Iterator` / `iterate_session`), user: one tool first, one operation.

### First tool
BDD only for this tick (`practices/bdd/.context/module-context.md` — development iterate: one test RED, then production GREEN). CleanEngineering pairing waits until the concept is proven.
### Next slice — host is not the call site

Stop BaseContextTool.iterate from composing Iterator. /iterate runs iterate.iterate:Iterator with arguments.tools listing the in-scope context tool(s). Also prove agent skills/commands use that call site, with an agentic BDD spec plus ai_judge that Iterator.iterate actually owned the run. Sources: practices/base/.context/module-context.md, actions/iterate/.context/module-context.md, utilities/agent_skills/.context/module-context.md, user: option A plus agent-skill validation.

### Next tool — sketch, complete replace

Invert sketch in one tick the way iterate ended: Sketcher.sketch(tools) is the host sketch body (open, record decisions, sketch_session, generate); BaseContextTool.sketch does not compose Sketcher; /sketch runs sketch.sketch:Sketcher with arguments.tools. Agent skills plus an agentic BDD spec with ai_judge. Sources: practices/base/base_context_tool.py (host sketch), actions/sketch/.context/module-context.md, utilities/agent_skills/.context/module-context.md, user: next tool then complete replace.

### Shared resolve — AgenticToolset.context_tools

Do not copy toolset loading into each kit. Iterator and Sketcher inherit `context_tool` / `context_tools` from AgenticToolset and loop `for host in self.context_tools(tools)`. Sources: primitives/agent_tools/.context/module-context.md, user: every action should not reimplement search.

