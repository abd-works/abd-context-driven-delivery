# The install path is not checked: a file as the path fails blaming the first toolset, and an empty path installs into the current directory

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\drive.py` (see bolt-01); `raw` passes the path to `Installer.create` as given.

**Story:** Register And Install Toolsets - no scenario covers this.

**Module and class:** `harness/installation/installer.py` `Installer.create` and `Deployment._install_all` (wraps the `FileExistsError` as *ToolsetInstallFailed* for the toolset being written).

**Severity:** misleading message (file as path); wrong result (empty path)

**Steps:**
1. `python drive.py install Claude C:/dev/_et/bolt/work/plain-folder/README.md raw`
2. `cd C:/dev/_et/bolt`, then `python drive.py install Claude "" raw` (the same as `--path ""`, as a script with an unset variable passes).

**Expected:** both refused before anything is written, naming the path: it is a file, or it is empty.

**Actual:**
1. `ToolsetInstallFailed: install failed for <class 'cdd_guidance.actions.diagnose.diagnose.Diagnose'>: FileExistsError: [WinError 183] Cannot create a file when that file already exists: 'C:\\dev\\_et\\bolt\\work\\plain-folder\\README.md'` - it reads as a fault in the Diagnose toolset.
2. Prints OK and writes `skills/`, `commands/`, `rules/`, `agents/`, `references/`, `language-adapters/`, `diagnostics.json`, and `.mcp.json` straight into the current directory (201 files beside the person's own), with `"path": "."` in the record. A clean from that directory removed the 201 files and left the four empty channel folders, `.mcp.json` (still naming the cdd server), and `diagnostics.json`.

Also seen, as a question: a path whose parents do not exist (`work/does/not/exist/.github`) is created without a word, while module-context.md says "Install into an IDE folder that exists".

**Tier that should catch it:** unit (`installer_spec.py`): no example gives a path that is a file or empty.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The steps call `drive.py`, which the report does not hold; I wrote my own from its "How it was run" line (`C:\dev\_et\sparky\confirm\bolt\drive.py`). A file as the path: `ToolsetInstallFailed: install failed for <class '...diagnose.Diagnose'>: FileExistsError: [WinError 183]`, word for word. An empty path: prints OK, `"path": "."`, and writes `agents`, `commands`, `language-adapters`, `references`, `rules`, `skills`, `diagnostics.json` into the current directory; clean removed 125 and left `agents`, `commands`, `rules`, `skills` and `diagnostics.json`. Differs from the report: I found no `.mcp.json` in that directory. The closing question about missing parents was not run.
- Cause, if you found it: `harness/installation/installer.py` `Installer.create` and `InstallTarget.__init__`: the path is used as given.
- Shares its cause with: bolt-02, bolt-03
