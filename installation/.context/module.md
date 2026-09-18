# installation

This is the master package for configuring **agent tools** into an AI runtime. Annotations, install writers, and the Cursor/MCP/hook runtimes live here. `.cursor` is the deploy target, not the source.

1. **One package, four jobs.** `Installer` collects annotated toolsets and writes them. `harness_files` writes skills, commands, and rules. `mcp` writes `mcp.json` and runs `python -m installation.mcp`. `hooks` writes `hooks.json` and runs `hook_server.py`. Do not grow a second install or host under `harness/` or `tools/`.

2. **Import from the repo root.** Use `installation.installer`, `installation.mcp`, `installation.hooks`, `installation.harness_files`. Do not put `installation/` on `PYTHONPATH` — that makes `import mcp` load this tree instead of the MCP SDK.

3. **Catalogs share `AgentToolSet`.** MCP and hooks load toolsets with `AgentToolSet.load_toolsets` and filter with `tools_for(InstallDestination.MCP)` / `tools_for(InstallDestination.HOOK)`. Do not rescan classes with `getmembers` or walk `toolset.tools` a second time.

4. **Default repo is the checkout root.** `installation/installer.py` is one level below the repo (`parents[1]`). Files under `installation/hooks/` and `installation/mcp/` are two levels below (`parents[2]`). Wrong parent counts send collect and specs outside the repo.

5. **Deploy artifacts stay in the IDE folder.** Install writes Cursor `hooks.json` (one `hook_server.py` command per event), `hook-handlers.json`, `mcp.json`, and markdown under `.cursor`. Change the writers here; do not hand-edit deploy copies as if they were source.
