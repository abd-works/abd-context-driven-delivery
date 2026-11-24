# Question: may a fidelity have every format unchosen, and what does generate write then

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers this.
- **Module and class:** `space/session/practice_session_output.py`, `FidelitySessionOutput.choose_format`
- **Severity:** answered question

## Steps
Sandbox `repo`, session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`).

    fidelity-session-output.choose_format {"session":"main","practice":"stories","fidelity":"story_map","format":"markdown","is_chosen":false}
    fidelity-session-output.choose_format {... "format":"drawio","is_chosen":false}
    generate.generate {"guidance":"stories-story-map"}

## Expected
Not known: nothing read says which is meant.

## Actual
Both calls succeed and the fidelity answers `"chosen_formats": []`. generate still answers its 25,818 characters of rules with no word that the fidelity now writes in no format.

## Tier that should catch it
Once the person answers, a unit example that states the answer.

## Answer (2026-11-23)

A fidelity keeps at least one format chosen: leaving out its last chosen format is refused with a named error. Built in `space/session/practices/practice_session_output.py` (`FidelitySessionOutput.choose_formats`, which `choose_format` and `FidelityFormats.choose_from` go through in one change, raising *LastFormatLeftOut*); tested by `space/session/practices/practice_session_output_spec.py` "a fidelity's chosen formats in a session" with one format chosen, left out, and with only the diagram formats chosen, the diagram group left out; the board's e2e test `generate-fidelity-outputs.story.ui.spec.ts` "Keep the last format picked" replaces "Keep Run off with no format picked" (not run); scenario "Keep the last format picked" in `story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md`.
