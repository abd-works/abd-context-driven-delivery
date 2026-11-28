# sparky-08: cdd.restart reloads CDD's code but keeps a project pattern's old module

**Title** - After a project's own pattern module is changed, `cdd.restart` answers `is_restarted: true` and re-reads the pattern's markdown, but keeps the module it imported first, so a tool added to the pattern never appears until the whole server process is stopped and started.

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. The built-in restart is described as "Restart the CDD MCP host on the code as it is now: reload its Python and start its toolsets again"; CDR 0005 says the project pattern "belongs to the project and changes with it".

**Module and class** - `harness/mcp/mcp_server.py` `ProjectToolsets.restarted` / `_forget_checkout_modules` forgets only modules under the served checkout; the `cdd_project_guidelines_<digest>` package and its modules live in the project's folder, stay in `sys.modules`, and `GuidelinesFolder.ensure_package` / `importlib.import_module` hand back the old module to the fresh `PROJECT_GUIDELINES`.

**Severity** - wrong result (the person is told the server runs the code as it is now).

**Steps**
1. Server 8911 as in sparky-01; alpha lists `alpha_domain_driven`; list alpha's tools once (`X-CDD-Project: .../work/alpha`) so the module is imported.
2. Add to `AlphaDomainDriven` in `work/alpha/guidelines/alpha_domain_driven/alpha_domain_driven.py`: `@mcp @agent_tool def alpha_version(self) -> str: return "v2"` (imports `agent_tool` from `harness.agent_tools.agent_tools`, `mcp` from `harness.mcp.mcp_annotations`).
3. `tools/call cdd.restart {}` for alpha; list alpha's tools again.
4. Control: a fresh process, `McpHost.from_repo(<build>).tools_listed_for(alpha)`.

**Expected** - After the restart alpha's tools include `alpha-domain-driven.alpha_version`, as the fresh process lists them.

**Actual** - Restart answers `{"is_restarted": true, "tools": 293, "exceptions": []}`; afterwards the list shows only `alpha-domain-driven.instructions` (its description now read from the edited markdown, `OWN-PATTERN-OF-alpha.`). The fresh process lists `['alpha-domain-driven.alpha_version', 'alpha-domain-driven.instructions']` and the call answers `v2`.

**Tier that should catch it** - heavy (`harness/mcp/mcp_server_host_heavy_spec.py` or the project-guidelines heavy spec: serve a project, change its pattern module, restart, list). No spec restarts a host that has served a project with its own patterns.
