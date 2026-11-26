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

## Triage

- **Status:** question for the person
- **Severity:** question
- **Triaged by:** Hinge

No source settles it. `story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md` "Leave out what git ignores" covers only a folder git ignores under the folder the session works in (board/node_modules); `story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md` "Add a file to a practice" says only that the file itself becomes a root. The code (`SessionFiles._files_at`) returns a file root as it is and lists a folder root through `git ls-files --exclude-standard`. Behaviour unchanged. Recommendation: what a person added by name is listed whatever .gitignore says, so a folder root that git ignores as a whole is listed by a walk (as a root outside a repository is, leaving out node_modules and the other unread folders), while ignored files inside a root that is not itself ignored stay left out.

## Fix

None: a question, no behaviour changed.

Commit: COMMIT
