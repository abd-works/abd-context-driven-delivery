# installation

- **`Installer` state path must exist.** If `.install-state.json` points at a directory that is gone (a temp install from specs), ignore it and install to `{repo}/.cursor`. Do not write the CDD checkout into a dead temp tree.
- Prove `/install` by the path in `.install-state.json` matching this repo’s `.cursor`, and by `cdd.ping` → `pong`. A returned `McpInstallation` object is not that proof.
