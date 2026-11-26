# choose_root takes a file, a folder outside the project, C:/Windows and an empty path as a practice's or fidelity's root, and generate then tells the agent to write there

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers choosing a root.
- **Module and class:** `space/session/practice_session_output.py`, `PracticeSessionOutput.choose_root` and `FidelitySessionOutput.choose_root`.
- **Severity:** wrong result for a file as a root; question for a root outside the project (the supervisor may know it is allowed)

## Steps
Sandbox `repo`, session `main` (`drv\c10.json`):

    practice-session-output.choose_root {"session": "main", "practice": "stories", "path": "src/order.py"}
    practice-session-output.choose_root {"session": "main", "practice": "stories", "path": "../outside-root"}
    fidelity-session-output.choose_root {"session": "main", "practice": "stories", "fidelity": "story_map", "path": "src/order.py"}
    fidelity-session-output.choose_root {... "path": "C:/Windows"}, {... "path": "../.."}, {... "path": ""}
    generate.generate {"guidance": "stories-story-map"}

## Expected
A root is a folder under the session's root: a file is refused by name, and so is a folder outside the project, as validate refuses a path "not under the session's root". The fidelity's answer shows the root it now has.

## Actual
Every call answers `isError=False`. The practice's answer shows `"root": "src/order.py"` and `"root": "C:/dev/_et/widget/work/outside-root"`. The fidelity's answer shows only its formats, so the caller cannot see what root was kept; session.json then held `"story_map": {"root": "."}` for the empty path. generate's session section then says:

    Where each listed practice writes:
    - stories: C:/dev/_et/widget/work/repo/src/order.py

## Tier that should catch it
Unit (the session output's spec): no example gives a file or a path outside the project as a root.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). Every `choose_root` call answers with no error. The practice's answer shows `"root": "src/order.py"` and, for `../outside-root`, a root outside the repository. The fidelity's answers show only its formats; `session.json` then held `"stories": {"root": "src/order.py", "story_map": {"root": "."}}`. `generate.generate` then says `Where each listed practice writes: - stories: .../repo/src/order.py`.
- Cause, if you found it: `space/session/practice_session_output.py` `PracticeSessionOutput.choose_root` and `FidelitySessionOutput.choose_root` keep the path as given.
- Shares its cause with: widget-07, widget-11

## Also seen by
- Pixel, round 2, through the board's own route `POST /api/session/.sessions%2Fmain%2Fsession.json/choose-workpath`: `session.choose_workpath` takes `no/such/folder` (root becomes `repo/no/such/folder`, which is not there), `C:\Windows` and `..\outside` (root `C:/dev/_et/pixel/work/outside`, outside the project) with 200 and no word, the same unchecked root for the session's workpath.

## Status: fixed (2026-11-23)
- Fixed before this pass (`dc600d22a`): a file and an empty path are refused as a practice's or a fidelity's root with `OutputRootRefused`.
- Fixed now: a folder outside the project is refused too (`PracticeSessionOutput.root_named`): `../outside-root`, `../..`, `C:/Windows` or any whole path outside are refused by name, "... is outside the project <folder>", by `practice-session-output.choose_root`, `fidelity-session-output.choose_root` and `add_root`, and nothing is kept. A root may be in the session's own checkout (a ticket's worktree) or in the repository's own folder. The fidelity's answer now shows the roots it has (`FidelitySessionOutput.root_paths`, each a path from the project).
- Covered by: `space/session/practices/practice_session_output_spec.py`, "a practice's root in a session" / "that a person chooses as a folder beside the project, climbing out of it" and "as a whole path to a folder outside the project", and "a fidelity's root in a session" / "that a person chooses as a folder outside the project", "read back from its answer", "with a folder outside the project added beside it".
- `space/kanban/kanban_tools_spec.py` chose a random temporary folder as a stand-in for a ticket's worktree; that root is now refused, so its example reads a file by its whole path under a practice root inside the project.
- Not in this fix: Pixel's `session.choose_workpath` (an unchecked workpath, under "Also seen by") is a different operation and is left as reported.
