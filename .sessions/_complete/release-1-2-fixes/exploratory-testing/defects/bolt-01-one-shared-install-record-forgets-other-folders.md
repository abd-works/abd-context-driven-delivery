# An install into a second folder makes the first folder's install unknown: its clean removes nothing and its stale files stay for good

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\drive.py` calls `Installer.create(ide, path, repo=<checkout>)` then `install()` / `clean()`, as the heavy spec does, with HOME/USERPROFILE/APPDATA/CDD_HOME pointed at the sandbox, `Deployment.ensure_runtimes` replaced (no server started), and `installer._SHARED_RECORD` pointed at `C:\dev\_et\bolt\shared-record\.install-state.json` so the checkout's own record is not written. Usage: `python drive.py install|clean <ide> <project folder>`.

**Story:** Register And Install Toolsets - no scenario covers two install folders on one checkout. `harness/installation/.context/module-context.md` promises "`/clean` removes what it wrote" and "one server installs many projects".

**Module and class:** `harness/installation/installer.py` `Installer.create` (`_SHARED_RECORD`: one `harness/installation/.install-state.json` for every folder that is not temporary) and `harness/installation/install_record.py` `InstallRecord.remove_installed` ("A record of another folder removes nothing").

**Severity:** wrong result

**Steps:**
1. `python drive.py install Claude C:/dev/_et/bolt/work/plain-folder` (201 files recorded).
2. `python drive.py install Cursor C:/dev/_et/bolt/work/plain-folder` - the one record now names `.cursor`.
3. `python drive.py install Claude C:/dev/_et/bolt/work/plain-folder` - the record names `.claude` again.
4. `python drive.py clean Cursor C:/dev/_et/bolt/work/plain-folder`.
5. Stale file: add `commands/old-command.md` to `plain-folder/.claude` and to the record's `installed_files` (standing for a file an older CDD wrote), install Claude into `work/folder with spaces (1)`, then install Claude into `plain-folder` again.

**Expected:** the clean removes the 203 files the Cursor install wrote; the reinstall in step 5 removes `old-command.md`, as it does when no other folder was installed in between (an install that replaces cleans the previous install first).

**Actual:** step 4 prints `clean removed 0` with no warning, and 204 files stay in `.cursor`. After step 5 `plain-folder/.claude/commands/old-command.md` is still there and is in no record, so no later install or clean can remove it. In real use this is every `install.py --from-chat <other project>` (the board mod runs it at chat start) and every person who installs both Claude and Cursor: the record flips to the latest folder, and renamed or deleted skills, commands, rules, and language adapters are left in all the others. An install with no arguments then also goes into that other project's folder, not the checkout's (seen: after a Kilo install into `one-commit`, `Installer.create(repo=...)` with no ide or path wrote `one-commit/.kilo`).

**Tier that should catch it:** heavy (`installer_heavy_spec.py`). Its installs go to temporary folders, which keep a record of their own in the folder, so no spec has two folders share the one record.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The steps call `drive.py`, which the report does not hold; I wrote my own from its "How it was run" line (`C:\dev\_et\sparky\confirm\bolt\drive.py`). Claude, Cursor, Claude installs into one folder, then clean Cursor: `clean removed 0`, 128 files stay in `.cursor`. The added `old-command.md` is still there after the install into the second folder and the reinstall, and is in no record. My counts are 125 and 127 files where the report says 201 and 203. Not run: the last sentence's install with no ide or path.
- Cause, if you found it: `harness/installation/installer.py` `Installer.create` keeps one `_SHARED_RECORD` for every folder that is not temporary, and `harness/installation/install_record.py` `InstallRecord.remove_installed` answers an empty list, without a word, when the record's path is another folder.
- Shares its cause with: bolt-03, bolt-06 (each is a folder whose files the one record does not describe, so `remove_installed` removes nothing and says nothing)
