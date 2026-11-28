# sparky-01: a pattern module with a syntax error makes every graph call of its project fail

**Title** - In a project whose guidelines folder holds one pattern module that does not import, every graph tool (`graph.practice_names`, `graph.inventory`, `graph.set_overlays`) answers `SyntaxError` and nothing else, although the cdd server's tool list for the same project skips the folder and serves the rest.

**Charter** - Sparky, theme 1 (a project that keeps its own patterns). **Tester** - Sparky.

**Story** - no scenario covers this. CDR `harness/graph/.context/cdr/0005-a-project-keeps-its-own-patterns.md` and `ProjectToolsets._with_guidelines` ("a guidelines folder that cannot be imported is recorded and its patterns left out") promise the folder is skipped; only the server's tool list does that.

**Module and class** - `harness/graph/pattern_overlays.py` `project_patterns` (calls `PROJECT_GUIDELINES.of(project).own_classes` with no handling), reached from `PatternOverlays.from_project` and `Graph.use_patterns_of` (`harness/graph/graph.py:1342`); compare `harness/mcp/mcp_server.py` `ProjectToolsets._with_guidelines`, which catches `LOAD_FAILURES`. Also `harness/installation/project_guidelines.py` `GuidelinesFolder._imported`: one bad subfolder stops every other pattern in the folder loading.

**Severity** - blocks work (the project's graph cannot be used at all, not even with the shipped `lern_domain_driven` its list names; the server itself stays up).

**Steps**
1. Sandbox: `CDD_HOME=C:\dev\_et\after-1-2-1\sparky\cdd_home`, `PYTHONUTF8=1`, `PYTHONPATH=<build>`; start `python -m harness.mcp --port 8911` from the build checkout.
2. Project `work/broken` (a git repo): `.context/config.json` = `{"guidelines_folder": "guidelines", "guidelines": ["stories", "broken_domain_driven", "lern_domain_driven"]}`; `guidelines/broken_domain_driven/broken_domain_driven.py` defines an `@agent_toolset class BrokenDomainDriven(Pattern)` and ends with the line `def oops(:`.
3. Over MCP HTTP with header `X-CDD-Project: C:/dev/_et/after-1-2-1/sparky/work/broken`: `tools/list` (works: 291 tools, `lern-domain-driven.instructions` present), then `tools/call graph.practice_names {}`, `graph.inventory {}`, `graph.set_overlays {"overlays": ["lern_domain_driven"]}`.

**Expected** - The broken folder is recorded and its patterns left out, as the server's tool list does; graph calls work with the patterns that do load (the shipped `lern_domain_driven`), and any message names the project's guidelines folder and the module that failed.

**Actual** - Each graph call answers `SyntaxError: invalid syntax (broken_domain_driven.py, line 10)` with no project or folder named; `graph.practice_names` fails too, though it lists practices, not patterns. `sessions.current` and `session.show` still work. The server log shows the tool list skipped it: `MCP standup exception: skipped guidelines of C:\dev\_et\after-1-2-1\sparky\work\broken: invalid syntax`.

**Tier that should catch it** - unit (`harness/graph/project_patterns_spec.py` with a fixture folder whose module fails to import), plus heavy for the server path. Every spec uses the one example project whose pattern imports cleanly, so no test has a folder that fails.
