---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Act On Files From File Menu

Map: [story-map.md](../../../.context/story-map.md#e-act-on-files-from-file-menu). Acceptance tests: `space/session/files/session_files_spec.py` (delete, every file in the session's folders), `space/session/validation/changed_artifact_spec.py` (validate a folder), `space/kanban/report_within_spec.py` (violations of a path), `space/session/practices/practice_session_output_spec.py` (add to a practice) for what the session answers; `harness/files_app/app/files/file-menu.spec.ts` for what only the page shows.

Requested (the person, 2026-11-26): "a right-click menu on the file viewer's folder/file tree, on files and folders": Delete, Validate, Display violations, and Add to practice ▸ with the session's practices. The menu already offers Add to chat context and Open in the file browser ([Open File In File Browser](../review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-file-in-file-browser)).

### Domain terms

- root: a file or a folder a practice's fidelity reads and writes under, kept in session.json relative to the folder the session works in (`FidelitySessionOutput.roots`). A practice holds many; only the folder it writes its documents under (`PracticeSessionOutput.choose_root`) must be a folder. The person (2026-11-26): "practice roots can take multiple folders and files; all folders and files get added to the whole of the practice at the point where added."
- the session's roots: the folder the session works in, and every root its practices write under (`SessionFiles.in_root`).

## Story: Delete File Or Folder From File Menu

#### Scenario: Delete a file after confirming

*Given* the Files app lists *board/.context/notes.md*, under the session's roots
*When* the Person right-clicks *notes.md* and chooses *Delete*
*Then* the page asks *Delete board/.context/notes.md? This cannot be undone.*
*When* the Person confirms
*Then* the session deletes *board/.context/notes.md* (`session.delete_file`)
*And* the file list is read again, without it

#### Scenario: Keep the file when the Person does not confirm

*Given* the page asks to confirm deleting *notes.md*
*When* the Person cancels
*Then* nothing is deleted and the menu closes

#### Scenario: Delete a folder and every file in it

*Given* the folder *board/drafts* holds two files
*When* the Person deletes *board/drafts* from its menu and confirms
*Then* the folder and both files are gone

#### Scenario Outline: Refuse what may not be deleted

*Given* the session works in *board*
*When* the Person deletes <path>
*Then* the session refuses it with <refusal>, and nothing is deleted
*And* the chat that opened the Files app is told *<path> was not deleted*, with the reason

| path | refusal |
|---|---|
| notes.md, outside the session's roots | PathOutsideRootsError |
| board, a root itself | RootDeleteRefused |
| .sessions/checkout-flow/session.json | SessionRecordWriteRefused |
| .sessions/checkout-flow, the folder holding session.json | SessionRecordWriteRefused |
| board/.git/config | VersionControlPathRefused |
| board/missing.md, not there | NamedPathNotFoundError |

## Story: Validate File Or Folder From File Menu

#### Scenario: Validate a file a fidelity declares

*Given* the session shows Stories' story map, which declares *.context/story-map.md*
*When* the Person right-clicks *story-map.md* and chooses *Validate*
*Then* the session runs the story map's graph rules on it (`session.check_changed_artifact`), saving a report and logging its validate line
*And* the page says which fidelities checked it

#### Scenario: Validate a folder

*Given* the folder *story_tests/checkout* holds scenario files the Stories scenarios fidelity declares
*When* the Person validates *story_tests/checkout*
*Then* each fidelity declaring a file in it validates the folder

#### Scenario: Say so when nothing declares the file

*Given* no fidelity the session shows declares *notes.md*
*When* the Person validates it
*Then* the page says no fidelity the session shows declares *notes.md*

## Story: Display Violations Of File Or Folder

#### Scenario: Show the rules a file breaks

*Given* the story map's latest report finds *verb-noun-format* broken at *.context/story-map.md* line 12
*When* the Person right-clicks *story-map.md* and chooses *Display violations*
*Then* the page shows *verb-noun-format* with the violation at line 12 (`ticket.violations_of`)
*When* the Person presses the violation
*Then* *story-map.md* opens at line 12

#### Scenario: Show the rules broken in a folder

*Given* violations in two files of *story_tests/checkout* and one in *.context/story-map.md*
*When* the Person displays the violations of *story_tests/checkout*
*Then* only the two files' violations show

#### Scenario: Say so when nothing is broken

*Given* no report finds a rule broken in *notes.md*
*When* the Person displays its violations
*Then* the page says no rule is broken in *notes.md*

## Story: Add File Or Folder To Practice

#### Scenario: Add a folder to a practice

*Given* the session's practices are Stories, DDD and Clean Engineering
*When* the Person right-clicks *story_tests/checkout* and points at *Add to practice*
*Then* a submenu lists Stories, DDD and Clean Engineering
*When* the Person chooses Stories
*Then* *story_tests/checkout* is a root of each Stories fidelity beside the roots it had (`practice-session-output.add_root`), kept in session.json
*And* the page says *story_tests/checkout added to Stories*

#### Scenario: Add a file to a practice

*Given* *c/vb/hr/e/story-1.md* is a file deep in the project
*When* the Person adds *story-1.md* to Stories
*Then* the file itself is a root of each Stories fidelity (`practice-session-output.add_root`)
*And* the file bar shows *story-1.md* at its top, under its own name (`PracticeSessionOutput.added_roots`)

#### Scenario: Show an added folder at the top of the file bar

*Given* the Person added *src/orders/refund* to Clean Engineering
*When* the file bar shows its files in their folders
*Then* *refund* is a folder at the top of the tree, holding the files under *src/orders/refund*

#### Scenario: Refuse a path outside the project

*When* a path outside the project is added to a practice
*Then* the session refuses it with OutputRootRefused, and session.json is unchanged
