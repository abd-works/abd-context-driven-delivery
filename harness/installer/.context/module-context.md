# harness/installer
*Installer* publishes every marked toolset member in the repository into an IDE's folder (`.claude`, `.cursor`, `.github`, Kilo), so an author never writes a skill, command, rules file, MCP entry, or hook entry by hand. A person runs it as `/install`, or `python scripts/install.py --ide Claude`, and `/clean` removes what it wrote. It finds the toolsets with *RepositoryToolsets* (harness/installation), writes each member through the installation of every channel its marks name (files and language adapters from harness/installation, MCP from harness/mcp, hooks from harness/hooks), then starts the hook server and the cdd server and installs the board and cdd plugins, so a finished install answers at once.

- **Purpose:** Install one repository into one IDE folder through every channel, from one walk of the repository, and start what that install needs running.
- **Seam (terms):** Installer (`install`, `install_self`, `clean`, `ensure_runtimes`, `diagnose_install`, `toolsets`, `write_diagnostics_section`); `/install`, `/clean`; `python scripts/install.py`
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/markdown, harness/hooks, harness/mcp. It sits at the top of the publishing chain: none of these imports it.

## Constraint

Change installed files only by changing the marked source and installing again; `.claude/`, `.cursor/`, `.github/`, `.mcp.json`, and the `cdd` entry in `~/.claude.json` are overwritten on every install. Install into an IDE folder that exists: when `.install-state.json` beside the installer names a folder that is gone, the install goes to `{repo}/.cursor`. Code that only needs the repository's toolsets or its import path reads *RepositoryToolsets*, not the Installer, so it does not depend on every channel.
