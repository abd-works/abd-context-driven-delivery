# Question: an ignored file added to a practice is listed by All files, but an ignored folder added to a practice lists nothing

- **Charter:** C3
- **Tester:** Gizmo
- **Story:** List Every File In Session Folders - "Leave out what git ignores"; Add File Or Folder To Practice.
- **Module and class:** `space/session/files/session_files.py`, `SessionFiles._files_at` (a file root is returned as it is; a folder root goes through `git ls-files --exclude-standard`, which drops ignored files).
- **Severity:** question

## Steps

`.gitignore` holds `ignored/`. `s.own_practices["stories"].add_root("ignored")`, then `add_root("ignored/secret.md")`, then `s.all_files()` (driver `scripts/roots.py`).

## Expected

One rule for both: either a root the person added is listed whatever .gitignore says (they chose it), or what git ignores is always left out.

## Actual

After adding the folder `ignored`, All files lists nothing from it - the person added a folder and sees no sign of it (the file bar shows the folder only if it has an entry). After adding the file `ignored/secret.md`, it is listed. Which is intended?
