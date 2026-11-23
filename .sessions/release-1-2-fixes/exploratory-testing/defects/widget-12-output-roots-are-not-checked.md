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
