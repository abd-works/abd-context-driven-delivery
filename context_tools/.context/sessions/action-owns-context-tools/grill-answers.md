# Grill Answers

### Driver of iterate
The iterate action owns the run. Context tools are arguments passed into it (slash-tool slash-action), not kits that BaseContextTool must compose so it can call the utility. Sources: `context_tools/base/.context/module-context.md` (lifecycle `iterate` + kit provider `iterator()`), `context_tools/actions/.context/module-context.md` (host-action kits compose with a context tool already in scope), `context_tools/base/base_context_tool.py` (`iterate` opens workspace, records decisions, calls `iterator.iterate_session()`, then `generate()`).

### First slice — one operation
Add one extra operation on Iterator that takes a collection of context tools. Move the original host `iterate` step that runs `generate()` onto that operation. Do not invert generate/validate/eval or relocate eval in this tick. Sources: `context_tools/actions/iterate/.context/module-context.md` (`Iterator` / `iterate_session`), user: one tool first, one operation.

### First tool
BDD only for this tick (`context_tools/bdd/.context/module-context.md` — development iterate: one test RED, then production GREEN). CleanEngineering pairing waits until the concept is proven.
