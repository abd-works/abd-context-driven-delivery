# Two installs started at the same moment, one from the main checkout and one from a ticket's worktree, fail one of them with a raw WinError 32 while both publish the board mod

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** the real `scripts/install.py`, from two copies of the build: `C:\dev\_et\bolt\checkout-main` (a clone, on main) and `C:\dev\_et\bolt\checkout-feature` (a linked worktree of it, branch feature-x). Home, USERPROFILE, APPDATA, LOCALAPPDATA, CLAUDE_CONFIG_DIR in the sandbox, `CDD_HOME=C:\dev\_et\bolt\cdd_home2`, `CDD_SERVER_PORT=48917` (dev lane 48918), a stub `claude` first on PATH. Both lanes were pinned and their servers running beforehand.

**Story:** Register And Install Toolsets / serve-cdd-code-in-lanes / install-into-the-lane-of-the-checkout. No scenario has two installs run at once.

**Module and class:** `harness/mcp/cdd_home.py` `CddHome._copy_mod` (from `write_claude_plugin` -> `write_mod_plugins` -> `_publish_mods` -> `_publish_mod`), reached from `McpInstallation.standup`. Both lanes copy their mods into the one marketplace, `<CDD_HOME>\claude-plugins`.

**Severity:** wrong result

**Steps:**
1. `cd checkout-main; python scripts/install.py --ide Claude --pin-runtime`, then the same in `checkout-feature`.
2. Start both at once: `(cd checkout-main && python scripts/install.py --ide Claude) & (cd checkout-feature && python scripts/install.py --ide Claude) & wait`

**Expected:** both installs finish, as each does alone; or the second waits for the first.

**Actual:** the worktree's install exits 0. The main checkout's exits 1 with a 46-line traceback ending
`shutil.Error: [('...\cdd_home2\runtime\harness\chat-ui\pane\.claude-plugin\plugin.json', '...\cdd_home2\claude-plugins\cdd-board\.claude-plugin\plugin.json', '[WinError 32] The process cannot access the file because it is being used by another process')]`.
It failed in standup, after its files and record were written and before the server check and `diagnostics.json`: `.claude` holds 201 files and no `diagnostics.json`, so the person sees a failed install and no report. Seen once in one try. In real use this is two chats starting together, since the board mod runs `install.py --from-chat` at chat start.

**Tier that should catch it:** heavy: no spec runs two installs at once against one cdd home.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The real `scripts/install.py` in a local clone of the build under my sandbox (`C:\dev\_et\sparky\confirm\bolt2\checkout-main`, removed afterwards), home, USERPROFILE, APPDATA, LOCALAPPDATA, CLAUDE_CONFIG_DIR and CDD_HOME in the sandbox, `CDD_SERVER_PORT=48930`, a stub `claude` first on PATH. A linked worktree `checkout-feature` on branch feature-x, both lanes pinned and serving (ports 48930 and 48931), then both installs started together, five times. Failed: 2 of 5. Both times the failing install was the worktree's, not the main checkout's, with the report's `shutil.Error ... claude-plugins\cdd-board\.claude-plugin\plugin.json ... [WinError 32]`, raised from `CddHome._copy_mod`. Its `.claude` held 202 files and a `diagnostics.json`; I cannot say that file was written by the failed run.
- Cause, if you found it: `harness/mcp/cdd_home.py` `CddHome._copy_mod`, reached from `write_claude_plugin` -> `write_mod_plugins` -> `_publish_mods` -> `_publish_mod`: both installs copy the mods into the one `<CDD_HOME>\claude-plugins` folder, and nothing keeps two installs apart.
- Shares its cause with: bolt-13 (two installs at once, nothing holds one back; the failing operation differs)
