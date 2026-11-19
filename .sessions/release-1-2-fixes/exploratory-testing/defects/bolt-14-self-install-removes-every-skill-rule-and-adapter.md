# `install.py --self`, described as an Installer-only refresh, removes every skill, rule, agent and language adapter the full install wrote

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** the real `scripts/install.py` from `C:\dev\_et\bolt\checkout-main` (a clone of the build on main), isolated as in bolt-12.

**Story:** Register And Install Toolsets. `--self` help: "Deploy only the Installer toolset (slash /install and /clean, hooks)". `Installer.install` docstring: "Installer-only refresh (`/install` and `/clean` without walking the catalog): `python scripts/install.py --self`". The heavy spec's "with the installer toolset as the only deploy subject" installs into an empty folder.

**Module and class:** `scripts/install.py` `_install_toolsets` (`install_self(replace=not args.no_replace)`); `harness/installation/installer.py` `Deployment.install_self` -> `run([], replace=True)`, which cleans the whole previous install first.

**Severity:** wrong result (question if a wipe is meant)

**Steps:**
1. `python scripts/install.py --ide Claude` - 201 files recorded in `.claude`.
2. `python scripts/install.py --ide Claude --self`
3. Count `.claude`.

**Expected:** a refresh of `/install` and `/clean` that leaves the rest of the install in place, or a word that everything else is being removed.

**Actual:** the record lists 19 files; `.claude/skills` holds 0 skills and `language-adapters` 0 files. Every practice, action, and toolset skill and rule is gone until a full install is run again, and the output says only how the server runs. `--self --no-replace` is the form that refreshes without removing.

**Tier that should catch it:** heavy (`installer_heavy_spec.py`): its self-install example starts from an empty folder, never from a full install.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The real `scripts/install.py` in a local clone of the build under my sandbox (`C:\dev\_et\sparky\confirm\bolt2\checkout-main`, removed afterwards), home, USERPROFILE, APPDATA, LOCALAPPDATA, CLAUDE_CONFIG_DIR and CDD_HOME in the sandbox, `CDD_SERVER_PORT=48930`, a stub `claude` first on PATH. `install.py --ide Claude`: the record lists 201 files, `.claude/skills` holds 76 folders, `language-adapters` 58 files. `install.py --ide Claude --self` exits 0, saying only how the server runs: the record lists 19 files, `skills` holds 0 and `language-adapters` 0. `--self --no-replace` was not run.
- Cause, if you found it: `scripts/install.py` `_install_toolsets` calls `install_self(replace=not args.no_replace)`, and `harness/installation/installer.py` `Deployment.install_self` runs `self.run([], replace=replace)`, which removes the whole previous install before writing the Installer's own files.
- Shares its cause with: none
