# `--ide claude` (lowercase) or any unknown IDE name installs the Cursor layout into `.cursor` without a word, and the record keeps the wrong name

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\drive.py` (see bolt-01): `Installer.create(ide, path, repo=<checkout>)` then `install()`, home and cdd home in the sandbox, no server started.

**Story:** Register And Install Toolsets - no scenario covers this. `scripts/install.py --help` says "IDE name: Cursor, VS Code, Kilo, or Claude".

**Module and class:** `harness/installation/ide_layout.py` `IdeLayout.folder_name` (`_FOLDERS.get(self.ide, <Cursor's>)`) and each `self.ide == "Claude"` test; `scripts/install.py` `_add_install_options` (`--ide` takes any text).

**Severity:** wrong result

**Steps:**
1. `python drive.py install claude C:/dev/_et/bolt/work/plain-folder`
2. `python drive.py install Emacs C:/dev/_et/bolt/work/plain-folder`

**Expected:** the name is matched whatever its case, and a name that is no IDE is refused with the four names it can be.

**Actual:** both print OK and write 203 files into `plain-folder\.cursor` in the Cursor layout (`.mdc` rules, `hooks.json`, and an `mcp.json` in the folder, since the name has no user-level config). The record is saved with `"ide": "claude"` / `"ide": "Emacs"`, so the next install with no `--ide` repeats it. A person on their first day who types `--ide claude` gets no `.claude` folder, no skills in Claude Code, and nothing that says why.

**Tier that should catch it:** unit (an `IdeLayout` spec or `installer_spec.py`): no example gives a name outside the four.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The steps call `drive.py`, which the report does not hold; I wrote my own from its "How it was run" line (`C:\dev\_et\sparky\confirm\bolt\drive.py`). `install claude` and `install Emacs` both print OK and write 128 files into `.cursor`; the record keeps `ide claude` and `ide Emacs`.
- Cause, if you found it: `harness/installation/ide_layout.py` `IdeLayout.folder_name`: `self._FOLDERS.get(self.ide, self._FOLDERS[self.DEFAULT_IDE])`, and `is_claude_code` compares with `"Claude"` exactly. `Installer.create` checks neither name nor path.
- Shares its cause with: bolt-03, bolt-04 (`Installer.create` takes the ide and the path as given, unchecked)
