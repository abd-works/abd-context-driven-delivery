# An install given a relative path saves that relative path in the install record, so a clean or install run from another directory no longer finds it

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\drive.py` (see bolt-01); `raw` passes the path to `Installer.create` as given.

**Story:** Register And Install Toolsets - no scenario covers this. Promised: "`/clean` removes what it wrote" (`harness/installation/.context/module-context.md`).

**Module and class:** `harness/installation/install_target.py` `InstallTarget.__init__` (`Path(path)`, never resolved); `harness/installation/install_record.py` `InstallRecord.save` (`"path": str(folder)`) and `remove_installed` (resolves the saved path against the current directory).

**Severity:** wrong result

**Steps:**
1. `cd C:/dev/_et/bolt/work/no-commits`, then `python ../../drive.py install Claude .claude raw` (the same as `install.py --ide Claude --path .claude`).
2. Read the record: `"path": ".claude"`.
3. `cd C:/dev/_et/bolt`, then `python drive.py clean Claude C:/dev/_et/bolt/work/no-commits`.

**Expected:** the record holds `C:\dev\_et\bolt\work\no-commits\.claude`, and the clean removes the 201 files.

**Actual:** `clean removed 0`; 202 files stay. By the code (not run, since it would write into the checkout): the next `install.py` with no arguments reads `.claude` against its own current directory, finds no such folder, and installs into `{repo}/.cursor` (`InstallTarget.from_last_install`).

**Tier that should catch it:** unit (`install_record_spec.py` / `installer_spec.py`): every example passes an absolute temporary path.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The steps call `drive.py`, which the report does not hold; I wrote my own from its "How it was run" line (`C:\dev\_et\sparky\confirm\bolt\drive.py`). From `work/no-commits`, install with path `.claude`: the record holds `"path": ".claude"`. Clean from another directory: `clean removed 0`, 126 files stay.
- Cause, if you found it: `harness/installation/install_target.py` `InstallTarget.__init__` keeps `Path(path)` unresolved; `InstallRecord.remove_installed` resolves the saved path against the current directory, finds another folder, and removes nothing.
- Shares its cause with: bolt-01, bolt-06 (the silent `remove_installed`); bolt-02, bolt-04 (unchecked arguments of `Installer.create`)
