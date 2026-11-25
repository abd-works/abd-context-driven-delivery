# Making a plain folder a repository copies every ignore line of the CDD checkout, so the first commit leaves out the person's own files (`_app.tsx`, `_config.yml`, `conf/`, `sandbox/`) and says nothing

**Charter:** Round 1 - installing CDD and making a repository as a person on their first day (card 55904a01e0e5)
**Tester:** Bolt

**How it was run:** `C:\dev\_et\bolt\mkrepo.py <folder>` calls `NewRepository(folder).make_from_folder()`, the one line `repo.make_repository` runs, then prints the branch, the log, `git ls-files`, and the status. Not run through the cdd server.

**Story:** `repo.make_repository` - "a git repository on main with a first commit of its files ... Its .gitignore first takes what the CDD checkout ignores" (`space/repo/repo.py`), "so that commit holds the folder's own files and not CDD's install or its sessions' working files" (`NewRepository.make_from_folder`). No scenario was found for a folder whose own files match CDD's ignore lines.

**Module and class:** `space/repo/new_repository.py` `NewRepository.write_ignores` (copies every line of `<CDD checkout>/.gitignore`, not only the lines for what CDD installs).

**Severity:** wrong result

**Steps:**
1. Make `C:\dev\_et\bolt\work\next-app` with `pages/_app.tsx`, `pages/index.tsx`, `conf/settings.yaml`, `sandbox/try.py`, `_layouts/default.html`, `_config.yml`, `count_all.py`.
2. `python mkrepo.py C:/dev/_et/bolt/work/next-app`
3. `git -C work/next-app ls-files` and `git -C work/next-app status --short --ignored`

**Expected:** the first commit holds the folder's own files; only what CDD writes into a project (`.claude/`, `.cursor/`, `.kilo/`, `.mcp.json`, session working files) is ignored.

**Actual:** the answer is `Created ... on main with a first commit. Its .gitignore took 126 lines from the CDD checkout's.` The commit holds `.gitignore`, `README.md`, and `pages/index.tsx` only. Ignored, and so never committed or pushed by any later save: `pages/_app.tsx`, `_config.yml`, `_layouts/`, `conf/`, `sandbox/`, `count_all.py`. The lines that do it are the CDD checkout's own housekeeping: `_*`, `conf/*`, `sandbox/`, `count_all.py`, `parse_board*.py`, `call_miro.py`, and others. `_*` alone hides Next.js `_app.tsx` / `_document.tsx`, Jekyll `_config.yml` / `_posts/`, and Python `_private.py` modules (only `__init__.py` and `__main__.py` are let back in). The status is clean afterwards, so nothing tells the person files were left out.

**Tier that should catch it:** heavy (a `new_repository` spec with real git): the existing examples make a repository from a folder holding only files CDD's lines do not match.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: The steps call `mkrepo.py`, which the report does not hold; I ran its one line, `NewRepository(Path(folder)).make_from_folder()` (a string for the folder fails with a TypeError). Answer: `took 126 lines from the CDD checkout's`. `git ls-files`: `.gitignore`, `README.md`, `pages/index.tsx`. Ignored: `_config.yml`, `_layouts/`, `conf/`, `count_all.py`, `pages/_app.tsx`, `sandbox/`.
- Cause, if you found it: `space/repo/new_repository.py` `NewRepository.write_ignores` copies every line of the CDD checkout's `.gitignore`.
- Shares its cause with: none
