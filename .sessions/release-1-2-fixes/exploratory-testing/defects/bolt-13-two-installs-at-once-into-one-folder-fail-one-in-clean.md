# Two installs started at the same moment into one folder fail one of them with a raw FileNotFoundError while it cleans the previous install

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** the real `scripts/install.py` from `C:\dev\_et\bolt\checkout-main`, isolated as in bolt-12.

**Story:** Register And Install Toolsets - no scenario has two installs run at once.

**Module and class:** `harness/installation/install_record.py` `InstallRecord.remove_installed` (`target.is_file()` then `target.unlink()`, with the other install removing the same files in between).

**Severity:** wrong result

**Steps:** in `checkout-main`, after one finished install: `python scripts/install.py --ide Claude & python scripts/install.py --ide Claude & wait`

**Expected:** both finish, or the second says another install is running in this folder.

**Actual:** one exits 0. The other exits 1 with a traceback ending
`FileNotFoundError: [WinError 2] The system cannot find the file specified: 'C:\\dev\\_et\\bolt\\checkout-main\\.claude\\skills\\builders-create-practice-guidance\\SKILL.md'`.
This time the folder ended whole (201 files recorded, all on disk), because the install that failed stopped in its clean. Nothing keeps the other order from happening: the second's clean removing files the first has just written. Seen once in one try. In real use: two chats opening in one project together, each running the board mod's install.

**Tier that should catch it:** heavy: no spec runs two installs at once into one folder.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The real `scripts/install.py` in a local clone of the build under my sandbox (`C:\dev\_et\sparky\confirm\bolt2\checkout-main`, removed afterwards), home, USERPROFILE, APPDATA, LOCALAPPDATA, CLAUDE_CONFIG_DIR and CDD_HOME in the sandbox, `CDD_SERVER_PORT=48930`, a stub `claude` first on PATH. After one finished install, two installs started together in `checkout-main`, five times. Failed: 5 of 5, one install of each pair exiting 1. Four ended with the report's `FileNotFoundError: [WinError 2]` for a `.claude\skills\...\SKILL.md`, and one with `PermissionError: [WinError 5] Access is denied` for such a file; all were raised from `install_record.py` line 76, `target.unlink()` in `remove_installed`. Each time the folder ended whole, 202 files.
- Cause, if you found it: `harness/installation/install_record.py` `InstallRecord.remove_installed`: `target.is_file()` then `target.unlink()` while the other install removes or rewrites the same files; nothing keeps two installs of one folder apart.
- Shares its cause with: bolt-12 (two installs at once); the operation is the one bolt-01, bolt-03 and bolt-06 show removing nothing
