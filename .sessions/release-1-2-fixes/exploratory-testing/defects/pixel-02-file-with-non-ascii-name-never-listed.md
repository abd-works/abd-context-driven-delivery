# A file whose name holds a letter outside ASCII (ü, é, 日本) is never listed in the Files app of a git project

- **Charter:** Round 1 - explore the Files app and the board's pages in a real browser as a person whose files change under the page
- **Tester:** Pixel
- **Story:** Review Generated Work In File Viewer > Open Files In Files App / Filter Files In Files App (the files of a session listed). No scenario covers a file name outside ASCII.
- **Module and class:** `space/session/session_files.py` `SessionFiles._tracked_under` (line 105): `git ls-files --cached --others --exclude-standard` is read line by line with git's default `core.quotepath`, so git answers `"src/\303\274n\303\257c\303\266d\303\251_\346\227\245\346\234\254.py"`, in quotes with octal escapes; `root / line` is then no file and `under_root` drops it at `if path.is_file()`. `space/repo/repo.py` `Branch.changed_files` (line 492) reads `git diff --name-only` and `git status --porcelain` the same way, and only strips the quotes, so the branch's changed files miss it too.
- **Severity:** wrong result (the file is in the session's work and on its branch, and the page shows neither it nor any word that a file was left out)

## Steps

Sandbox: `C:\dev\_et\pixel\work\repo`, branch and session `pixel-files`; Files server on 8902 (`C:\dev\_et\pixel\work\scripts\stack.py`), script `C:\dev\_et\pixel\work\scripts\t3.py`.

1. In `src/`, write `ünïcödé_日本.py` (text `uni = 1`) beside `with space.py`, `hash#tag.py`, `per%cent%20.py`, `a&b=c.py`; commit them on `pixel-files`.
2. Open `http://127.0.0.1:8902/?files=pixel-files&fidelity=stories-story-map,clean-engineering-code,stories-acceptance-tests&project=C:\dev\_et\pixel\work\repo`, press **All session files**, turn the code format filter off.
3. Or ask the listing itself: `POST http://127.0.0.1:8902/api/ticket/pixel-files/fidelity-files` with headers `x-cdd-files: 1`, `x-cdd-project: C:\dev\_et\pixel\work\repo` and body `{"fidelities":["clean-engineering-code"]}`.

## Expected

Every file under the session's root that git tracks or would track is listed (`SessionFiles.under_root`'s own description), `ünïcödé_日本.py` among them, as the files with a space, `#`, `%` and `&` in their names are.

## Actual

The list and the answer of step 3 hold `a&b=c.py`, `big.py`, `binary.py`, `cart.py`, `empty.py`, `hash#tag.py`, `latin1.py`, the long-named file, `per%cent%20.py`, `with space.py`, and no `ünïcödé_日本.py`. Nothing fails and nothing says a file was left out. `git -C repo ls-files src` shows the cause: its last line is `"src/\303\274n\303\257c\303\266d\303\251_\346\227\245\346\234\254.py"`.

A plain folder with no git is walked with `rglob` and is not affected; a name with a double quote, a backslash or a tab is quoted by git the same way.

## Tier that should catch it

heavy (a spec of `SessionFiles.under_root` and `Branch.changed_files` on a real git repository): the quoting is git's own, which `MockGit` in the unit tier does not reproduce. No spec seeds a file name outside ASCII. Reading with `-z`, or with `-c core.quotepath=false`, answers the names as they are.

## Also seen by

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own stack (`pstack.py`), the five files committed on branch `rivet-files`: step 3's `fidelity-files` call answers `a&b=c.py`, `cart.py`, `hash#tag.py`, `order.py`, `per%cent%20.py`, `with space.py` and no `ünïcödé_日本.py`; the page's list is the same. `git ls-files src` ends with `"src/\303\274n\303\257c\303\266d\303\251_\346\227\245\346\234\254.py"`.
- Cause, if you found it: `space/session/session_files.py` `SessionFiles._tracked_under`, line 105, as the report says: git's quoted line is joined to the root and dropped at `if path.is_file()`. I read `space/repo/repo.py` `Branch.changed_files` (lines 492 to 497) and it has the same reading; I did not run it apart from the listing.
- Shares its cause with: none
