# installation

- **`Installer` state path must exist.** If `.install-state.json` points at a directory that is gone (a temp install from specs), ignore it and install to `{repo}/.cursor`. Do not write the CDD checkout into a dead temp tree.
- **The deploy walk parses `harness/`.** Marked toolsets there install with the rest of the repo. Leave `harness/` off `PYTHONPATH` so `import mcp` stays the MCP SDK.
- Prove `/install` by the path in `.install-state.json` matching this repo’s `.cursor`, and by `cdd.ping` → `pong`. A returned `McpInstallation` object is not that proof.
- **`@noDeploy` keeps that operation out of install.** Skill, command, MCP, and hook marks on the same operation do not write files. The catalog can still list it. Use it when the operation is not ready to deploy.
