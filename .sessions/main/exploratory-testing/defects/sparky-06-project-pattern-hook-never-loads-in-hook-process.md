# sparky-06: a hook on a project's own pattern is installed but can never load in the hook process

**Title** - An install publishes a project pattern's `@hook` operation into `hook-handlers.json` under its digest package name (`cdd_project_guidelines_<digest>....:AlphaDomainDriven`), but the hook process never makes that package importable, so the handler is skipped as "No module named ..." on every event and the hook never runs.

**Charter** - Sparky, theme 1. **Tester** - Sparky.

**Story** - no scenario covers this. CDR 0005 says a project pattern "installs under `patterns/`, beside the shipped ones", and the graph worker is handed `patterns_project` precisely so it can import the package (`graph_worker.py`); the hook side has no such step.

**Module and class** - `harness/hooks/hook_server.py` `HandlerCatalog._load_items` / `HookServer.from_handlers` / `from_repository` (load each `ref` by name with nothing calling `GuidelinesFolder.ensure_package`); `harness/installation/project_guidelines.py` `GuidelinesFolder.ensure_package` is the only thing that registers the package.

**Severity** - wrong result (the hook is silently skipped; the only trace is the hook stand-up notice).

**Steps**
1. Sandbox env (`CDD_HOME`, `PYTHONUTF8=1`, `PYTHONPATH=<build>`, `USERPROFILE`/`HOME` pointed at a sandbox folder, `CDD_SERVER_PORT=8912`).
2. `work/alpha/.context/config.json` = `{"guidelines_folder": "guidelines", "guidelines": ["stories", "ddd", "alpha_domain_driven"]}`; `guidelines/alpha_domain_driven/alpha_domain_driven.py` defines `@agent_toolset class AlphaDomainDriven(Pattern)` with `@hook("postToolUse") def mark_edit(self, tool_use) -> dict: return {"additional_context": "HOOK-OF-alpha"}`.
3. Install the guidelines into Cursor: `Installer.create(ide="Cursor", path=work/alpha/.cursor, repo=<build>)`, then `installer.install([r for r in installer.repository_toolsets() if guideline_name(r.toolset_class)])`. `work/alpha/.cursor/hook-handlers.json` now lists `{"event": "postToolUse", "operation": "mark_edit", "ref": "cdd_project_guidelines_b4032f9d29e7.alpha_domain_driven.alpha_domain_driven:AlphaDomainDriven"}`, and `hooks.json` runs `harness/hooks/hook_daemon.py` for `postToolUse`.
4. In a fresh process: `HookServer.from_handlers(r"work\alpha\.cursor\hook-handlers.json", repo=<build>)`, then `dispatch(HookPayload({"hook_event_name": "postToolUse", "workspace_roots": [alpha], "tool_name": "Write", "tool_input": {"file_path": alpha + r"\src\x.py"}}))`.
5. Control: the same, after `PROJECT_GUIDELINES.of(alpha).own_classes` in that process.

**Expected** - The handler loads and answers `additional_context: HOOK-OF-alpha` for alpha's edit.

**Actual** - Step 4: `hook standup skipped illegitimate handlers and continued: - cdd_project_guidelines_b4032f9d29e7.alpha_domain_driven.alpha_domain_driven:AlphaDomainDriven: No module named 'cdd_project_guidelines_b4032f9d29e7.alpha_domain_driven.alpha_domain_driven'`; result `{'permission': 'allow'}`. Step 5 answers `{'permission': 'allow', 'additional_context': 'HOOK-OF-alpha'}`, so only the import is missing. For Claude, the install records `hook 0 -> 0` and the cdd plugin's hooks come from the cdd home, so the project's hook is not even listed.

**Tier that should catch it** - heavy (install into a project with a pattern hook, then load the hook server from the written `hook-handlers.json` in a fresh process). The example project's pattern has no hook, and the heavy spec only checks the skill and rules files.
