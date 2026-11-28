# sparky-02: a guidelines list edited while the cdd server runs is ignored by the tool list but used by the graph

**Title** - After a project's `.context/config.json` `guidelines` list changes, the running cdd server keeps listing and answering the old patterns' tools for that project, while its graph applies the new list, so one project works under two different lists at once.

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. `HeldProjectGuidelines.of` promises "its config file is read again once it changes"; CDR 0005 says a pattern no list names is left out of the server's tools.

**Module and class** - `harness/mcp/mcp_server.py` `McpHost._server_for` keeps one `ProjectToolsets` per project for the life of the process (`ProjectToolsets.for_project` chooses guidelines once); `harness/graph/pattern_overlays.py` `project_patterns` reads the config on each call.

**Severity** - wrong result.

**Steps**
1. Start the build's server: `python -m harness.mcp --port 8911` (sandbox env as in sparky-01).
2. `work/alpha/.context/config.json` = `{"guidelines_folder": "guidelines", "guidelines": ["stories", "ddd", "alpha_domain_driven"]}`, with `guidelines/alpha_domain_driven/alpha_domain_driven.py` defining `class AlphaDomainDriven(Pattern)`.
3. `tools/list` with `X-CDD-Project: .../work/alpha`: `alpha-domain-driven.instructions` listed, no `lern-domain-driven.instructions`. Correct.
4. Without restarting, rewrite the list to `["stories", "ddd", "lern_domain_driven"]`.
5. `tools/list` again; `tools/call alpha-domain-driven.instructions`; `tools/call lern-domain-driven.instructions`; `tools/call graph.set_overlays {"overlays": ["lern_domain_driven"]}`.

**Expected** - The server serves alpha as its list now says: `lern-domain-driven.instructions` listed and callable, `alpha-domain-driven.instructions` gone, as the graph already does.

**Actual** - The tool list still shows `alpha-domain-driven.instructions` and it still answers; `lern-domain-driven.instructions` answers `ToolNotEnrolled: lern-domain-driven.instructions is not a tool the cdd server publishes`. In the same process `graph.set_overlays ["lern_domain_driven"]` applies the LERN overlay (rules `lern.domain.driven.stories.DomainSpec...`). Only a server restart brings the tool list in line.

**Tier that should catch it** - unit (`harness/mcp/project_guidelines_spec.py`: list a project's tools, change its config, list again). Specs build a fresh host per example, so none changes the config under a host that has already served the project.
