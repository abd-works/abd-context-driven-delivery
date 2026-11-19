# Install from latest on a checkout already past the newest release rewrites its committed, newer version in pyproject.toml back to the release's and leaves the file modified

**Charter:** Round 1 second charter - the install scripts and the lanes (card 89963ac5a974)
**Tester:** Bolt

**How it was run:** step 1 of `--from-latest` only, through the script's own functions (`_latest_release`, the merge, `_match_release_version`) loaded from `C:\dev\_et\bolt\checkout-main\scripts\install.py`. The script itself was not run: after step 1 it runs `--restart-everything`, which stops every app's server on the ports the person's own apps use.

**Story:** `/install-latest` step 1: "A checkout already at or past that release merges nothing and keeps its own commits" (`scripts/install.py` `_install_from_latest`). `_match_release_version` is written for "a local edit to the version line ... which the merge leaves in place".

**Module and class:** `scripts/install.py` `_match_release_version`.

**Severity:** wrong result

**Steps:**
1. In `checkout-main` (v1.2.0 is an ancestor of HEAD, `version = "1.2.0"`), set `version = "1.3.0"` in `pyproject.toml` and commit it, as `/version` does for the next release.
2. Call `_latest_release()` -> `v1.2.0`; `git merge --no-edit v1.2.0` -> "Already up to date."; `_match_release_version("v1.2.0")`.

**Expected:** the checkout keeps its own commits, its version among them: it is past the release, and nothing in the file is a local edit.

**Actual:** `version = "1.2.0" (set from v1.2.0)`; `pyproject.toml` reads 1.2.0 again and `git status` shows ` M pyproject.toml`. The install then runs, and the chat bar shows 1.2.0, for code that is ahead of 1.2.0; the next commit of the whole worktree commits the downgrade.

**Tier that should catch it:** unit (`scripts/install_spec.py`): its examples change the version line without committing it, on a checkout at the release.
