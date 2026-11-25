# An install stopped halfway leaves its files in the folder with no record of them, so clean removes nothing

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\drive.py` (see bolt-01), with the process killed 0.9 seconds after it started.

**Story:** Register And Install Toolsets - no scenario covers a stopped install. Promised: "`/clean` removes what it wrote" (`harness/installation/.context/module-context.md`); *ToolsetInstallFailed* says the install stops "so no IDE folder is left with part of a toolset".

**Module and class:** `harness/installation/installer.py` `Deployment.run` (the record is saved once, in `_save_installed_files`, after every file is written; the previous install is cleaned before the first is written).

**Severity:** wrong result

**Steps:**
1. `python drive.py install Cursor C:/dev/_et/bolt/work/one-commit &`, then after 0.9 s `taskkill /F /T /PID <its pid>`.
2. Count the files in `work/one-commit/.cursor`, and read the record.
3. `python drive.py clean Cursor C:/dev/_et/bolt/work/one-commit`.

**Expected:** the record lists the files written so far (or the folder is marked as holding an unfinished install), so a clean removes them and the next install knows what to replace.

**Actual:** 114 files are in `.cursor`; the record still describes the install before it (`Claude .claude 201`); `clean removed 0`, and the 114 files stay. An install run again over them finished and recorded 203 files, so the same version repairs itself. The files are lost to every later clean when the next install is of another version, another folder, or another IDE. The same holds for an install that fails with *ToolsetInstallFailed* partway (file as the path, bolt-04): what it wrote before failing is in no record. Where the stopped install replaced an earlier one, that earlier install's files were already removed, so the folder holds part of the new install and none of the old.

**Tier that should catch it:** heavy (`installer_heavy_spec.py`): "a toolset reference that cannot be instantiated" checks the error, not what the record says of the files written before it.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The steps call `drive.py`, which the report does not hold; I wrote my own from its "How it was run" line (`C:\dev\_et\sparky\confirm\bolt\drive.py`). I killed the Cursor install 1.33 s after its start (a whole install takes about 1.6 s here), not at 0.9 s. 128 files were in `.cursor`, the record still read `Claude ...plain-folder\.claude 125`, and `clean removed 0` left all 128. So my stop came later than the report's 114 files, with the same result. Not run: the reinstall over the files.
- Cause, if you found it: `harness/installation/installer.py` `Deployment.run` saves the record once, after every file is written; until then the one shared record describes the install before, and `InstallRecord.remove_installed` removes nothing for another folder.
- Shares its cause with: bolt-01, bolt-03
